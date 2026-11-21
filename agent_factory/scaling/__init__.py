"""
Auto-scaling infrastructure and concurrency governance package.
"""

from agent_factory.scaling.autoscaler import (
    CircuitState,
    WorkerPoolConfig,
    CircuitBreakerError,
    QueueBackpressureError,
    CircuitBreaker,
    AutoscalingWorkerPool,
)
from agent_factory.scaling.worker_daemon import (
    WorkerProbeHandler,
    create_daemon_server,
    run_worker_daemon,
)

__all__ = [
    "CircuitState",
    "WorkerPoolConfig",
    "CircuitBreakerError",
    "QueueBackpressureError",
    "CircuitBreaker",
    "AutoscalingWorkerPool",
    "WorkerProbeHandler",
    "create_daemon_server",
    "run_worker_daemon",
]
