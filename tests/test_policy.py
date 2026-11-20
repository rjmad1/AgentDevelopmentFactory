"""
Unit tests for Policy Enforcement, Boundary Defense, and Path Security.
"""

import pytest
from pathlib import Path
from agent_factory.security.policy import PolicyEnforcer, PolicyViolationError
from agent_factory.specs.schema import PolicySpec, LimitsSpec, EffectLevel


def test_path_boundary_enforcement(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    inside_file = ws / "artifacts" / "report.md"

    outside_file = tmp_path / "system32" / "hacked.txt"

    policy = PolicySpec(
        permitted_effects=[EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT],
        permitted_tools=["write_artifact"],
    )
    limits = LimitsSpec(paid_spend_ceiling=0.0)
    enforcer = PolicyEnforcer(ws, policy, limits)

    # Valid write inside workspace
    valid_p = enforcer.validate_path_access(inside_file, write=True)
    assert str(valid_p).startswith(str(ws.resolve()))

    # Unauthorized write outside workspace must fail
    with pytest.raises(PolicyViolationError, match="Security Boundary Violation"):
        enforcer.validate_path_access(outside_file, write=True)


def test_tool_effect_level_enforcement(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    policy = PolicySpec(
        permitted_tools=["read_data"],
        permitted_effects=[EffectLevel.READ_PUBLIC],
    )
    limits = LimitsSpec()
    enforcer = PolicyEnforcer(ws, policy, limits)

    # Valid tool invocation
    enforcer.validate_tool_invocation("read_data", EffectLevel.READ_PUBLIC)

    # Unlisted tool invocation fails
    with pytest.raises(PolicyViolationError, match="not in the permitted tools allowlist"):
        enforcer.validate_tool_invocation("unauthorized_tool", EffectLevel.READ_PUBLIC)

    # Exceeding effect level fails
    with pytest.raises(PolicyViolationError, match="exceeds permitted effects"):
        enforcer.validate_tool_invocation("read_data", EffectLevel.SPEND_DELETE)


def test_budget_spend_ceiling_enforcement(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    policy = PolicySpec()
    limits = LimitsSpec(paid_spend_ceiling=0.0)
    enforcer = PolicyEnforcer(ws, policy, limits)

    # Free spend succeeds
    enforcer.validate_spending(0.0, 0.0)

    # Additional spend above ceiling fails
    with pytest.raises(PolicyViolationError, match="Budget Ceiling Exceeded"):
        enforcer.validate_spending(0.0, 0.05)
