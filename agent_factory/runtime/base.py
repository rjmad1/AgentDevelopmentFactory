"""
Abstract Base Class for Agent Execution Runtimes.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel


class ExecutionLimits(BaseModel):
    max_wall_time_seconds: int = 60
    max_steps: int = 20
    paid_spend_ceiling: float = 0.0


class ExecutionResult(BaseModel):
    success: bool
    exit_code: int
    duration_ms: float
    stdout: str
    stderr: str
    artifacts_created: Dict[str, str] = {}
    error_message: str = ""


class AgentRuntime(ABC):
    """Abstract interface defining agent execution boundaries."""

    @abstractmethod
    def execute(
        self,
        entrypoint_script: Path,
        args: list,
        limits: ExecutionLimits,
        workdir: Path,
    ) -> ExecutionResult:
        pass
