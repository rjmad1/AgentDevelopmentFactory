"""
Universal Agent Specification Standard - Pydantic Schema and Validation Models.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml
from pydantic import BaseModel, Field, field_validator


class EffectLevel(str, Enum):
    READ_PUBLIC = "READ_PUBLIC"
    READ_PRIVATE = "READ_PRIVATE"
    WRITE_LOCAL_DRAFT = "WRITE_LOCAL_DRAFT"
    CHANGE_ACCOUNT = "CHANGE_ACCOUNT"
    SEND_PUBLISH = "SEND_PUBLISH"
    SPEND_DELETE = "SPEND_DELETE"


class RiskClassification(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DenialAction(str, Enum):
    STOP_AND_REPORT = "stop_and_report"
    QUARANTINE = "quarantine"
    HUMAN_ESCALATE = "human_escalate"


class InputParameter(BaseModel):
    type: str = Field(..., description="Data type: string, integer, float, boolean, list, object, file")
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None


class OutputParameter(BaseModel):
    type: str = Field(..., description="Data type: file, markdown, json, text")
    format: Optional[str] = None
    path: Optional[str] = None
    description: Optional[str] = None


class PolicySpec(BaseModel):
    mode: str = Field("draft_only", description="Operating mode: draft_only, read_only, full_autonomous")
    data_classification: str = Field("public_or_synthetic", description="Data sensitivity tier")
    permitted_tools: List[str] = Field(default_factory=list, description="Allowlist of tool IDs")
    permitted_effects: List[EffectLevel] = Field(default_factory=list, description="Permitted authority boundaries")
    secrets: Union[str, List[str]] = Field("none", description="Named secret references only; never raw secrets")
    on_denial: DenialAction = Field(DenialAction.STOP_AND_REPORT, description="Action taken when a tool/guard denies access")


class LimitsSpec(BaseModel):
    max_steps: int = Field(20, ge=1, le=200, description="Maximum agent execution steps")
    max_wall_time_seconds: int = Field(60, ge=5, le=3600, description="Execution timeout in seconds")
    max_tokens: int = Field(8000, ge=100, le=128000, description="Maximum tokens per run")
    paid_spend_ceiling: float = Field(0.0, ge=0.0, description="Ceiling for paid external API spend ($0 = free only)")
    max_parallel_workers: int = Field(1, ge=1, le=16, description="Parallel worker limit")


class StateSpec(BaseModel):
    durable_fields: List[str] = Field(default_factory=lambda: ["request_id", "stage", "evidence_refs"])


class AcceptanceSpec(BaseModel):
    suite: str = Field(..., description="Evaluation benchmark suite path or ID")
    required_checks: List[str] = Field(default_factory=list, description="Mandatory quality checks")
    minimum_efficacy: float = Field(0.95, ge=0.0, le=1.0)
    minimum_safety: float = Field(1.00, ge=1.0, le=1.0, description="Safety must always be 1.0 (zero tolerance)")


class UniversalAgentSpec(BaseModel):
    schema_version: int = Field(1, description="Specification schema version")
    agent_id: str = Field(..., description="Unique machine-readable agent identifier")
    version: str = Field("1.0.0", description="Semantic version string")
    owner: str = Field("Admin", description="Owner or stakeholder name")
    purpose: str = Field(..., min_length=10, description="Clear statement of agent objective")
    inputs: Dict[str, InputParameter] = Field(default_factory=dict)
    outputs: Dict[str, OutputParameter] = Field(default_factory=dict)
    policy: PolicySpec = Field(default_factory=PolicySpec)
    limits: LimitsSpec = Field(default_factory=LimitsSpec)
    state: StateSpec = Field(default_factory=StateSpec)
    acceptance: AcceptanceSpec
    targets: Dict[str, str] = Field(
        default_factory=lambda: {"local_process": "candidate", "hermes": "candidate"}
    )

    @field_validator("schema_version")
    def validate_schema_version(cls, v: int) -> int:
        if v != 1:
            raise ValueError(f"Unsupported schema_version: {v}. Factory supports schema_version 1.")
        return v


def load_spec_from_yaml(path: Union[str, Path]) -> UniversalAgentSpec:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Spec file not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return UniversalAgentSpec(**data)


def save_spec_to_yaml(spec: UniversalAgentSpec, path: Union[str, Path]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(spec.model_dump(mode="json"), f, sort_keys=False)
    return p


def get_json_schema() -> Dict[str, Any]:
    return UniversalAgentSpec.model_json_schema()
