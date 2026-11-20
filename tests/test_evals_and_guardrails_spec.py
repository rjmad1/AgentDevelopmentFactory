"""
Comprehensive Verification Tests for ADF Evals and Guardrails Specification.
Verifies Risk Tiers (T0-T3), EV-01..15 Catalogue, Reliability (pass@k vs pass^k),
10-Layer Guardrails (G1..G10), SEC-01..10 Adversarial Suite, and 9 Release Gates.
"""

import pytest
import yaml
from pathlib import Path

from agent_factory.specs.schema import (
    RiskTier,
    UniversalAgentSpec,
    InputParameter,
    OutputParameter,
    PolicySpec,
    LimitsSpec,
    AcceptanceSpec,
    EffectLevel,
)
from agent_factory.evals.eval_catalogue import (
    EvalCatalogue,
    EvalRecord,
    ReliabilityCalculator,
    EvalGenerator,
    GraderType,
)
from agent_factory.security.guardrail_engine import GuardrailEngine, GuardrailPolicy
from agent_factory.security.adversarial_suite import AdversarialSuiteRunner
from agent_factory.evals.release_gates import ReleaseGateVerifier, ReleaseGateReport
from agent_factory.evals.metrics import MetricsCalculator, EfficiencyMetrics, EvaluationScore


def _create_sample_spec(tier: RiskTier = RiskTier.T0, agent_id: str = "sample_eval_agent") -> UniversalAgentSpec:
    return UniversalAgentSpec(
        schema_version=1,
        agent_id=agent_id,
        version="1.0.0",
        owner="EvaluationEngineer",
        risk_tier=tier,
        purpose="Analyze telemetry metrics and produce quality reports without side effects.",
        inputs={"data_path": InputParameter(type="string", description="CSV data path")},
        outputs={"report": OutputParameter(type="markdown", path="artifacts/report.md")},
        policy=PolicySpec(
            mode="read_only" if tier == RiskTier.T0 else "full_autonomous",
            permitted_tools=["read_local_csv", "compute_metrics"],
            permitted_effects=[EffectLevel.READ_PUBLIC],
        ),
        limits=LimitsSpec(
            max_steps=20,
            max_tokens=8000,
            max_wall_time_seconds=60,
            paid_spend_ceiling=0.0,
        ),
        acceptance=AcceptanceSpec(
            suite="test_evals/standard_eval.json",
            minimum_efficacy=0.95,
            minimum_safety=1.00,
        ),
    )


def test_eval_catalogue_completeness_ev01_to_ev15():
    """Verify all 15 eval catalog specifications from Section 3.5 are defined."""
    entries = EvalCatalogue.list_all()
    assert len(entries) == 15, f"Expected 15 eval catalogue definitions, got {len(entries)}"

    ids = [e.id for e in entries]
    for i in range(1, 16):
        expected_id = f"EV-{i:02d}"
        assert expected_id in ids, f"Missing catalogue ID: {expected_id}"

    # Verify EV-06 (Refusal and escalation) requires T1+
    ev06 = EvalCatalogue.get_eval("EV-06")
    assert ev06 is not None
    assert RiskTier.T0 not in ev06.applicable_tiers
    assert RiskTier.T1 in ev06.applicable_tiers
    assert RiskTier.T2 in ev06.applicable_tiers


def test_reliability_calculator_pass_at_k_and_pass_power_k():
    """Verify pass@k vs pass^k reliability metrics per Section 3.4."""
    # Scenario: 5 trials with 4 successes and 1 failure
    trials_mixed = [True, True, True, True, False]

    # pass@1: 1 random sample has 4/5 = 0.8 probability of success
    pass_at_1 = ReliabilityCalculator.calculate_pass_at_k(trials_mixed, k=1)
    assert pass_at_1 == 0.8

    # pass@2: 2 random samples out of 5 (with only 1 failure) guarantees >=1 success -> 1.0
    pass_at_2 = ReliabilityCalculator.calculate_pass_at_k(trials_mixed, k=2)
    assert pass_at_2 == 1.0

    # pass^k: all k must succeed -> 0.0 (because 1 failed)
    pass_power_k = ReliabilityCalculator.calculate_pass_power_k(trials_mixed)
    assert pass_power_k == 0.0, "pass^k must be 0.0 when any trial fails"

    # All 5 succeed
    trials_perfect = [True, True, True, True, True]
    assert ReliabilityCalculator.calculate_pass_power_k(trials_perfect) == 1.0

    # Compounding error: 3-step sequence with [0.95, 0.95, 0.95]
    compounding = ReliabilityCalculator.calculate_compounding_error([0.95, 0.95, 0.95])
    assert compounding == round(0.95 ** 3, 4)
    assert compounding < 0.86, "Compounding error must reflect probability loss across multi-step execution"


def test_eval_record_anatomy_per_section_3_1():
    """Verify EvalRecord schema conforms to Section 3.1 anatomy."""
    record = EvalRecord(
        id="EVAL-TEST-001",
        agent_version="1.0.0",
        task="Audit supplier catalog anomalies",
        inputs={"catalog_url": "fixtures/sample.csv"},
        environment_fixture="local_sqlite_db",
        graders=[GraderType.CODE, GraderType.LLM_JUDGE],
        trials=3,
        outcome="PASSED",
        transcript=[
            {"step": 1, "tool": "read_local_csv", "result": "10 rows loaded"},
            {"step": 2, "action": "compute_statistics", "result": "mean=42.0"},
        ],
        cost=0.0,
        latency=45.2,
    )
    assert record.id == "EVAL-TEST-001"
    assert record.trials == 3
    assert len(record.transcript) == 2
    assert record.cost == 0.0


def test_guardrail_policy_generator_and_yaml_section_4_3():
    """Verify Section 4.3 canonical YAML guardrail policy generation."""
    spec_t1 = _create_sample_spec(tier=RiskTier.T1, agent_id="rfq_drafter")
    spec_t1.policy.permitted_tools = ["read_supplier_catalog", "draft_email", "send_email"]
    spec_t1.policy.permitted_effects = [EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT, EffectLevel.SEND_PUBLISH]

    policy = GuardrailEngine.generate_policy(spec_t1)
    assert policy.agent == "rfq_drafter"
    assert policy.risk_tier == RiskTier.T1

    # In T1, write/send tools require approval tokens
    assert "send_email" in policy.tools.approval_required
    assert policy.limits.max_cost_per_run_usd <= 0.50
    assert policy.data.pii_redaction is True

    # Test YAML serialization matches spec format
    yaml_text = GuardrailEngine.serialize_policy_yaml(policy)
    loaded = yaml.safe_load(yaml_text)
    assert loaded["agent"] == "rfq_drafter"
    assert loaded["risk_tier"] == "T1"
    assert "send_email" in loaded["tools"]["approval_required"]
    assert loaded["data"]["pii_redaction"] is True
    assert "human_queue" == loaded["escalation"]["to"]


def test_guardrail_coverage_tier_audit():
    """Verify 100% mandatory guardrail coverage check by tier per Section 4.2."""
    spec_t0 = _create_sample_spec(tier=RiskTier.T0)
    audit_t0 = GuardrailEngine.audit_guardrail_coverage(spec_t0)
    assert audit_t0["passed"] is True
    assert len(audit_t0["missing_mandatory_layers"]) == 0
    assert audit_t0["coverage_percentage"] >= 80.0

    # Test T1 audit with approval requirement
    spec_t1 = _create_sample_spec(tier=RiskTier.T1)
    audit_t1 = GuardrailEngine.audit_guardrail_coverage(spec_t1)
    assert audit_t1["passed"] is True


def test_adversarial_security_suite_sec01_to_sec10():
    """Verify SEC-01 through SEC-10 adversarial test evaluations."""
    spec = _create_sample_spec(tier=RiskTier.T0)
    sec_res = AdversarialSuiteRunner.evaluate_agent(spec)

    assert sec_res.total_tests == 10
    assert sec_res.passed_tests == 10
    assert sec_res.has_critical_or_high_failure is False
    assert sec_res.passed is True

    # Adversarial vulnerability test: raw secret declaration must fail SEC-06
    vulnerable_spec = _create_sample_spec(tier=RiskTier.T0)
    vulnerable_spec.policy.secrets = ["sk-live12345678901234567890abcdef"]
    vuln_res = AdversarialSuiteRunner.evaluate_agent(vulnerable_spec)
    assert vuln_res.passed is False
    assert vuln_res.has_critical_or_high_failure is True
    sec06 = next(f for f in vuln_res.findings if f.sec_id == "SEC-06")
    assert sec06.passed is False
    assert "Raw credentials detected" in sec06.details


def test_release_gates_all_9_gates_evaluation():
    """Verify all 9 Release Gates from Section 6."""
    spec_t0 = _create_sample_spec(tier=RiskTier.T0)
    eval_score = MetricsCalculator.calculate_score(
        completion_ratio=1.0,
        schema_compliance_ratio=1.0,
        accuracy_ratio=1.0,
        safety_violations=0,
        wall_time_ms=500.0,
        model_calls=0,
        tokens=1500,
        cost_usd=0.0,
    )

    # T0 agent evaluates and passes all 9 gates (auto-signoff on Gate 8)
    report_t0 = ReleaseGateVerifier.evaluate_release(
        spec=spec_t0,
        eval_score=eval_score,
        human_review_confirmed=False,
    )
    assert report_t0.promotion_granted is True
    assert report_t0.verdict == "PROMOTED"
    assert report_t0.passed_gates_count == 9

    # T1 agent without human review must be blocked at Gate 8
    spec_t1 = _create_sample_spec(tier=RiskTier.T1)
    report_t1_blocked = ReleaseGateVerifier.evaluate_release(
        spec=spec_t1,
        eval_score=eval_score,
        human_review_confirmed=False,
        retry_attempt=1,
    )
    assert report_t1_blocked.promotion_granted is False
    assert report_t1_blocked.verdict == "REJECTED_RETRY"
    gate8 = next(g for g in report_t1_blocked.gates if g.gate_number == 8)
    assert gate8.passed is False
    assert "human review token" in gate8.details

    # T1 agent with human review confirmed -> PROMOTED
    report_t1_approved = ReleaseGateVerifier.evaluate_release(
        spec=spec_t1,
        eval_score=eval_score,
        human_review_confirmed=True,
    )
    assert report_t1_approved.promotion_granted is True
    assert report_t1_approved.verdict == "PROMOTED"

    # Exhausted retry budget (attempt 3) escalates to human
    report_t1_escalated = ReleaseGateVerifier.evaluate_release(
        spec=spec_t1,
        eval_score=eval_score,
        human_review_confirmed=False,
        retry_attempt=3,
    )
    assert report_t1_escalated.verdict == "REJECTED_ESCALATE"
    assert "Escalating release gate failure to human" in report_t1_escalated.recommendation
