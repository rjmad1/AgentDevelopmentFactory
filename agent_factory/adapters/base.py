"""
Abstract Base Classes for Model Providers and Execution Harness Adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ModelAdapter(ABC):
    """Abstract interface for LLM inference providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> str:
        pass

    @abstractmethod
    def check_health(self) -> bool:
        pass


class HarnessAdapter(ABC):
    """Abstract interface for external engineering and execution harnesses."""

    @abstractmethod
    def run_bounded_task(self, command: str, workdir: str, timeout_seconds: int = 60) -> Dict[str, Any]:
        pass
