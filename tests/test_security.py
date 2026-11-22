"""
Unit tests for Secret Redaction, Approval Tokens, and Skill Quarantine.
"""

from agent_factory.security.redactor import SecretRedactor
from agent_factory.security.approval_gate import ApprovalGate
from agent_factory.security.quarantine import SkillQuarantine
from agent_factory.specs.schema import RiskClassification


def test_secret_redaction():
    text_with_keys = (
        "Here is the key: sk-1234567890abcdef1234567890 and AWS: AKIAIOSFODNN7EXAMPLE "
        "and header Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz"
    )
    clean = SecretRedactor.redact_text(text_with_keys)

    assert "sk-1234567890" not in clean
    assert "[REDACTED_API_KEY]" in clean
    assert "AKIAIOSFODNN7EXAMPLE" not in clean
    assert "[REDACTED_AWS_KEY]" in clean
    assert "Bearer [REDACTED_TOKEN]" in clean


def test_approval_gate_validation(monkeypatch):
    project_id = "proj_test_123"
    action = "RELEASE_PROMOTION"

    # Low risk allows AUTO_APPROVED
    assert ApprovalGate.verify_token("AUTO_APPROVED_LOW_RISK", project_id, action, RiskClassification.LOW) is True

    # High risk rejects AUTO_APPROVED
    assert ApprovalGate.verify_token("AUTO_APPROVED_LOW_RISK", project_id, action, RiskClassification.HIGH) is False

    # High risk rejects fake or forged token
    assert ApprovalGate.verify_token("OWNER_APPROVED_fake_sig", project_id, action, RiskClassification.HIGH) is False

    # High risk succeeds with authentic cryptographic token
    valid_token = ApprovalGate.generate_owner_token(project_id, action)
    assert ApprovalGate.verify_token(valid_token, project_id, action, RiskClassification.HIGH) is True

    # Cryptographic entropy check: signature must be full 64-char SHA256 hex digest (256 bits)
    sig_hex = valid_token.replace("OWNER_APPROVED_", "")
    assert len(sig_hex) == 64, f"Expected 64-char hex digest, got {len(sig_hex)}"

    # Cryptographic key isolation test: token generated with key_A must be rejected under key_B
    monkeypatch.setenv("ADF_HMAC_MASTER_KEY", "master_key_alpha_9999")
    token_a = ApprovalGate.generate_owner_token(project_id, action)
    assert ApprovalGate.verify_token(token_a, project_id, action, RiskClassification.HIGH) is True

    monkeypatch.setenv("ADF_HMAC_MASTER_KEY", "master_key_beta_8888")
    assert ApprovalGate.verify_token(token_a, project_id, action, RiskClassification.HIGH) is False


def test_skill_quarantine_ast_audit():
    safe_code = """
import math
import csv

def process(x):
    return math.sqrt(x)
"""
    findings_safe = SkillQuarantine.audit_python_source(safe_code)
    assert len(findings_safe) == 0

    dangerous_code = """
import os
import ctypes

def exploit():
    os.system("calc.exe")
    eval("1+1")
"""
    findings_bad = SkillQuarantine.audit_python_source(dangerous_code)
    assert len(findings_bad) >= 3
    assert any("Prohibited module import: 'ctypes'" in f for f in findings_bad)
    assert any("Prohibited direct shell call: 'os.system()'" in f for f in findings_bad)
    assert any("Dangerous dynamic call: 'eval()'" in f for f in findings_bad)
