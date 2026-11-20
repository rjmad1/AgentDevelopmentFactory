"""
Request Intake and Requirements Decomposition Engine.
"""

import re
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel

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
)


class IntakeResult(BaseModel):
    project_id: str
    agent_id: str
    risk_level: RiskClassification
    spec: UniversalAgentSpec


class RequestIntake:
    """Decomposes raw user requests into validated Universal Agent Specifications."""

    @classmethod
    def process_request(
        cls,
        prompt: str,
        owner: str = "Admin",
        forced_risk: Optional[RiskClassification] = None,
    ) -> IntakeResult:
        # Determine slug and identifiers
        slug_match = re.sub(r"[^a-zA-Z0-9_]+", "_", prompt.lower()[:30]).strip("_")
        agent_id = slug_match if slug_match else f"agent_{uuid.uuid4().hex[:8]}"
        project_id = f"proj_{uuid.uuid4().hex[:10]}"

        # Risk Classification Heuristics
        lower_prompt = prompt.lower()
        if forced_risk:
            risk = forced_risk
        elif any(k in lower_prompt for k in ["delete", "spend", "money", "payment", "publish", "send email", "telegram"]):
            risk = RiskClassification.HIGH
        elif any(k in lower_prompt for k in ["private", "modify", "database", "write remote"]):
            risk = RiskClassification.MEDIUM
        else:
            risk = RiskClassification.LOW

        # Define policy permissions based on risk
        permitted_effects = [EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT]
        if risk == RiskClassification.MEDIUM:
            permitted_effects.append(EffectLevel.READ_PRIVATE)

        spec = UniversalAgentSpec(
            schema_version=1,
            agent_id=agent_id,
            version="1.0.0",
            owner=owner,
            purpose=prompt.strip(),
            inputs={
                "input_data": InputParameter(
                    type="string",
                    description="Path to target input dataset or parameters",
                    required=True,
                )
            },
            outputs={
                "report": OutputParameter(
                    type="file",
                    format="markdown",
                    path="artifacts/report.md",
                    description="Primary operational report",
                ),
                "summary": OutputParameter(
                    type="file",
                    format="json",
                    path="artifacts/summary.json",
                    description="Structured outcome ledger",
                ),
            },
            policy=PolicySpec(
                mode="draft_only",
                data_classification="public_or_synthetic",
                permitted_tools=["read_local_csv", "compute_statistics", "write_workspace_artifact"],
                permitted_effects=permitted_effects,
                secrets="none",
            ),
            limits=LimitsSpec(
                max_steps=20,
                max_wall_time_seconds=60,
                paid_spend_ceiling=0.0,
                max_parallel_workers=1,
            ),
            state=StateSpec(durable_fields=["project_id", "stage", "evidence_refs"]),
            acceptance=AcceptanceSpec(
                suite="evals/standard_pack",
                required_checks=["functional_correctness", "schema_compliance", "zero_unauthorized_effects"],
                minimum_efficacy=0.95,
                minimum_safety=1.00,
            ),
            targets={"local_process": "candidate", "hermes": "candidate"},
        )

        return IntakeResult(
            project_id=project_id,
            agent_id=agent_id,
            risk_level=risk,
            spec=spec,
        )
