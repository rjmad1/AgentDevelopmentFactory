"""
Unit Tests for Sandboxed Execution Runtime and Automated Red Teaming Suite.
Verifies hermetic process isolation, AST quarantine pre-execution gating,
filesystem containment, and continuous adversarial prompt injection stress testing.
"""

import os
import sys
import pytest
from pathlib import Path

from agent_factory.runtime.sandbox import SandboxedLocalProcessRuntime, SandboxConfig
from agent_factory.runtime.base import ExecutionLimits
from agent_factory.security.red_team import RedTeamHarness, AttackCategory, RedTeamProbe
from agent_factory.guardrails.nemo_nist import RailType
from agent_factory.specs.schema import (
    UniversalAgentSpec,
    RiskTier,
    EffectLevel,
    InputParameter,
    OutputParameter,
    PolicySpec,
    LimitsSpec,
    AcceptanceSpec,
)


def _create_test_spec(tier: RiskTier = RiskTier.T0) -> UniversalAgentSpec:
    return UniversalAgentSpec(
        schema_version=1,
        agent_id="sandboxed_agent",
        version="1.0.0",
        owner="SecurityLead",
        risk_tier=tier,
        purpose="Analyze tabular data in sandboxed environment without external network access.",
        inputs={"input_data": InputParameter(type="string", description="Dataset path")},
        outputs={"report": OutputParameter(type="file", path="artifacts/report.md")},
        policy=PolicySpec(
            permitted_tools=["read_local_csv", "compute_statistics", "write_workspace_artifact"],
            permitted_effects=[EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT],
        ),
        limits=LimitsSpec(max_steps=20, paid_spend_ceiling=0.0),
        acceptance=AcceptanceSpec(suite="evals/standard", minimum_efficacy=0.95, minimum_safety=1.0),
    )


# =========================================================================
# Sandboxed Runtime Tests
# =========================================================================

def test_sandbox_fs_containment_blocks_escape(tmp_path):
    """Verify sandbox rejects executing scripts outside workspace root."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    outside_script = outside_dir / "evil.py"
    outside_script.write_text("print('hacked')")

    runtime = SandboxedLocalProcessRuntime()
    limits = ExecutionLimits(max_wall_time_seconds=5)

    res = runtime.execute(outside_script, [], limits, ws)
    assert res.success is False
    assert res.exit_code == 126
    assert "SANDBOX_CONTAINMENT_VIOLATION" in res.stderr


def test_sandbox_ast_quarantine_blocks_prohibited_builtins(tmp_path):
    """Verify sandbox rejects scripts with eval/exec/os.system before spawning subprocess."""
    ws = tmp_path / "workspace"
    src_dir = ws / "src"
    src_dir.mkdir(parents=True)
    dangerous_script = src_dir / "bad_agent.py"
    dangerous_script.write_text("import os\neval('os.system(\"calc\")')\n")

    runtime = SandboxedLocalProcessRuntime()
    limits = ExecutionLimits(max_wall_time_seconds=5)

    res = runtime.execute(dangerous_script, [], limits, ws)
    assert res.success is False
    assert res.exit_code == 126
    assert "AST_QUARANTINE_REJECTED" in res.stderr
    assert "Dangerous dynamic call" in res.stderr


def test_sandbox_network_isolation_and_env_stripping(tmp_path):
    """Verify sandbox strips credentials and injects offline network proxies."""
    ws = tmp_path / "workspace"
    ws.mkdir()

    # Set mock sensitive environment variables on host
    os.environ["OPENAI_API_KEY"] = "sk-testsecretkey12345"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "mock_secret_aws_key"

    runtime = SandboxedLocalProcessRuntime()
    env = runtime._prepare_sandboxed_env(ws)

    # Assert stripped
    assert "OPENAI_API_KEY" not in env
    assert "AWS_SECRET_ACCESS_KEY" not in env

    # Assert network isolation proxy
    assert env.get("HTTP_PROXY") == "http://127.0.0.1:0"
    assert env.get("HTTPS_PROXY") == "http://127.0.0.1:0"
    assert env.get("PYTHONDONTWRITEBYTECODE") == "1"


def test_sandbox_legitimate_execution_success(tmp_path):
    """Verify clean agent script executes safely inside sandbox and creates artifacts."""
    ws = tmp_path / "workspace"
    src_dir = ws / "src"
    src_dir.mkdir(parents=True)

    clean_script = src_dir / "agent.py"
    clean_code = """
import sys
from pathlib import Path

art_dir = Path("artifacts")
art_dir.mkdir(parents=True, exist_ok=True)
with open(art_dir / "report.md", "w") as f:
    f.write("# Clean Sandboxed Execution Report\\nSuccess")

print("SANDBOX_EXECUTION_COMPLETED")
"""
    clean_script.write_text(clean_code)

    runtime = SandboxedLocalProcessRuntime()
    limits = ExecutionLimits(max_wall_time_seconds=10)

    res = runtime.execute(clean_script, [], limits, ws)
    assert res.success is True
    assert res.exit_code == 0
    assert "SANDBOX_EXECUTION_COMPLETED" in res.stdout
    assert "report.md" in res.artifacts_created


# =========================================================================
# Red Team Harness & Adversarial Stress Tests
# =========================================================================

def test_red_team_harness_evaluates_all_attack_categories(tmp_path):
    """Verify red teaming suite executes probes across all 5 attack categories."""
    spec = _create_test_spec(tier=RiskTier.T0)
    report = RedTeamHarness.run_suite(spec, tmp_path)

    assert report.total_probes == 16
    assert report.blocked_probes == 16
    assert report.bypassed_probes == 0
    assert report.block_rate_percentage == 100.0
    assert report.verdict == "PASS / HARDENED"

    categories_tested = {p.category for p in report.probes}
    assert AttackCategory.DIRECT_INJECTION.value in categories_tested
    assert AttackCategory.INDIRECT_INJECTION.value in categories_tested
    assert AttackCategory.OBFUSCATION_JAILBREAK.value in categories_tested
    assert AttackCategory.TOOL_MISUSE_AGENCY.value in categories_tested
    assert AttackCategory.SECRET_EXFILTRATION.value in categories_tested


def test_red_team_harness_catches_vulnerability(tmp_path):
    """Verify red team harness detects failure if a probe bypasses guardrails."""
    spec = _create_test_spec(tier=RiskTier.T0)
    # Craft a probe that deliberately does not match guardrails to test failure reporting
    mock_probe = RedTeamProbe(
        probe_id="MOCK-FAIL-01",
        category=AttackCategory.DIRECT_INJECTION,
        name="Benign Probe",
        description="A probe with normal text that does not trigger guardrail",
        attack_payload={"input_data": "Normal analytical task"},
        target_rail=RailType.INPUT_RAIL,
        expected_nist_control="MP-2.3",
        severity="CRITICAL",
    )

    res = RedTeamHarness.evaluate_probe(mock_probe, spec, tmp_path)
    assert res.blocked is False
    assert "Probe bypassed input guardrails" in res.details
