"""
Agent Threat Modeler implementing OWASP Top 10 for Agentic Applications (genai.owasp.org [S18]).
Performs automated pre-flight security evaluation of Universal Agent Specifications before generation.
"""

from typing import Dict, Any, List
from pydantic import BaseModel
from agent_factory.specs.schema import UniversalAgentSpec, EffectLevel, RiskClassification


class ThreatFinding(BaseModel):
    category: str
    risk_level: str
    description: str
    remediation: str


class ThreatReport(BaseModel):
    agent_id: str
    risk_score: float  # 0.0 to 10.0
    passed: bool
    findings: List[ThreatFinding]
    recommendations: List[str]


class AgentThreatModeler:
    """Evaluates agent blueprints against the OWASP Top 10 for Agentic Applications."""

    @classmethod
    def evaluate_blueprint(cls, spec: UniversalAgentSpec) -> ThreatReport:
        findings: List[ThreatFinding] = []
        score = 0.0

        # ASI01: Goal Hijacking
        # Check if user inputs have unbounded type or if instructions lack isolation
        if any(inp.type == "string" and inp.required for inp in spec.inputs.values()):
            if spec.policy.mode == "full_autonomous":
                findings.append(ThreatFinding(
                    category="ASI01: Goal Hijacking Risk",
                    risk_level="HIGH",
                    description="Unbounded string inputs accepted under full_autonomous mode without mandatory human oversight.",
                    remediation="Demote mode to draft_only or require approval token for critical state transitions."
                ))
                score += 3.5

        # ASI02: Tool Misuse / Excessive Agency
        high_effects = {EffectLevel.SEND_PUBLISH, EffectLevel.SPEND_DELETE, EffectLevel.CHANGE_ACCOUNT}
        granted_high_effects = high_effects.intersection(set(spec.policy.permitted_effects))
        if granted_high_effects:
            findings.append(ThreatFinding(
                category="ASI02: Tool Misuse & Excessive Agency Risk",
                risk_level="HIGH",
                description=f"Agent permitted high-impact effects {[e.value for e in granted_high_effects]}. Requires explicit approval gate token before execution.",
                remediation="Ensure elevated effects are gated behind ApprovalGate and require explicit token."
            ))
            score += 3.0

        # ASI03: Memory and Context Poisoning
        if "session_tokens" in spec.state.durable_fields or "credentials" in spec.state.durable_fields:
            findings.append(ThreatFinding(
                category="ASI03: Memory & Context Poisoning",
                risk_level="HIGH",
                description="Sensitive authentication credentials declared in durable cross-session state fields.",
                remediation="Remove credentials from durable_fields; use ephemeral memory only."
            ))
            score += 3.0

        # ASI04: Insecure Output Handling
        # Check if outputs include executable script formats without AST quarantine
        executable_outputs = [out for out in spec.outputs.values() if out.format in ["sh", "bash", "exe", "py"]]
        if executable_outputs:
            findings.append(ThreatFinding(
                category="ASI04: Insecure Output Handling",
                risk_level="MEDIUM",
                description="Agent emits raw executable code artifacts. Must be subjected to AST quarantine audit.",
                remediation="Route generated code through SkillQuarantine before execution."
            ))
            score += 2.0

        # ASI05: Sensitive Information Disclosure
        if isinstance(spec.policy.secrets, list) and any(s.startswith("sk-") or len(s) > 30 for s in spec.policy.secrets):
            findings.append(ThreatFinding(
                category="ASI05: Sensitive Information Disclosure / Raw Secret Leakage",
                risk_level="CRITICAL",
                description="Raw credential string detected in policy secrets configuration.",
                remediation="Replace raw secrets with named indirect environment references (e.g. 'ENV_API_KEY')."
            ))
            score += 5.0

        # Paid spend ceiling check
        if spec.limits.paid_spend_ceiling > 0.0:
            findings.append(ThreatFinding(
                category="FinOps / Unbounded Spend",
                risk_level="LOW",
                description=f"Paid spend ceiling set to ${spec.limits.paid_spend_ceiling} (non-zero).",
                remediation="Ensure paid API calls are tracked with per-run telemetry meters."
            ))
            score += 1.0

        risk_score = min(round(score, 1), 10.0)
        passed = risk_score < 4.0 and not any(f.risk_level == "CRITICAL" for f in findings)

        recommendations = [f.remediation for f in findings]
        if passed:
            recommendations.append("Blueprint conforms to baseline OWASP Agentic Top 10 controls.")

        return ThreatReport(
            agent_id=spec.agent_id,
            risk_score=risk_score,
            passed=passed,
            findings=findings,
            recommendations=recommendations,
        )
