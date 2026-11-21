"""
Dynamic Auto-Scaling Infrastructure & Concurrency Governance.
Manages workload spikes, queue backpressure, worker pool scaling, and circuit breaker protection.
Enforces system reliability under variable demand while upholding the $0.00 spend ceiling.
"""

import time
import queue
import threading
from concurrent.futures import Future
from enum import Enum
from typing import Callable, Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Normal operation: traffic flows freely
    OPEN = "OPEN"            # Tripped: traffic rejected to prevent cascading failure
    HALF_OPEN = "HALF_OPEN"  # Testing recovery with canary executions


class WorkerPoolConfig(BaseModel):
    min_workers: int = 1
    max_workers: int = 16
    scale_up_threshold_queue_depth: int = 3
    worker_increment: int = 2
    scale_down_idle_seconds: float = 5.0
    max_queue_depth: int = 100
    circuit_breaker_failure_rate: float = 0.25  # 25% failure trips breaker
    circuit_breaker_window_size: int = 20
    circuit_breaker_recovery_seconds: float = 3.0


class CircuitBreakerError(Exception):
    """Raised when request is rejected due to tripped circuit breaker."""
    pass


class QueueBackpressureError(Exception):
    """Raised when queue exceeds maximum capacity under spike."""
    pass


class CircuitBreaker:
    """
    Sliding-window circuit breaker protecting downstream services and agents from cascading failures.
    """

    def __init__(
        self,
        failure_rate_threshold: float = 0.25,
        window_size: int = 20,
        recovery_seconds: float = 3.0,
        consecutive_successes_to_close: int = 3,
    ):
        self.failure_rate_threshold = failure_rate_threshold
        self.window_size = window_size
        self.recovery_seconds = recovery_seconds
        self.consecutive_successes_to_close = consecutive_successes_to_close

        self.state: CircuitState = CircuitState.CLOSED
        self._lock = threading.Lock()
        self._history: List[bool] = []  # True = success, False = failure
        self._last_state_change: float = time.perf_counter()
        self._half_open_successes: int = 0

    def can_execute(self) -> bool:
        """Determines if execution is permitted based on circuit state."""
        with self._lock:
            now = time.perf_counter()
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                if now - self._last_state_change >= self.recovery_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self._last_state_change = now
                    self._half_open_successes = 0
                    return True
                return False

            if self.state == CircuitState.HALF_OPEN:
                # In half-open, allow canary probes through
                return True

            return False

    def record_success(self) -> None:
        """Records successful execution."""
        with self._lock:
            self._history.append(True)
            if len(self._history) > self.window_size:
                self._history.pop(0)

            if self.state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.consecutive_successes_to_close:
                    self.state = CircuitState.CLOSED
                    self._last_state_change = time.perf_counter()
                    self._history.clear()

    def record_failure(self, err: Optional[str] = None) -> None:
        """Records failed execution and evaluates trip threshold."""
        with self._lock:
            self._history.append(False)
            if len(self._history) > self.window_size:
                self._history.pop(0)

            if self.state == CircuitState.HALF_OPEN:
                # Immediate trip back to open on failure during recovery
                self.state = CircuitState.OPEN
                self._last_state_change = time.perf_counter()
                return

            if self.state == CircuitState.CLOSED and len(self._history) >= 5:
                fail_count = sum(1 for res in self._history if not res)
                current_fail_rate = fail_count / len(self._history)
                if current_fail_rate >= self.failure_rate_threshold:
                    self.state = CircuitState.OPEN
                    self._last_state_change = time.perf_counter()

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            total = len(self._history)
            fails = sum(1 for r in self._history if not r)
            fail_rate = (fails / total) if total > 0 else 0.0
            return {
                "state": self.state.value,
                "history_length": total,
                "fail_rate": round(fail_rate, 3),
                "is_healthy": (self.state == CircuitState.CLOSED),
            }


class AutoscalingWorkerPool:
    """
    Dynamic worker pool with automated scaling on queue depth, backpressure limits,
    and integrated circuit breaker protection.
    """

    def __init__(self, config: Optional[WorkerPoolConfig] = None):
        self.config = config or WorkerPoolConfig()
        self.circuit_breaker = CircuitBreaker(
            failure_rate_threshold=self.config.circuit_breaker_failure_rate,
            window_size=self.config.circuit_breaker_window_size,
            recovery_seconds=self.config.circuit_breaker_recovery_seconds,
        )

        self._task_queue: queue.Queue = queue.Queue(maxsize=self.config.max_queue_depth)
        self._workers: List[threading.Thread] = []
        self._current_worker_count = 0
        self._active_task_count = 0
        self._total_completed = 0
        self._total_failed = 0
        self._lock = threading.Lock()
        self._running = True

        # Initial baseline worker provision
        self._ensure_workers(self.config.min_workers)

    def _worker_loop(self) -> None:
        """Worker thread lifecycle with idle scale-down awareness."""
        while self._running:
            try:
                task_item = self._task_queue.get(timeout=self.config.scale_down_idle_seconds)
            except queue.Empty:
                with self._lock:
                    # Scale down if above min_workers and queue is empty
                    if self._current_worker_count > self.config.min_workers and self._task_queue.empty():
                        self._current_worker_count -= 1
                        return
                continue

            if task_item is None:
                # Sentinel to terminate
                return

            func, args, kwargs, future = task_item
            with self._lock:
                self._active_task_count += 1

            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                future.set_result(result)
                self.circuit_breaker.record_success()
                with self._lock:
                    self._total_completed += 1
            except Exception as e:
                future.set_exception(e)
                self.circuit_breaker.record_failure(str(e))
                with self._lock:
                    self._total_failed += 1
            finally:
                with self._lock:
                    self._active_task_count -= 1
                self._task_queue.task_done()

    def _ensure_workers(self, target_count: int) -> None:
        """Spawns additional worker threads up to bounded maximum."""
        target_count = min(target_count, self.config.max_workers)
        with self._lock:
            while self._current_worker_count < target_count:
                self._current_worker_count += 1
                t = threading.Thread(target=self._worker_loop, daemon=True)
                t.start()
                self._workers.append(t)

    def _check_and_autoscale(self) -> None:
        """Evaluates queue pressure and triggers dynamic scale-up if needed."""
        pending = self._task_queue.qsize()
        with self._lock:
            current_workers = self._current_worker_count

        if pending >= self.config.scale_up_threshold_queue_depth and current_workers < self.config.max_workers:
            needed = min(
                self.config.max_workers,
                current_workers + self.config.worker_increment
            )
            self._ensure_workers(needed)

    def submit(self, fn: Callable[..., Any], *args, **kwargs) -> Future:
        """
        Submits work to pool.
        Enforces Circuit Breaker check and Queue Backpressure limit.
        """
        if not self.circuit_breaker.can_execute():
            raise CircuitBreakerError(
                f"CIRCUIT_BREAKER_OPEN: Service degraded. Rejecting execution to prevent cascading failure."
            )

        if self._task_queue.qsize() >= self.config.max_queue_depth:
            raise QueueBackpressureError(
                f"QUEUE_BACKPRESSURE_LIMIT: Capacity exceeded ({self._task_queue.qsize()}/{self.config.max_queue_depth})."
            )

        future: Future = Future()
        try:
            self._task_queue.put_nowait((fn, args, kwargs, future))
        except queue.Full:
            raise QueueBackpressureError("QUEUE_FULL: Unable to enqueue task.")

        self._check_and_autoscale()
        return future

    def get_status(self) -> Dict[str, Any]:
        """Provides real-time observability metrics for autoscaling and load."""
        with self._lock:
            pending = self._task_queue.qsize()
            workers = self._current_worker_count
            active = self._active_task_count
            completed = self._total_completed
            failed = self._total_failed

        utilization = (active / workers) if workers > 0 else 0.0
        cb_metrics = self.circuit_breaker.get_metrics()

        return {
            "current_workers": workers,
            "min_workers": self.config.min_workers,
            "max_workers": self.config.max_workers,
            "active_tasks": active,
            "queued_tasks": pending,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "utilization_pct": round(utilization * 100, 1),
            "circuit_breaker": cb_metrics,
        }

    def simulate_workload_spike(
        self,
        num_tasks: int = 15,
        task_duration_seconds: float = 0.05,
        fail_fraction: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Stress test simulation: injects a burst of tasks and measures auto-scaling behavior.
        """
        initial_status = self.get_status()
        futures = []

        def sample_work(idx: int):
            time.sleep(task_duration_seconds)
            if fail_fraction > 0 and (idx % int(1.0 / fail_fraction) == 0):
                raise RuntimeError(f"Simulated fault in task {idx}")
            return f"result_{idx}"

        peak_workers = initial_status["current_workers"]
        for i in range(num_tasks):
            try:
                fut = self.submit(sample_work, i)
                futures.append(fut)
                status_now = self.get_status()
                if status_now["current_workers"] > peak_workers:
                    peak_workers = status_now["current_workers"]
            except Exception:
                pass

        # Wait for submitted tasks
        successes = 0
        failures = 0
        for fut in futures:
            try:
                fut.result(timeout=10.0)
                successes += 1
            except Exception:
                failures += 1

        final_status = self.get_status()
        return {
            "tasks_injected": num_tasks,
            "tasks_succeeded": successes,
            "tasks_failed": failures,
            "initial_workers": initial_status["current_workers"],
            "peak_workers": peak_workers,
            "scaled_up": (peak_workers > initial_status["current_workers"]),
            "circuit_breaker_status": final_status["circuit_breaker"],
        }

    def shutdown(self, wait: bool = True) -> None:
        """Gracefully drains queue and stops workers."""
        self._running = False
        # Wake up sleeping workers
        with self._lock:
            for _ in range(self._current_worker_count + 5):
                try:
                    self._task_queue.put_nowait(None)
                except Exception:
                    pass
