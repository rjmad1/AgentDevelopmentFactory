"""
Unit tests for Universal Agent Specification Schema and Validator.
"""

import pytest
from pathlib import Path
from agent_factory.specs.schema import (
    UniversalAgentSpec,
    InputParameter,
    OutputParameter,
    PolicySpec,
    LimitsSpec,
    StateSpec,
    AcceptanceSpec,
    EffectLevel,
    RiskClassification,
    load_spec_from_yaml,
    save_spec_to_yaml,
)
from agent_factory.specs.validator import SpecValidator


def test_valid_agent_spec(tmp_path):
    spec = UniversalAgentSpec(
        schema_version=1,
        agent_id="test_agent",
        version="1.0.0",
        purpose="A valid test agent for data processing",
        inputs={"data": InputParameter(type="string", description="input data")},
        outputs={"report": OutputParameter(type="file", path="artifacts/report.md")},
        policy=PolicySpec(
            mode="draft_only",
            permitted_tools=["tool_a"],
            permitted_effects=[EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT],
        ),
        limits=LimitsSpec(max_steps=10, max_wall_time_seconds=30),
        state=StateSpec(durable_fields=["req_id"]),
        acceptance=AcceptanceSpec(suite="evals/test", required_checks=["check_1"]),
    )

    yaml_file = tmp_path / "agent.yaml"
    save_spec_to_yaml(spec, yaml_file)
    loaded = load_spec_from_yaml(yaml_file)

    assert loaded.agent_id == "test_agent"
    assert loaded.policy.permitted_effects == [EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT]

    validator = SpecValidator()
    res = validator.validate_spec(loaded.model_dump(mode="json"))
    assert res.is_valid is True
    assert len(res.errors) == 0


def test_reject_invalid_schema_version():
    with pytest.raises(ValueError, match="Unsupported schema_version: 2"):
        UniversalAgentSpec(
            schema_version=2,
            agent_id="invalid_agent",
            purpose="Should fail due to unsupported version",
            acceptance=AcceptanceSpec(suite="evals/test"),
        )


def test_validator_rejects_raw_secret():
    validator = SpecValidator()
    raw_spec = {
        "schema_version": 1,
        "agent_id": "leaky_agent",
        "version": "1.0.0",
        "owner": "Admin",
        "purpose": "Agent that leaks a raw secret in policy",
        "acceptance": {"suite": "evals/test"},
        "policy": {
            "secrets": ["sk-abcdef1234567890abcdef1234567890"],  # Raw secret
        },
    }

    res = validator.validate_spec(raw_spec)
    assert res.is_valid is False
    assert any("Security Violation: Raw secret detected" in err for err in res.errors)


def test_validator_enforces_approval_for_elevated_effects():
    validator = SpecValidator()
    raw_spec = {
        "schema_version": 1,
        "agent_id": "privileged_agent",
        "version": "1.0.0",
        "owner": "Admin",
        "purpose": "Agent requesting high-risk effect without token",
        "acceptance": {"suite": "evals/test"},
        "policy": {
            "permitted_effects": ["SPEND_DELETE"],
        },
    }

    # Should fail without approval token
    res = validator.validate_spec(raw_spec, approval_token=None)
    assert res.is_valid is False
    assert any("Policy Denial: Agent requests elevated effects" in err for err in res.errors)

    # Should succeed with valid owner approval token
    res_approved = validator.validate_spec(raw_spec, approval_token="OWNER_APPROVED_valid_token")
    assert res_approved.is_valid is True
