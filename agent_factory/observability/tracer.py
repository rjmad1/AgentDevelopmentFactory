"""
W3C TraceContext & OpenTelemetry-Compatible Distributed Tracing Engine.
Enables hierarchical span tracing and full causal observability across agent reasoning chains.
"""

import os
import secrets
import time
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class SpanKind(str, Enum):
    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


class SpanStatus(str, Enum):
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


class TraceContext(BaseModel):
    trace_id: str = Field(default_factory=lambda: secrets.token_hex(16))  # 128-bit hex
    span_id: str = Field(default_factory=lambda: secrets.token_hex(8))    # 64-bit hex
    parent_span_id: Optional[str] = None
    trace_flags: str = "01"  # Sampled

    def to_traceparent(self) -> str:
        """Serializes to W3C TraceContext traceparent standard header."""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags}"

    @classmethod
    def from_traceparent(cls, header: str) -> "TraceContext":
        """Parses a W3C TraceContext traceparent header."""
        parts = header.strip().split("-")
        if len(parts) >= 4 and parts[0] == "00":
            return cls(
                trace_id=parts[1],
                span_id=parts[2],
                trace_flags=parts[3],
            )
        return cls()

    def create_child(self) -> "TraceContext":
        """Spawns child context linked to current span as parent."""
        return TraceContext(
            trace_id=self.trace_id,
            span_id=secrets.token_hex(8),
            parent_span_id=self.span_id,
            trace_flags=self.trace_flags,
        )


class SpanEvent(BaseModel):
    name: str
    timestamp_iso: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    attributes: Dict[str, Any] = Field(default_factory=dict)


class SpanRecord(BaseModel):
    name: str
    service_name: str
    kind: SpanKind = SpanKind.INTERNAL
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time_iso: str
    end_time_iso: Optional[str] = None
    duration_ms: float = 0.0
    status: SpanStatus = SpanStatus.UNSET
    error_message: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    events: List[SpanEvent] = Field(default_factory=list)


class Span:
    """Context manager representing an active operational span in the reasoning chain."""

    def __init__(
        self,
        tracer: "Tracer",
        name: str,
        context: TraceContext,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        self.tracer = tracer
        self.name = name
        self.context = context
        self.kind = kind
        self.attributes = dict(attributes or {})
        self.events: List[SpanEvent] = []
        self.status = SpanStatus.UNSET
        self.error_message: Optional[str] = None

        self.start_wall_time = time.perf_counter()
        self.start_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.end_time_iso: Optional[str] = None
        self.duration_ms = 0.0

    def set_attribute(self, key: str, value: Any) -> "Span":
        self.attributes[key] = value
        return self

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> "Span":
        self.events.append(SpanEvent(name=name, attributes=attributes or {}))
        return self

    def set_status(self, status: SpanStatus, error_message: Optional[str] = None) -> "Span":
        self.status = status
        if error_message:
            self.error_message = error_message
        return self

    def record_error(self, err: Union[Exception, str]) -> "Span":
        msg = str(err)
        self.status = SpanStatus.ERROR
        self.error_message = msg
        self.add_event("exception", {"exception.message": msg, "exception.type": type(err).__name__})
        return self

    def end(self) -> SpanRecord:
        elapsed = (time.perf_counter() - self.start_wall_time) * 1000.0
        self.duration_ms = round(elapsed, 2)
        self.end_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if self.status == SpanStatus.UNSET:
            self.status = SpanStatus.OK

        record = SpanRecord(
            name=self.name,
            service_name=self.tracer.service_name,
            kind=self.kind,
            trace_id=self.context.trace_id,
            span_id=self.context.span_id,
            parent_span_id=self.context.parent_span_id,
            start_time_iso=self.start_time_iso,
            end_time_iso=self.end_time_iso,
            duration_ms=self.duration_ms,
            status=self.status,
            error_message=self.error_message,
            attributes=self.attributes,
            events=self.events,
        )
        self.tracer._record_completed_span(record)
        return record

    def __enter__(self) -> "Span":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.record_error(exc_val)
        self.end()


class Tracer:
    """Manages active spans and exports OpenTelemetry / Jaeger traces."""

    def __init__(
        self,
        service_name: str = "agent-factory-runtime",
        trace_storage_file: Optional[Path] = None,
    ):
        self.service_name = service_name
        self.trace_storage_file = trace_storage_file
        self.completed_spans: List[SpanRecord] = []

    def start_span(
        self,
        name: str,
        parent_context: Optional[TraceContext] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """Starts a new span. Spawns child context if parent_context is provided, or creates root context."""
        if parent_context:
            context = parent_context.create_child()
        else:
            context = TraceContext()

        return Span(
            tracer=self,
            name=name,
            context=context,
            kind=kind,
            attributes=attributes,
        )

    def _record_completed_span(self, record: SpanRecord) -> None:
        self.completed_spans.append(record)

        if self.trace_storage_file:
            try:
                p = Path(self.trace_storage_file)
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, "a", encoding="utf-8") as f:
                    f.write(record.model_dump_json() + "\n")
            except Exception:
                pass

    def get_spans_for_trace(self, trace_id: str) -> List[SpanRecord]:
        return [s for s in self.completed_spans if s.trace_id == trace_id]

    def export_jaeger_json(self, trace_id: str) -> Dict[str, Any]:
        """Formats spans into Jaeger/OpenTelemetry compatible hierarchical payload."""
        spans = self.get_spans_for_trace(trace_id)
        return {
            "data": [
                {
                    "traceID": trace_id,
                    "spans": [
                        {
                            "traceID": s.trace_id,
                            "spanID": s.span_id,
                            "operationName": s.name,
                            "references": (
                                [{"refType": "CHILD_OF", "traceID": s.trace_id, "spanID": s.parent_span_id}]
                                if s.parent_span_id
                                else []
                            ),
                            "startTime": s.start_time_iso,
                            "duration": int(s.duration_ms * 1000),  # microseconds
                            "tags": [{"key": k, "type": "string", "value": str(v)} for k, v in s.attributes.items()],
                            "logs": [{"timestamp": e.timestamp_iso, "fields": [{"key": "event", "value": e.name}]} for e in s.events],
                            "process": {"serviceName": s.service_name},
                        }
                        for s in spans
                    ],
                }
            ]
        }
