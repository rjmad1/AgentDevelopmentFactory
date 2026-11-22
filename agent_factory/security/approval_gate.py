"""
Risk-Based Approval Gate and Anti-Forgery Token Verifier.
"""

import os
import secrets
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

    _ephemeral_key: Optional[bytes] = None

    @classmethod
    def _get_master_key(cls) -> bytes:
        """
        Retrieves the cryptographic master key from environment variables (ADF_HMAC_MASTER_KEY).
        If unset, lazily initializes an ephemeral, cryptographically secure 256-bit process key.
        Completely eliminates hardcoded static cryptographic salts (CWE-321).
        """
        env_key = os.environ.get("ADF_HMAC_MASTER_KEY") or os.environ.get("ADF_HMAC_SECRET")
        if env_key:
            return env_key.encode("utf-8")
        if cls._ephemeral_key is None:
            cls._ephemeral_key = secrets.token_bytes(32)
        return cls._ephemeral_key

    @classmethod
    def generate_owner_token(cls, project_id: str, action_scope: str) -> str:
        """Generates an HMAC-signed owner approval token with full 256-bit cryptographic entropy."""
        message = f"{project_id}:{action_scope}".encode("utf-8")
        sig = hmac.new(cls._get_master_key(), message, hashlib.sha256).hexdigest()
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
