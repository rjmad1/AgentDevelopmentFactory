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

__all__ = [
    "CircuitState",
    "WorkerPoolConfig",
    "CircuitBreakerError",
    "QueueBackpressureError",
    "CircuitBreaker",
    "AutoscalingWorkerPool",
]
