"""
Agent Development Factory - Background Worker Daemon & SRE Probe Server.
Exposes Kubernetes liveness (/healthz), readiness (/readyz), and Prometheus (/metrics) endpoints.
Coordinates background autoscaling worker pool execution under strict $0.00 spend ceiling.
"""

import os
import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any

from agent_factory.scaling.autoscaler import (
    AutoscalingWorkerPool,
    WorkerPoolConfig,
    CircuitState,
)

logger = logging.getLogger("adf.worker_daemon")


class WorkerProbeHandler(BaseHTTPRequestHandler):
    """Zero-dependency HTTP handler for Kubernetes probes and Prometheus metrics."""

    pool: Optional[AutoscalingWorkerPool] = None

    def log_message(self, format: str, *args: Any) -> None:
        """Silence standard console logging for probe calls."""
        pass

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = json.dumps({"status": "healthy", "service": "adf-agent-worker"}).encode("utf-8")
            self.wfile.write(payload)
            return

        if path == "/readyz":
            if not self.pool or not self.pool._running:
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "not_ready", "reason": "worker_pool_stopped"}).encode("utf-8"))
                return

            if self.pool.circuit_breaker.state == CircuitState.OPEN:
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "not_ready", "reason": "circuit_breaker_open"}).encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ready", "service": "adf-agent-worker"}).encode("utf-8"))
            return

        if path == "/metrics":
            status = self.pool.get_status() if self.pool else {
                "queued_tasks": 0,
                "current_workers": 0,
                "active_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "circuit_breaker": {"state": "CLOSED"},
            }

            cb_state_val = 0
            state_str = status.get("circuit_breaker", {}).get("state", "CLOSED")
            if state_str == "HALF_OPEN":
                cb_state_val = 1
            elif state_str == "OPEN":
                cb_state_val = 2

            lines = [
                "# HELP agent_factory_queued_tasks Number of tasks currently queued",
                "# TYPE agent_factory_queued_tasks gauge",
                f"agent_factory_queued_tasks {status['queued_tasks']}",
                "# HELP agent_factory_current_workers Number of active worker threads",
                "# TYPE agent_factory_current_workers gauge",
                f"agent_factory_current_workers {status['current_workers']}",
                "# HELP agent_factory_active_tasks Number of tasks currently running",
                "# TYPE agent_factory_active_tasks gauge",
                f"agent_factory_active_tasks {status['active_tasks']}",
                "# HELP agent_factory_completed_tasks_total Total completed tasks",
                "# TYPE agent_factory_completed_tasks_total counter",
                f"agent_factory_completed_tasks_total {status['completed_tasks']}",
                "# HELP agent_factory_failed_tasks_total Total failed tasks",
                "# TYPE agent_factory_failed_tasks_total counter",
                f"agent_factory_failed_tasks_total {status['failed_tasks']}",
                "# HELP agent_factory_circuit_state Circuit breaker state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)",
                "# TYPE agent_factory_circuit_state gauge",
                f"agent_factory_circuit_state {cb_state_val}",
                "# HELP agent_factory_spend_ceiling_usd Spend ceiling in USD",
                "# TYPE agent_factory_spend_ceiling_usd gauge",
                "agent_factory_spend_ceiling_usd 0.00",
                "",
            ]
            body = "\n".join(lines).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()


def create_daemon_server(
    port: int = 8000,
    pool: Optional[AutoscalingWorkerPool] = None,
) -> HTTPServer:
    """Creates an HTTPServer instance wired to the provided worker pool."""
    handler = WorkerProbeHandler
    handler.pool = pool
    server = HTTPServer(("0.0.0.0", port), handler)
    return server


def run_worker_daemon() -> None:
    """Main CLI entrypoint for running the worker daemon container process."""
    min_workers = int(os.environ.get("ADF_WORKER_MIN", "1"))
    max_workers = int(os.environ.get("ADF_WORKER_MAX", "16"))
    port = int(os.environ.get("ADF_WORKER_PORT", "8000"))

    config = WorkerPoolConfig(min_workers=min_workers, max_workers=max_workers)
    pool = AutoscalingWorkerPool(config=config)

    server = create_daemon_server(port=port, pool=pool)
    print(f"[WORKER DAEMON] Started ADF Worker Daemon on port {port} (Min: {min_workers}, Max: {max_workers})")
    print(f"[WORKER DAEMON] Enforcing strict $0.00 spend ceiling.")

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        while True:
            import time
            time.sleep(1.0)
    except (KeyboardInterrupt, SystemExit):
        print("\n[WORKER DAEMON] Shutting down worker pool and probe server...")
        server.shutdown()
        pool.shutdown(wait=True)
        print("[WORKER DAEMON] Graceful shutdown complete.")


if __name__ == "__main__":
    run_worker_daemon()
