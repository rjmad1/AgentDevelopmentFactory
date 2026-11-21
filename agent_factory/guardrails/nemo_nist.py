"""
NeMo & NIST Operational Safety Guardrail Framework.
Implements programmable 4-phase guardrails derived from NeMo Guardrails architecture
and rigorously mapped to the NIST AI Risk Management Framework (NIST AI 100-1).
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from pydantic import BaseModel, Field

from agent_factory.specs.schema import (
    UniversalAgentSpec,
    RiskTier,
    EffectLevel,
    RiskClassification,
    InputParameter,
    OutputParameter,
    LimitsSpec,
)
from agent_factory.security.redactor import SecretRedactor
from agent_factory.security.approval_gate import ApprovalGate


class RailType(str, Enum):
    INPUT_RAIL = "INPUT_RAIL"
    DIALOG_RAIL = "DIALOG_RAIL"
    EXECUTION_RAIL = "EXECUTION_RAIL"
    OUTPUT_RAIL = "OUTPUT_RAIL"


class NistFunction(str, Enum):
    GOVERN = "GOVERN"
    MAP = "MAP"
    MEASURE = "MEASURE"
    MANAGE = "MANAGE"


class NistControl(BaseModel):
    code: str
    function: NistFunction
    title: str
    description: str


class GuardrailViolation(BaseModel):
    rail_type: RailType
    rail_name: str
    nist_control: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    message: str
    offending_payload: Optional[str] = None


class GuardrailViolationError(PermissionError):
    """Raised when an execution path violates declarative schema or security boundaries."""
    def __init__(self, violation: GuardrailViolation):
        self.violation = violation
        super().__init__(
            f"[{violation.rail_type.value} BLOCKED | NIST {violation.nist_control}] "
            f"({violation.severity}) {violation.rail_name}: {violation.message}"
        )


class NistFrameworkCatalog:
    """NIST AI RMF (AI 100-1) Control Catalog mapped to NeMo Guardrails."""

    CONTROLS = {
        "GV-1.1": NistControl(
            code="GV-1.1",
            function=NistFunction.GOVERN,
            title="Legal & Regulatory Boundary Governance",
            description="Legal, regulatory, and policy boundaries are identified and enforced at runtime."
        ),
        "GV-1.2": NistControl(
            code="GV-1.2",
            function=NistFunction.GOVERN,
            title="Declarative System Scope & Policy Governance",
            description="System boundaries, tool permissions, and operational constraints are formally specified."
        ),
        "GV-1.3": NistControl(
            code="GV-1.3",
            function=NistFunction.GOVERN,
            title="Human Authorization & Authority Gating",
            description="High-impact actions require explicit cryptographic human approval tokens."
        ),
        "GV-3.1": NistControl(
            code="GV-3.1",
            function=NistFunction.GOVERN,
            title="Continuous Audit Logging & Traceability",
            description="Audit records, guardrail triggers, and verification decisions are recorded in an append-only ledger."
        ),
        "MP-1.1": NistControl(
            code="MP-1.1",
            function=NistFunction.MAP,
            title="Operational Context & Boundary Mapping",
            description="Inputs, schemas, and operating environment parameters are explicitly bounded."
        ),
        "MP-2.3": NistControl(
            code="MP-2.3",
            function=NistFunction.MAP,
            title="Adversarial Threat & Injection Categorization",
            description="Known failure modes, prompt injection vectors, and unauthorized paths are categorized."
        ),
        "MS-2.2": NistControl(
            code="MS-2.2",
            function=NistFunction.MEASURE,
            title="Reliability, Schema & Grounding Measurement",
            description="Outputs are quantitatively verified against schemas, constraints, and factual source data."
        ),
        "MS-2.7": NistControl(
            code="MS-2.7",
            function=NistFunction.MEASURE,
            title="Security & Secret Containment Measurement",
            description="Outputs and memory state are continuously scanned for secret leakage and contamination."
        ),
        "MG-1.1": NistControl(
            code="MG-1.1",
            function=NistFunction.MANAGE,
            title="Resource Ceiling & Governor Management",
            description="Execution step count, token consumption, wall time, and financial spend are capped."
        ),
        "MG-2.2": NistControl(
            code="MG-2.2",
            function=NistFunction.MANAGE,
            title="Active Operational Safety & Fail-Safe Execution Blocking",
            description="Execution paths deviating from certified specifications are blocked immediately."
        ),
        "MG-2.4": NistControl(
            code="MG-2.4",
            function=NistFunction.MANAGE,
            title="Fail-Safe Escalation & Containment Protocol",
            description="Violations trigger safe fallback, execution halt, and escalation to human review."
        ),
    }

    @classmethod
    def get_control(cls, code: str) -> Optional[NistControl]:
        return cls.CONTROLS.get(code)


class InputRails:
    """
    Phase 1: Input Rails (NeMo programmable input guardrails).
    Guards against prompt injection, input schema deviation, and sensitive PII ingestion.
    """

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"(ignore|disregard|forget|override|bypass)\s+(all\s+)?(previous|prior|above|system)?\s*(instructions|prompts|rules|guidelines|policies)", re.IGNORECASE),
        re.compile(r"(you\s+are\s+now|act\s+as|pretend\s+to\s+be)\s+(DAN|unfiltered|jailbroken|an\s+unrestricted\s+ai|root|admin)", re.IGNORECASE),
        re.compile(r"(\<\|im_start\|\>|\<\|im_end\|\>|\[INST\]|\[\/INST\]|\<\<SYS\>\>|\<\<\/SYS\>\>|---BEGIN SYSTEM---)", re.IGNORECASE),
        re.compile(r"(disable|turn\s+off|circumvent|deactivate)\s+(guardrails?|safety|filters?|security|checks?)", re.IGNORECASE),
        re.compile(r"(do\s+anything\s+now|jailbreak\s+mode|developer\s+mode\s+enabled)", re.IGNORECASE),
        re.compile(r"(system\s*:\s*you\s+must|new\s+system\s+directive|hidden\s+instruction)", re.IGNORECASE),
    ]

    PII_PATTERNS = [
        (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
        (re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"), "[REDACTED_CREDIT_CARD]"),
        (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    ]

    @classmethod
    def check_prompt_injection(cls, text: str) -> Optional[GuardrailViolation]:
        """Detects prompt injection and jailbreak payloads (NIST MP-2.3 / MG-2.2)."""
        if not text or not isinstance(text, str):
            return None

        for pat in cls.PROMPT_INJECTION_PATTERNS:
            match = pat.search(text)
            if match:
                return GuardrailViolation(
                    rail_type=RailType.INPUT_RAIL,
                    rail_name="PromptInjectionDefense",
                    nist_control="MP-2.3",
                    severity="CRITICAL",
                    message=f"Prompt injection pattern detected: '{match.group(0)}'. Execution path blocked.",
                    offending_payload=match.group(0),
                )
        return None

    @classmethod
    def validate_input_schema(
        cls, inputs: Dict[str, Any], declared_inputs: Dict[str, InputParameter]
    ) -> List[GuardrailViolation]:
        """Validates input payload conforms strictly to declarative schema (NIST MP-1.1 / GV-1.2)."""
        violations = []

        # Check for required inputs
        for name, param in declared_inputs.items():
            if param.required and name not in inputs and param.default is None:
                violations.append(
                    GuardrailViolation(
                        rail_type=RailType.INPUT_RAIL,
                        rail_name="InputSchemaConformity",
                        nist_control="MP-1.1",
                        severity="HIGH",
                        message=f"Missing mandatory input parameter '{name}' declared in specification.",
                        offending_payload=name,
                    )
                )

        # Check types for provided inputs
        for name, value in inputs.items():
            if name not in declared_inputs:
                violations.append(
                    GuardrailViolation(
                        rail_type=RailType.INPUT_RAIL,
                        rail_name="InputSchemaConformity",
                        nist_control="GV-1.2",
                        severity="MEDIUM",
                        message=f"Undeclared input parameter '{name}' violates declarative specification boundary.",
                        offending_payload=name,
                    )
                )
                continue

            param = declared_inputs[name]
            expected_type = param.type.lower()

            if expected_type in ["string", "file"] and not isinstance(value, str):
                violations.append(
                    GuardrailViolation(
                        rail_type=RailType.INPUT_RAIL,
                        rail_name="InputSchemaConformity",
                        nist_control="MP-1.1",
                        severity="HIGH",
                        message=f"Input '{name}' must be of type string, got {type(value).__name__}.",
                        offending_payload=str(value),
                    )
                )
            elif expected_type == "integer" and not (isinstance(value, int) and not isinstance(value, bool)):
                violations.append(
                    GuardrailViolation(
                        rail_type=RailType.INPUT_RAIL,
                        rail_name="InputSchemaConformity",
                        nist_control="MP-1.1",
                        severity="HIGH",
                        message=f"Input '{name}' must be of type integer, got {type(value).__name__}.",
                        offending_payload=str(value),
                    )
                )
            elif expected_type == "float" and not isinstance(value, (int, float)):
                violations.append(
                    GuardrailViolation(
                        rail_type=RailType.INPUT_RAIL,
                        rail_name="InputSchemaConformity",
                        nist_control="MP-1.1",
                        severity="HIGH",
                        message=f"Input '{name}' must be of type float, got {type(value).__name__}.",
                        offending_payload=str(value),
                    )
                )
            elif expected_type == "boolean" and not isinstance(value, bool):
                violations.append(
                    GuardrailViolation(
                        rail_type=RailType.INPUT_RAIL,
                        rail_name="InputSchemaConformity",
                        nist_control="MP-1.1",
                        severity="HIGH",
                        message=f"Input '{name}' must be of type boolean, got {type(value).__name__}.",
                        offending_payload=str(value),
                    )
                )

        return violations

    @classmethod
    def sanitize_pii(cls, text: str) -> Tuple[str, bool]:
        """Redacts PII tokens from input text (NIST GV-1.1 / MG-1.1)."""
        if not text or not isinstance(text, str):
            return text, False

        redacted = text
        modified = False
        for pattern, replacement in cls.PII_PATTERNS:
            if pattern.search(redacted):
                redacted = pattern.sub(replacement, redacted)
                modified = True

        # Also apply secret redaction
        clean_text = SecretRedactor.redact_text(redacted)
        if clean_text != redacted:
            modified = True

        return clean_text, modified


class DialogRails:
    """
    Phase 2: Dialog & Reasoning Rails (NeMo programmable dialog guardrails).
    Guards against intent drift, uncertified goal hijacking, and illegal state transitions.
    """

    PROHIBITED_INTENT_KEYWORDS = [
        "delete_system_files",
        "format_disk",
        "drop_database",
        "exfiltrate_secrets",
        "bypass_authentication",
        "execute_arbitrary_shell",
        "grant_admin_access",
        "reverse_shell",
        "crypto_mining",
    ]

    CERTIFIED_STATE_TRANSITIONS = {
        "INIT": ["INTAKE"],
        "INTAKE": ["PLAN", "BLOCKED"],
        "PLAN": ["EXECUTE_TOOL", "SYNTHESIZE", "BLOCKED"],
        "EXECUTE_TOOL": ["OBSERVE", "BLOCKED"],
        "OBSERVE": ["PLAN", "EXECUTE_TOOL", "SYNTHESIZE", "BLOCKED"],
        "SYNTHESIZE": ["VERIFY_OUTPUT", "BLOCKED"],
        "VERIFY_OUTPUT": ["COMPLETE", "BLOCKED"],
        "COMPLETE": [],
        "BLOCKED": ["ESCALATED"],
        "ESCALATED": [],
    }

    @classmethod
    def check_intent_drift(
        cls, proposed_action: str, certified_purpose: str
    ) -> Optional[GuardrailViolation]:
        """Ensures proposed action stays within certified agent purpose (NIST GV-1.2 / MG-2.2)."""
        action_lower = proposed_action.lower()

        # Check explicitly prohibited intents
        for kw in cls.PROHIBITED_INTENT_KEYWORDS:
            if kw in action_lower:
                return GuardrailViolation(
                    rail_type=RailType.DIALOG_RAIL,
                    rail_name="IntentDriftPrevention",
                    nist_control="GV-1.2",
                    severity="CRITICAL",
                    message=f"Action '{proposed_action}' contains prohibited intent '{kw}'. Bounded execution blocked.",
                    offending_payload=kw,
                )

        return None

    @classmethod
    def validate_state_transition(
        cls, current_state: str, next_state: str
    ) -> Optional[GuardrailViolation]:
        """Enforces canonical state machine flow (NIST MG-2.2)."""
        allowed = cls.CERTIFIED_STATE_TRANSITIONS.get(current_state, [])
        if next_state not in allowed:
            return GuardrailViolation(
                rail_type=RailType.DIALOG_RAIL,
                rail_name="StateTransitionIntegrity",
                nist_control="MG-2.2",
                severity="HIGH",
                message=f"Illegal state transition from '{current_state}' to '{next_state}'. Allowed: {allowed}.",
                offending_payload=f"{current_state} -> {next_state}",
            )
        return None


class ExecutionRails:
    """
    Phase 3: Execution & Tool Rails (NeMo programmable tool guardrails).
    Guards against unauthorized tool calls, schema parameter deviations, path traversal,
    missing action approval tokens, and resource exhaustion.
    """

    @classmethod
    def validate_tool_allowlist(
        cls, tool_name: str, spec: UniversalAgentSpec
    ) -> Optional[GuardrailViolation]:
        """Enforces strict tool allowlist from declarative spec (NIST GV-1.2 / MG-2.2)."""
        permitted = spec.policy.permitted_tools
        if tool_name not in permitted:
            return GuardrailViolation(
                rail_type=RailType.EXECUTION_RAIL,
                rail_name="ToolAllowlistEnforcement",
                nist_control="GV-1.2",
                severity="CRITICAL",
                message=f"Tool '{tool_name}' is not permitted by declarative specification allowlist: {permitted}.",
                offending_payload=tool_name,
            )
        return None

    @classmethod
    def validate_effect_level(
        cls, requested_effect: EffectLevel, spec: UniversalAgentSpec
    ) -> Optional[GuardrailViolation]:
        """Enforces permitted effect levels from declarative spec (NIST GV-1.2 / MG-2.2)."""
        permitted = spec.policy.permitted_effects
        if requested_effect not in permitted:
            return GuardrailViolation(
                rail_type=RailType.EXECUTION_RAIL,
                rail_name="EffectBoundaryEnforcement",
                nist_control="GV-1.2",
                severity="HIGH",
                message=f"Effect '{requested_effect.value}' exceeds permitted boundaries: {[e.value for e in permitted]}.",
                offending_payload=requested_effect.value,
            )
        return None

    @classmethod
    def validate_path_containment(
        cls,
        target_path: Union[str, Path],
        write: bool,
        workspace_root: Path,
        spec: UniversalAgentSpec,
    ) -> Optional[GuardrailViolation]:
        """Enforces real filesystem containment and symlink/junction defense (NIST MP-2.3 / MG-2.2)."""
        ws_root = workspace_root.resolve()
        p = Path(target_path)
        resolved = (ws_root / p).resolve() if not p.is_absolute() else p.resolve()

        # Boundary check
        is_contained = str(resolved).startswith(str(ws_root))

        if write and not is_contained:
            return GuardrailViolation(
                rail_type=RailType.EXECUTION_RAIL,
                rail_name="PathContainmentDefense",
                nist_control="MG-2.2",
                severity="CRITICAL",
                message=f"Security Boundary Violation: Write attempted outside workspace at '{resolved}'.",
                offending_payload=str(resolved),
            )

        if not write and not is_contained:
            has_read_perm = (
                EffectLevel.READ_PUBLIC in spec.policy.permitted_effects
                or EffectLevel.READ_PRIVATE in spec.policy.permitted_effects
            )
            if not has_read_perm:
                return GuardrailViolation(
                    rail_type=RailType.EXECUTION_RAIL,
                    rail_name="PathContainmentDefense",
                    nist_control="MG-2.2",
                    severity="HIGH",
                    message=f"Security Boundary Violation: Reading outside workspace at '{resolved}' without explicit read permission.",
                    offending_payload=str(resolved),
                )

        return None

    @classmethod
    def validate_action_gate(
        cls,
        tool_name: str,
        effect_level: EffectLevel,
        spec: UniversalAgentSpec,
        approval_token: Optional[str] = None,
    ) -> Optional[GuardrailViolation]:
        """Enforces cryptographic human approval tokens for elevated actions (NIST GV-1.3 / MG-2.2)."""
        elevated_effects = [
            EffectLevel.WRITE_LOCAL_DRAFT,
            EffectLevel.CHANGE_ACCOUNT,
            EffectLevel.SEND_PUBLISH,
            EffectLevel.SPEND_DELETE,
        ]

        if effect_level in elevated_effects:
            # T1, T2, T3 require approval for write/external/spend actions
            if spec.risk_tier in [RiskTier.T1, RiskTier.T2, RiskTier.T3]:
                risk_class = (
                    RiskClassification.HIGH
                    if spec.risk_tier in [RiskTier.T2, RiskTier.T3]
                    else RiskClassification.MEDIUM
                )
                is_valid = ApprovalGate.verify_token(
                    approval_token, spec.agent_id, tool_name, risk_class
                )
                if not is_valid:
                    return GuardrailViolation(
                        rail_type=RailType.EXECUTION_RAIL,
                        rail_name="ActionGateAuthorization",
                        nist_control="GV-1.3",
                        severity="CRITICAL",
                        message=(
                            f"Action Gate Intercept: Elevated action '{tool_name}' ({effect_level.value}) "
                            f"at Risk Tier '{spec.risk_tier.value}' requires a valid cryptographic approval token."
                        ),
                        offending_payload=tool_name,
                    )
        return None

    @classmethod
    def validate_resource_governor(
        cls,
        current_steps: int,
        current_tokens: int,
        current_cost: float,
        elapsed_seconds: float,
        limits: LimitsSpec,
    ) -> Optional[GuardrailViolation]:
        """Enforces hard execution resource ceilings (NIST MG-1.1 / MG-2.2)."""
        if current_steps > limits.max_steps:
            return GuardrailViolation(
                rail_type=RailType.EXECUTION_RAIL,
                rail_name="ResourceCeilingGovernor",
                nist_control="MG-1.1",
                severity="HIGH",
                message=f"Step count {current_steps} exceeded maximum step ceiling {limits.max_steps}.",
                offending_payload=f"steps={current_steps}",
            )

        if current_tokens > limits.max_tokens:
            return GuardrailViolation(
                rail_type=RailType.EXECUTION_RAIL,
                rail_name="ResourceCeilingGovernor",
                nist_control="MG-1.1",
                severity="HIGH",
                message=f"Token consumption {current_tokens} exceeded maximum token ceiling {limits.max_tokens}.",
                offending_payload=f"tokens={current_tokens}",
            )

        if current_cost > limits.paid_spend_ceiling:
            return GuardrailViolation(
                rail_type=RailType.EXECUTION_RAIL,
                rail_name="ResourceCeilingGovernor",
                nist_control="MG-1.1",
                severity="CRITICAL",
                message=f"Projected cost ${current_cost:.4f} exceeded spend ceiling ${limits.paid_spend_ceiling:.4f}.",
                offending_payload=f"cost={current_cost}",
            )

        if elapsed_seconds > limits.max_wall_time_seconds:
            return GuardrailViolation(
                rail_type=RailType.EXECUTION_RAIL,
                rail_name="ResourceCeilingGovernor",
                nist_control="MG-1.1",
                severity="HIGH",
                message=f"Elapsed wall time {elapsed_seconds:.1f}s exceeded ceiling {limits.max_wall_time_seconds}s.",
                offending_payload=f"time={elapsed_seconds}",
            )

        return None


class OutputRails:
    """
    Phase 4: Output Rails (NeMo programmable output guardrails).
    Guards against output schema violation, secret leaks, and ungrounded hallucinations.
    """

    @classmethod
    def validate_output_schema(
        cls, generated_artifacts: Dict[str, str], declared_outputs: Dict[str, OutputParameter]
    ) -> List[GuardrailViolation]:
        """Enforces output artifacts match declared schema specifications (NIST MS-2.2 / GV-1.2)."""
        violations = []

        for out_name, out_spec in declared_outputs.items():
            if out_spec.path:
                expected_filename = Path(out_spec.path).name
                found = any(Path(p).name == expected_filename for p in generated_artifacts.values())
                if not found:
                    violations.append(
                        GuardrailViolation(
                            rail_type=RailType.OUTPUT_RAIL,
                            rail_name="OutputSchemaConformity",
                            nist_control="MS-2.2",
                            severity="HIGH",
                            message=f"Declared output artifact '{out_name}' ({out_spec.path}) was not produced.",
                            offending_payload=out_spec.path,
                        )
                    )

        return violations

    @classmethod
    def check_secret_leaks(cls, text: str) -> Optional[GuardrailViolation]:
        """Detects credential or secret token leakage in output (NIST MS-2.7 / MG-2.2)."""
        if not text or not isinstance(text, str):
            return None

        # Check raw patterns before redaction
        for pattern, label in SecretRedactor.PATTERNS:
            match = pattern.search(text)
            if match:
                return GuardrailViolation(
                    rail_type=RailType.OUTPUT_RAIL,
                    rail_name="SecretLeakContainment",
                    nist_control="MS-2.7",
                    severity="CRITICAL",
                    message=f"Output contains sensitive credential leak ({label}). Output blocked.",
                    offending_payload=label,
                )
        return None

    @classmethod
    def verify_grounding(
        cls, output_summary: Dict[str, Any], ground_truth: Dict[str, Any]
    ) -> Optional[GuardrailViolation]:
        """Verifies output claims ground in verified input facts (NIST MS-2.2)."""
        if not ground_truth:
            return None

        # Check record counts or summary fields if present in ground truth
        gt_rows = ground_truth.get("total_rows") or ground_truth.get("total_entries")
        out_rows = output_summary.get("total_rows") or output_summary.get("total_records")

        if gt_rows is not None and out_rows is not None:
            if int(gt_rows) != int(out_rows):
                return GuardrailViolation(
                    rail_type=RailType.OUTPUT_RAIL,
                    rail_name="FactualGroundingVerification",
                    nist_control="MS-2.2",
                    severity="HIGH",
                    message=f"Ungrounded Hallucination: Output claims {out_rows} total rows, but source truth contains {gt_rows}.",
                    offending_payload=f"out={out_rows}, gt={gt_rows}",
                )

        return None
