"""
Risk-Based Approval Gate and Anti-Forgery Token Verifier.
"""

import hmac
import hashlib
from typing import Optional
from pydantic import BaseModel
from agent_factory.specs.schema import RiskClassification


class ApprovalRecord(BaseModel):
    project_id: str
    agent_id: str
    action_scope: str
    risk_level: RiskClassification
    approver: str
    token: str
    timestamp: str


class ApprovalGate:
    """Enforces human-in-the-loop gates for medium/high-risk releases and elevated permissions."""

    # Internal master secret used for local token verification (in memory or host-scoped)
    _SECRET_SALT = b"Antigravity2.0_Hermes_Factory_Salt_20261103"

    @classmethod
    def generate_owner_token(cls, project_id: str, action_scope: str) -> str:
        """Generates an HMAC-signed owner approval token."""
        message = f"{project_id}:{action_scope}".encode("utf-8")
        sig = hmac.new(cls._SECRET_SALT, message, hashlib.sha256).hexdigest()[:16]
        return f"OWNER_APPROVED_{sig}"

    @classmethod
    def verify_token(cls, token: Optional[str], project_id: str, action_scope: str, risk: RiskClassification) -> bool:
        """
        Validates approval token against risk level.
        LOW risk allows AUTO_APPROVED_LOW_RISK tokens.
        MEDIUM / HIGH risk strictly requires a valid cryptographic owner token.
        """
        if risk == RiskClassification.LOW:
            if token and (token.startswith("AUTO_APPROVED_") or token.startswith("OWNER_APPROVED_")):
                return True
            return False

        # Medium and High Risk require valid HMAC signature
        if not token or not token.startswith("OWNER_APPROVED_"):
            return False

        expected_token = cls.generate_owner_token(project_id, action_scope)
        return hmac.compare_digest(token, expected_token)
