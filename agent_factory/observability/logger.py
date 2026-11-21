"""
Structured JSON Lines Logging for Agent Runtimes.
Provides log correlation with W3C distributed tracing context (trace_id, span_id).
"""

import sys
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

from agent_factory.observability.tracer import TraceContext


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogRecord(BaseModel):
    timestamp_iso: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    level: LogLevel
    message: str
    service_name: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    agent_id: Optional[str] = None
    component: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None


class StructuredLogger:
    """JSON Lines structured logger correlated with distributed tracing spans."""

    def __init__(
        self,
        service_name: str = "agent-factory-runtime",
        log_file: Optional[Union[str, Path]] = None,
        min_level: LogLevel = LogLevel.INFO,
        write_stdout: bool = True,
    ):
        self.service_name = service_name
        self.log_file = Path(log_file) if log_file else None
        self.min_level = min_level
        self.write_stdout = write_stdout
        self._bound_context: Dict[str, Any] = {}
        self.history: list[StructuredLogRecord] = []

        self._level_order = {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
            LogLevel.CRITICAL: 50,
        }

    def bind(self, **kwargs) -> "StructuredLogger":
        """Returns a cloned logger with bound context attributes."""
        clone = StructuredLogger(
            service_name=self.service_name,
            log_file=self.log_file,
            min_level=self.min_level,
            write_stdout=self.write_stdout,
        )
        clone._bound_context = {**self._bound_context, **kwargs}
        clone.history = self.history
        return clone

    def bind_trace(self, context: TraceContext) -> "StructuredLogger":
        """Binds W3C trace context to logger."""
        return self.bind(
            trace_id=context.trace_id,
            span_id=context.span_id,
            parent_span_id=context.parent_span_id,
        )

    def _should_log(self, level: LogLevel) -> bool:
        return self._level_order.get(level, 20) >= self._level_order.get(self.min_level, 20)

    def log(
        self,
        level: LogLevel,
        message: str,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        component: Optional[str] = None,
        error: Optional[Union[Exception, Dict[str, Any]]] = None,
        **extra,
    ) -> StructuredLogRecord:
        """Emits a structured JSON record."""
        if not self._should_log(level):
            return None

        # Resolve merged context
        resolved_trace_id = trace_id or self._bound_context.get("trace_id")
        resolved_span_id = span_id or self._bound_context.get("span_id")
        resolved_parent_span_id = self._bound_context.get("parent_span_id")
        resolved_agent_id = agent_id or self._bound_context.get("agent_id")
        resolved_component = component or self._bound_context.get("component")

        merged_attrs = {k: v for k, v in self._bound_context.items() if k not in (
            "trace_id", "span_id", "parent_span_id", "agent_id", "component"
        )}
        merged_attrs.update(extra)

        err_payload = None
        if error:
            if isinstance(error, Exception):
                err_payload = {
                    "type": type(error).__name__,
                    "message": str(error),
                }
            elif isinstance(error, dict):
                err_payload = error
            else:
                err_payload = {"message": str(error)}

        record = StructuredLogRecord(
            level=level,
            message=message,
            service_name=self.service_name,
            trace_id=resolved_trace_id,
            span_id=resolved_span_id,
            parent_span_id=resolved_parent_span_id,
            agent_id=resolved_agent_id,
            component=resolved_component,
            attributes=merged_attrs,
            error=err_payload,
        )

        self.history.append(record)
        json_line = record.model_dump_json()

        if self.write_stdout:
            sys.stdout.write(json_line + "\n")
            sys.stdout.flush()

        if self.log_file:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json_line + "\n")
            except Exception:
                pass

        return record

    def debug(self, message: str, **kwargs) -> Optional[StructuredLogRecord]:
        return self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> Optional[StructuredLogRecord]:
        return self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> Optional[StructuredLogRecord]:
        return self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> Optional[StructuredLogRecord]:
        return self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> Optional[StructuredLogRecord]:
        return self.log(LogLevel.CRITICAL, message, **kwargs)
