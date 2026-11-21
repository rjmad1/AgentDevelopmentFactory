"""
Tests for Distributed Tracing, Structured Logging, and Auto-Scaling Concurrency Governance.
Verifies W3C TraceContext conformance, JSON Lines telemetry correlation,
dynamic worker pool autoscaling under spike bursts, and circuit breaker protection.
"""

import time
import json
import pytest
from pathlib import Path

from agent_factory.observability import (
    SpanKind,
    SpanStatus,
    TraceContext,
    Span,
    Tracer,
    LogLevel,
    StructuredLogger,
)
from agent_factory.scaling import (
    CircuitState,
    WorkerPoolConfig,
    CircuitBreakerError,
    QueueBackpressureError,
    CircuitBreaker,
    AutoscalingWorkerPool,
)
from agent_factory.specs.schema import (
    UniversalAgentSpec,
    LimitsSpec,
    PolicySpec,
    AcceptanceSpec,
    EffectLevel,
    RiskTier,
    InputParameter,
    OutputParameter,
)
from agent_factory.guardrails.reasoning_engine import ConstrainedReasoningEngine


def _create_minimal_spec(agent_id: str = "observability-agent-01") -> UniversalAgentSpec:
    return UniversalAgentSpec(
        schema_version=1,
        agent_id=agent_id,
        version="1.0.0",
        owner="ObservabilityLead",
        purpose="Analyze local non-sensitive CSV datasets for anomalies and generate audit reports.",
        risk_tier=RiskTier.T0,
        inputs={
            "task_data": InputParameter(type="string", description="Workload payload", required=True)
        },
        outputs={
            "summary": OutputParameter(type="file", format="json", path="artifacts/summary.json")
        },
        policy=PolicySpec(
            mode="draft_only",
            permitted_tools=["file_reader"],
            permitted_effects=[EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT],
        ),
        limits=LimitsSpec(max_steps=10, max_tokens=1000, max_wall_time_seconds=30, paid_spend_ceiling=0.0),
        acceptance=AcceptanceSpec(suite="evals/standard", minimum_efficacy=0.95, minimum_safety=1.00),
    )


def test_w3c_trace_context_propagation():
    """Verify W3C TraceContext generation, parsing, and child context linkage."""
    ctx = TraceContext()
    assert len(ctx.trace_id) == 32
    assert len(ctx.span_id) == 16
    assert ctx.parent_span_id is None

    # Serialization to W3C traceparent standard
    traceparent = ctx.to_traceparent()
    assert traceparent.startswith(f"00-{ctx.trace_id}-{ctx.span_id}-")

    # Parsing from traceparent
    parsed = TraceContext.from_traceparent(traceparent)
    assert parsed.trace_id == ctx.trace_id
    assert parsed.span_id == ctx.span_id

    # Child context propagation
    child = ctx.create_child()
    assert child.trace_id == ctx.trace_id
    assert child.span_id != ctx.span_id
    assert child.parent_span_id == ctx.span_id
    assert child.to_traceparent().startswith(f"00-{ctx.trace_id}-{child.span_id}-")


def test_tracer_hierarchical_spans_and_jaeger_export(tmp_path):
    """Verify tracer records parent-child span hierarchy and exports Jaeger-compatible JSON."""
    trace_file = tmp_path / "spans.jsonl"
    tracer = Tracer(service_name="test-reasoning-service", trace_storage_file=trace_file)

    with tracer.start_span("root_reasoning_pipeline") as root_span:
        root_span.set_attribute("pipeline.version", "1.0.0")
        root_span.add_event("pipeline_started")

        # Child 1: Screening
        with tracer.start_span("input_screening", parent_context=root_span.context) as child1:
            child1.set_attribute("tokens", 50)
            child1.add_event("prompt_cleared")

        # Child 2: Execution with simulated failure capture
        with tracer.start_span("tool_exec", parent_context=root_span.context) as child2:
            child2.record_error("Simulated tool timeout")

    # Assert completed spans recorded
    spans = tracer.get_spans_for_trace(root_span.context.trace_id)
    assert len(spans) == 3

    # Assert storage file was populated with JSON Lines
    assert trace_file.exists()
    lines = [json.loads(line) for line in trace_file.read_text(encoding="utf-8").strip().split("\n")]
    assert len(lines) == 3

    # Verify Jaeger export structure
    jaeger_payload = tracer.export_jaeger_json(root_span.context.trace_id)
    assert "data" in jaeger_payload
    trace_data = jaeger_payload["data"][0]
    assert trace_data["traceID"] == root_span.context.trace_id
    assert len(trace_data["spans"]) == 3

    # Check parentage references in export
    child_records = [s for s in trace_data["spans"] if s["operationName"] in ("input_screening", "tool_exec")]
    for c in child_records:
        assert len(c["references"]) == 1
        assert c["references"][0]["refType"] == "CHILD_OF"
        assert c["references"][0]["spanID"] == root_span.context.span_id


def test_structured_logger_correlation_and_levels(tmp_path):
    """Verify structured logger formats JSON Lines with correlated trace context."""
    log_file = tmp_path / "agent.jsonl"
    logger = StructuredLogger(
        service_name="agent-runner",
        log_file=log_file,
        min_level=LogLevel.DEBUG,
        write_stdout=False,
    )

    ctx = TraceContext()
    bound_logger = logger.bind_trace(ctx).bind(agent_id="agent-xyz")

    bound_logger.info("Starting agent plan execution", goal="generate summary")
    bound_logger.warning("Resource nearing threshold", current_tokens=850)
    bound_logger.error("Execution anomaly detected", error=ValueError("Invalid artifact path"))

    assert len(bound_logger.history) == 3
    assert log_file.exists()

    with open(log_file, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    assert len(records) == 3
    for r in records:
        assert r["trace_id"] == ctx.trace_id
        assert r["span_id"] == ctx.span_id
        assert r["agent_id"] == "agent-xyz"

    assert records[0]["level"] == "INFO"
    assert records[0]["message"] == "Starting agent plan execution"
    assert records[2]["level"] == "ERROR"
    assert records[2]["error"]["type"] == "ValueError"


def test_circuit_breaker_lifecycle():
    """Verify circuit breaker transitions: CLOSED -> OPEN on failures -> HALF_OPEN -> CLOSED on recovery."""
    cb = CircuitBreaker(
        failure_rate_threshold=0.25,
        window_size=10,
        recovery_seconds=0.1,  # Fast for test
        consecutive_successes_to_close=2,
    )

    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # 4 successes, 1 failure (20% failure, below 25%)
    for _ in range(4):
        cb.record_success()
    cb.record_failure("Err 1")
    assert cb.state == CircuitState.CLOSED

    # Add another failure (2 / 6 = 33.3%, above 25% threshold)
    cb.record_failure("Err 2")
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Wait for recovery timeout
    time.sleep(0.12)
    # Now can_execute should transition to HALF_OPEN
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Two consecutive successes in half-open should close the breaker
    cb.record_success()
    assert cb.state == CircuitState.HALF_OPEN
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True


def test_autoscaling_worker_pool_under_workload_spike():
    """Verify autoscaling pool scales up workers dynamically under a burst of tasks."""
    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=8,
        scale_up_threshold_queue_depth=2,
        worker_increment=2,
        scale_down_idle_seconds=0.2,
        max_queue_depth=50,
    )
    pool = AutoscalingWorkerPool(config=config)

    initial_status = pool.get_status()
    assert initial_status["current_workers"] == 1
    assert initial_status["min_workers"] == 1

    # Inject spike burst
    spike_result = pool.simulate_workload_spike(
        num_tasks=12,
        task_duration_seconds=0.04,
        fail_fraction=0.0,
    )

    assert spike_result["tasks_injected"] == 12
    assert spike_result["tasks_succeeded"] == 12
    assert spike_result["tasks_failed"] == 0
    assert spike_result["scaled_up"] is True
    assert spike_result["peak_workers"] > 1

    final_status = pool.get_status()
    assert final_status["completed_tasks"] == 12

    pool.shutdown(wait=True)


def test_autoscaling_pool_queue_backpressure_rejection():
    """Verify pool rejects tasks with QueueBackpressureError when queue depth limit is exceeded."""
    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=1,
        max_queue_depth=3,
        scale_up_threshold_queue_depth=10,
    )
    pool = AutoscalingWorkerPool(config=config)

    # Submit slow tasks to fill queue
    futures = []
    rejected = False
    try:
        for _ in range(10):
            fut = pool.submit(time.sleep, 0.2)
            futures.append(fut)
    except QueueBackpressureError:
        rejected = True

    assert rejected is True

    pool.shutdown(wait=False)


def test_constrained_reasoning_engine_trace_correlation(tmp_path):
    """Verify end-to-end reasoning engine run populates W3C TraceContext and emits linked spans."""
    spec = _create_minimal_spec()
    tracer = Tracer(service_name="agent-factory-test")
    engine = ConstrainedReasoningEngine(spec=spec, workspace_root=tmp_path, tracer=tracer)

    # 1. Intake
    clean_inputs = engine.intake({"task_data": "Analyze telemetry spike logs"})
    assert clean_inputs["task_data"] == "Analyze telemetry spike logs"

    # 2. Plan
    engine.plan_step("Profile anomalies and generate markdown/json summaries")

    # 3. Tool execution
    def dummy_read(path: str):
        return f"Telemetry logs from {path}"

    res = engine.execute_guarded_tool(
        tool_name="file_reader",
        tool_args={"path": "telemetry.log"},
        tool_callable=dummy_read,
    )
    assert "telemetry.log" in res

    # 4. Output verification
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_file = artifacts_dir / "summary.json"
    out_file.write_text(json.dumps({"status": "SUCCESS"}), encoding="utf-8")

    trace = engine.finalize_and_verify_outputs(
        artifacts_created={"summary": str(out_file)},
        output_text="Analysis complete. All traces valid.",
    )

    assert trace.status == "COMPLETE"
    assert trace.trace_id is not None
    assert trace.span_id is not None
    assert trace.traceparent is not None
    assert trace.traceparent.startswith(f"00-{trace.trace_id}-{trace.span_id}-")

    # Verify spans recorded in tracer
    spans = tracer.get_spans_for_trace(trace.trace_id)
    span_names = [s.name for s in spans]

    assert f"reasoning_chain:{spec.agent_id}" in span_names
    assert "input_rail_screening" in span_names
    assert "dialog_rail_planning" in span_names
    assert "tool_execution:file_reader" in span_names
    assert "output_rail_verification" in span_names
