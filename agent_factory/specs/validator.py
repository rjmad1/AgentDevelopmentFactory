"""
Semantic and Syntactic Spec Validator for Universal Agent Specifications.
"""

import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import jsonschema

from agent_factory.specs.schema import (
    UniversalAgentSpec,
    EffectLevel,
    get_json_schema,
)


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    normalized_spec: Optional[UniversalAgentSpec] = None


class SpecValidator:
    """Performs deep syntactic and semantic validation on agent specifications."""

    # Patterns indicating raw API keys leaked into config
    RAW_SECRET_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
        re.compile(r"Bearer\s+[a-zA-Z0-9\._\-]{20,}", re.IGNORECASE),
        re.compile(r"[a-f0-9]{32,64}", re.IGNORECASE),
    ]

    def validate_spec(
        self,
        raw_data: Dict[str, Any],
        approval_token: Optional[str] = None,
        available_tools: Optional[List[str]] = None,
    ) -> ValidationResult:
        errors = []
        warnings = []

        # 1. Syntactic JSON Schema Validation
        try:
            schema = get_json_schema()
            jsonschema.validate(instance=raw_data, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"JSON Schema validation error at {list(e.path)}: {e.message}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # 2. Pydantic Model Instantiation
        try:
            spec = UniversalAgentSpec(**raw_data)
        except Exception as e:
            errors.append(f"Pydantic instantiation error: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # 3. Secret Leakage Check
        secrets_field = spec.policy.secrets
        if isinstance(secrets_field, list):
            secret_candidates = secrets_field
        elif isinstance(secrets_field, str) and secrets_field.lower() != "none":
            secret_candidates = [secrets_field]
        else:
            secret_candidates = []

        for candidate in secret_candidates:
            for pattern in self.RAW_SECRET_PATTERNS:
                if pattern.search(candidate):
                    errors.append(
                        f"Security Violation: Raw secret detected in policy.secrets ('{candidate[:6]}...'). "
                        "Only named references (e.g. 'OMNIROUTE_API_KEY_REF') are permitted."
                    )

        # 4. Authority & Permission Boundary Checks
        high_risk_effects = {EffectLevel.CHANGE_ACCOUNT, EffectLevel.SEND_PUBLISH, EffectLevel.SPEND_DELETE}
        requested_high_risk = [e for e in spec.policy.permitted_effects if e in high_risk_effects]

        if requested_high_risk:
            if not approval_token:
                errors.append(
                    f"Policy Denial: Agent requests elevated effects {requested_high_risk} "
                    "without an authorized human approval token."
                )
            elif not approval_token.startswith("OWNER_APPROVED_"):
                errors.append(
                    f"Policy Denial: Invalid approval token '{approval_token}'. "
                    "Must be an authorized owner token for elevated permissions."
                )

        # 5. Budgetary Ceiling Check
        if spec.limits.paid_spend_ceiling > 0.0:
            if not approval_token:
                errors.append(
                    f"Budget Violation: paid_spend_ceiling is ${spec.limits.paid_spend_ceiling:.2f}. "
                    "Paid model usage requires explicit owner approval under the Free-First rule."
                )

        # 6. Tool Allowlist Validation
        if available_tools is not None:
            for tool in spec.policy.permitted_tools:
                if tool not in available_tools:
                    warnings.append(
                        f"Unresolved Tool Dependency: Tool '{tool}' is not currently active in the Capability Registry."
                    )

        # 7. Step & Timeout Quota Checks
        if spec.limits.max_wall_time_seconds > 600 and not approval_token:
            warnings.append(
                f"Long-Horizon Task: max_wall_time_seconds is {spec.limits.max_wall_time_seconds}s (>10m). "
                "Ensure checkpoints are configured."
            )

        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            normalized_spec=spec if is_valid else None,
        )
