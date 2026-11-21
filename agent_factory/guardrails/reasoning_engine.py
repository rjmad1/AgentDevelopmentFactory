"""
Bounded Agent Reasoning Engine with NeMo & NIST Guardrail Enforcement.
Treats the ingested specification pack as the authoritative source of truth.
Blocks any execution path that deviates from certified specifications or violates security boundaries.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field

from agent_factory.specs.schema import (
    UniversalAgentSpec,
    EffectLevel,
    RiskTier,
)
from agent_factory.guardrails.nemo_nist import (
    RailType,
    NistControl,
    NistFrameworkCatalog,
    GuardrailViolation,
    GuardrailViolationError,
    InputRails,
    DialogRails,
    ExecutionRails,
    OutputRails,
)
from agent_factory.observability.tracer import (
    Tracer,
    TraceContext,
    Span,
    SpanKind,
    SpanStatus,
)


class ReasoningStepRecord(BaseModel):
    step_number: int
    state: str
    action_type: str
    action_name: str
    guardrails_passed: bool
    nist_controls_evaluated: List[str]
    details: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0


class BoundedExecutionTrace(BaseModel):
    agent_id: str
    version: str
    spec_authoritative_sha256: str
    risk_tier: str
    status: str  # COMPLETED, BLOCKED, ESCALATED
    steps_executed: int
    total_tokens: int
    total_cost_usd: float
    elapsed_seconds: float
    violations_detected: List[GuardrailViolation] = Field(default_factory=list)
    steps: List[ReasoningStepRecord] = Field(default_factory=list)
    artifacts: Dict[str, str] = Field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    traceparent: Optional[str] = None


class ConstrainedReasoningEngine:
    """
    Reasoning engine operating strictly within the declarative boundaries of UniversalAgentSpec.
    Applies NeMo input, dialog, execution, and output rails mapped to NIST AI RMF.
    """

    def __init__(
        self,
        spec: UniversalAgentSpec,
        workspace_root: Union[str, Path],
        approval_token: Optional[str] = None,
        tracer: Optional[Tracer] = None,
        parent_trace_context: Optional[TraceContext] = None,
    ):
        self.spec = spec
        self.workspace_root = Path(workspace_root).resolve()
        self.approval_token = approval_token

        # Compute deterministic spec hash as binding anchor
        import hashlib
        spec_json = spec.model_dump_json()
        self.spec_sha256 = hashlib.sha256(spec_json.encode("utf-8")).hexdigest()

        # Observability & Distributed Tracing
        self.tracer = tracer or Tracer(service_name=f"agent-{spec.agent_id}")
        self.root_span = self.tracer.start_span(
            name=f"reasoning_chain:{self.spec.agent_id}",
            parent_context=parent_trace_context,
            kind=SpanKind.INTERNAL,
            attributes={
                "agent.id": self.spec.agent_id,
                "agent.version": self.spec.version,
                "agent.risk_tier": self.spec.risk_tier.value,
                "spec.sha256": self.spec_sha256,
            },
        )
        self.trace_context = self.root_span.context

        # Operational state
        self.current_state = "INIT"
        self.step_count = 0
        self.accumulated_tokens = 0
        self.accumulated_cost_usd = 0.0
        self.start_time = time.perf_counter()
        self.trace_steps: List[ReasoningStepRecord] = []
        self.violations: List[GuardrailViolation] = []

    def _block_and_raise(self, violation: GuardrailViolation) -> None:
        """Transitions engine to BLOCKED status, logs violation, and raises GuardrailViolationError."""
        self.current_state = "BLOCKED"
        self.violations.append(violation)
        self.root_span.record_error(violation.message)
        self.root_span.set_attribute("guardrail.violation.rail", violation.rail_type.value if hasattr(violation.rail_type, "value") else str(violation.rail_type))
        self.root_span.set_attribute("guardrail.violation.control", str(violation.nist_control))
        self.root_span.end()
        raise GuardrailViolationError(violation)

    def intake(self, raw_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: Input Rails & Intake Gate.
        Evaluates prompt injection, schema boundaries, and PII containment.
        """
        step_start = time.perf_counter()
        evaluated_controls = ["MP-1.1", "MP-2.3", "GV-1.1", "GV-1.2", "MG-2.2"]

        with self.tracer.start_span("input_rail_screening", parent_context=self.trace_context) as span:
            span.set_attribute("rail.type", "INPUT")
            span.set_attribute("input_keys", list(raw_inputs.keys()))

            # Validate state transition
            trans_err = DialogRails.validate_state_transition(self.current_state, "INTAKE")
            if trans_err:
                span.record_error(trans_err.message)
                self._block_and_raise(trans_err)

            sanitized_inputs = {}
            for key, value in raw_inputs.items():
                if isinstance(value, str):
                    # 1. Prompt Injection Defense (NeMo input rail / NIST MP-2.3)
                    inj_err = InputRails.check_prompt_injection(value)
                    if inj_err:
                        span.record_error(inj_err.message)
                        self._block_and_raise(inj_err)

                    # 2. PII Sanitization (NIST GV-1.1 / MG-1.1)
                    clean_val, _ = InputRails.sanitize_pii(value)
                    sanitized_inputs[key] = clean_val
                else:
                    sanitized_inputs[key] = value

            # 3. Input Schema Conformity (NIST MP-1.1 / GV-1.2)
            schema_errs = InputRails.validate_input_schema(sanitized_inputs, self.spec.inputs)
            if schema_errs:
                span.record_error(schema_errs[0].message)
                self._block_and_raise(schema_errs[0])

            self.current_state = "INTAKE"
            duration = (time.perf_counter() - step_start) * 1000.0

            self.trace_steps.append(
                ReasoningStepRecord(
                    step_number=self.step_count + 1,
                    state="INTAKE",
                    action_type="INPUT_SCREENING",
                    action_name="intake_validation",
                    guardrails_passed=True,
                    nist_controls_evaluated=evaluated_controls,
                    details={"inputs_validated": list(sanitized_inputs.keys())},
                    duration_ms=round(duration, 2),
                )
            )
            return sanitized_inputs

    def plan_step(self, proposed_goal: str) -> None:
        """
        Phase 2: Dialog & Intent Rails.
        Validates goal against certified spec purpose and state transition flow.
        """
        step_start = time.perf_counter()
        evaluated_controls = ["GV-1.2", "MG-2.2"]

        with self.tracer.start_span("dialog_rail_planning", parent_context=self.trace_context) as span:
            span.set_attribute("rail.type", "DIALOG")
            span.set_attribute("proposed_goal", proposed_goal)

            trans_err = DialogRails.validate_state_transition(self.current_state, "PLAN")
            if trans_err:
                span.record_error(trans_err.message)
                self._block_and_raise(trans_err)

            # Check intent drift
            drift_err = DialogRails.check_intent_drift(proposed_goal, self.spec.purpose)
            if drift_err:
                span.record_error(drift_err.message)
                self._block_and_raise(drift_err)

            self.current_state = "PLAN"
            duration = (time.perf_counter() - step_start) * 1000.0

            self.trace_steps.append(
                ReasoningStepRecord(
                    step_number=self.step_count + 1,
                    state="PLAN",
                    action_type="REASONING_FLOW",
                    action_name="plan_goal_alignment",
                    guardrails_passed=True,
                    nist_controls_evaluated=evaluated_controls,
                    details={"proposed_goal": proposed_goal},
                    duration_ms=round(duration, 2),
                )
            )

    def guard_tool_action(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        requested_effect: EffectLevel = EffectLevel.READ_PUBLIC,
        estimated_tokens: int = 100,
        estimated_cost_usd: float = 0.0,
    ) -> None:
        """
        Phase 3: Execution & Tool Rails.
        Strictly enforces tool allowlist, path boundary, action approval tokens, and limits.
        """
        evaluated_controls = ["GV-1.2", "GV-1.3", "MP-2.3", "MG-1.1", "MG-2.2"]

        # 1. Resource Limits Governor Check (NIST MG-1.1)
        elapsed = time.perf_counter() - self.start_time
        res_err = ExecutionRails.validate_resource_governor(
            current_steps=self.step_count + 1,
            current_tokens=self.accumulated_tokens + estimated_tokens,
            current_cost=self.accumulated_cost_usd + estimated_cost_usd,
            elapsed_seconds=elapsed,
            limits=self.spec.limits,
        )
        if res_err:
            self._block_and_raise(res_err)

        # 2. Tool Allowlist Check (NIST GV-1.2)
        allow_err = ExecutionRails.validate_tool_allowlist(tool_name, self.spec)
        if allow_err:
            self._block_and_raise(allow_err)

        # 3. Permitted Effect Level Check (NIST GV-1.2)
        eff_err = ExecutionRails.validate_effect_level(requested_effect, self.spec)
        if eff_err:
            self._block_and_raise(eff_err)

        # 4. Action Gate Authorization (NIST GV-1.3)
        act_err = ExecutionRails.validate_action_gate(
            tool_name=tool_name,
            effect_level=requested_effect,
            spec=self.spec,
            approval_token=self.approval_token,
        )
        if act_err:
            self._block_and_raise(act_err)

        # 5. Path Containment & Symlink Defense (NIST MP-2.3 / MG-2.2)
        for arg_key, arg_val in tool_args.items():
            if any(term in arg_key.lower() for term in ["path", "file", "dir", "dest", "src"]) and isinstance(arg_val, (str, Path)):
                is_write = requested_effect == EffectLevel.WRITE_LOCAL_DRAFT
                path_err = ExecutionRails.validate_path_containment(
                    target_path=arg_val,
                    write=is_write,
                    workspace_root=self.workspace_root,
                    spec=self.spec,
                )
                if path_err:
                    self._block_and_raise(path_err)

    def execute_guarded_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_callable: Callable[..., Any],
        requested_effect: EffectLevel = EffectLevel.READ_PUBLIC,
        tokens_consumed: int = 100,
        cost_usd: float = 0.0,
    ) -> Any:
        """Pre-screens tool action against Execution Rails, executes it, and records trace."""
        step_start = time.perf_counter()

        with self.tracer.start_span(f"tool_execution:{tool_name}", parent_context=self.trace_context) as span:
            span.set_attribute("rail.type", "EXECUTION")
            span.set_attribute("tool.name", tool_name)
            span.set_attribute("tool.effect", requested_effect.value)

            # Guard pre-execution
            self.guard_tool_action(
                tool_name=tool_name,
                tool_args=tool_args,
                requested_effect=requested_effect,
                estimated_tokens=tokens_consumed,
                estimated_cost_usd=cost_usd,
            )

            # Execute
            self.step_count += 1
            self.accumulated_tokens += tokens_consumed
            self.accumulated_cost_usd += cost_usd

            try:
                result = tool_callable(**tool_args)
            except Exception as e:
                span.record_error(str(e))
                raise

            duration = (time.perf_counter() - step_start) * 1000.0

            self.current_state = "OBSERVE"
            self.trace_steps.append(
                ReasoningStepRecord(
                    step_number=self.step_count,
                    state="EXECUTE_TOOL",
                    action_type="TOOL_INVOCATION",
                    action_name=tool_name,
                    guardrails_passed=True,
                    nist_controls_evaluated=["GV-1.2", "GV-1.3", "MP-2.3", "MG-1.1", "MG-2.2"],
                    details={
                        "tool": tool_name,
                        "effect": requested_effect.value,
                        "tokens": tokens_consumed,
                        "cost_usd": cost_usd,
                    },
                    duration_ms=round(duration, 2),
                )
            )
            return result

    def finalize_and_verify_outputs(
        self,
        artifacts_created: Dict[str, str],
        output_text: str = "",
        ground_truth: Optional[Dict[str, Any]] = None,
    ) -> BoundedExecutionTrace:
        """
        Phase 4: Output Rails & Final Gate.
        Enforces output schema compliance, secret leak containment, and factual grounding.
        """
        step_start = time.perf_counter()
        evaluated_controls = ["MS-2.2", "MS-2.7", "GV-1.2", "MG-2.2"]

        with self.tracer.start_span("output_rail_verification", parent_context=self.trace_context) as span:
            span.set_attribute("rail.type", "OUTPUT")
            span.set_attribute("artifacts.count", len(artifacts_created))

            # Validate state transition to SYNTHESIZE
            trans_err = DialogRails.validate_state_transition(self.current_state, "SYNTHESIZE")
            if trans_err:
                span.record_error(trans_err.message)
                self._block_and_raise(trans_err)
            self.current_state = "SYNTHESIZE"

            # 1. Output Secret Leak Containment (NIST MS-2.7)
            if output_text:
                leak_err = OutputRails.check_secret_leaks(output_text)
                if leak_err:
                    span.record_error(leak_err.message)
                    self._block_and_raise(leak_err)

            # 2. Output Schema Conformity (NIST MS-2.2 / GV-1.2)
            schema_errs = OutputRails.validate_output_schema(artifacts_created, self.spec.outputs)
            if schema_errs:
                span.record_error(schema_errs[0].message)
                self._block_and_raise(schema_errs[0])

            # 3. Grounding Verification (NIST MS-2.2)
            if ground_truth and artifacts_created:
                # If summary JSON exists, inspect grounding
                for art_name, art_path in artifacts_created.items():
                    if art_path.endswith(".json") and Path(art_path).exists():
                        try:
                            with open(art_path, "r", encoding="utf-8") as f:
                                parsed_summary = json.load(f)
                            ground_err = OutputRails.verify_grounding(parsed_summary, ground_truth)
                            if ground_err:
                                span.record_error(ground_err.message)
                                self._block_and_raise(ground_err)
                        except Exception:
                            pass

        # Final transition to COMPLETE
        self.current_state = "COMPLETE"
        elapsed = time.perf_counter() - self.start_time
        duration = (time.perf_counter() - step_start) * 1000.0

        self.trace_steps.append(
            ReasoningStepRecord(
                step_number=self.step_count + 1,
                state="VERIFY_OUTPUT",
                action_type="OUTPUT_VALIDATION",
                action_name="output_schema_and_grounding",
                guardrails_passed=True,
                nist_controls_evaluated=evaluated_controls,
                details={"artifacts_verified": list(artifacts_created.keys())},
                duration_ms=round(duration, 2),
            )
        )

        self.root_span.set_attribute("steps_executed", self.step_count)
        self.root_span.set_attribute("total_tokens", self.accumulated_tokens)
        self.root_span.set_attribute("total_cost_usd", self.accumulated_cost_usd)
        self.root_span.end()

        return BoundedExecutionTrace(
            agent_id=self.spec.agent_id,
            version=self.spec.version,
            spec_authoritative_sha256=self.spec_sha256,
            risk_tier=self.spec.risk_tier.value,
            status=self.current_state,
            steps_executed=self.step_count,
            total_tokens=self.accumulated_tokens,
            total_cost_usd=self.accumulated_cost_usd,
            elapsed_seconds=round(elapsed, 2),
            violations_detected=self.violations,
            steps=self.trace_steps,
            artifacts=artifacts_created,
            trace_id=self.trace_context.trace_id,
            span_id=self.trace_context.span_id,
            traceparent=self.trace_context.to_traceparent(),
        )
