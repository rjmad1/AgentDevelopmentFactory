"""
Factory Control Plane Orchestration Engine and State Machine.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
import json

from agent_factory.control_plane.task_ledger import TaskLedger
from agent_factory.specs.schema import UniversalAgentSpec, RiskClassification
from agent_factory.specs.validator import SpecValidator
from agent_factory.security.approval_gate import ApprovalGate


class FactoryStage(str, Enum):
    INTAKE = "INTAKE"
    SPEC_DRAFT = "SPEC_DRAFT"
    SPEC_REVIEW = "SPEC_REVIEW"
    BUILD = "BUILD"
    TEST = "TEST"
    EVALUATE = "EVALUATE"
    REMEDIATE = "REMEDIATE"
    PACKAGE = "PACKAGE"
    RELEASE = "RELEASE"
    OPERATION = "OPERATION"
    RETIRED = "RETIRED"


class StageTransitionResult(Exception):
    pass


class FactoryOrchestrator:
    """Coordinates lifecycle progression, state checkpoints, and approval gates."""

    STAGE_ORDER = [
        FactoryStage.INTAKE,
        FactoryStage.SPEC_DRAFT,
        FactoryStage.SPEC_REVIEW,
        FactoryStage.BUILD,
        FactoryStage.TEST,
        FactoryStage.EVALUATE,
        FactoryStage.PACKAGE,
        FactoryStage.RELEASE,
        FactoryStage.OPERATION,
    ]

    def __init__(self, workspace_root: Path, ledger: TaskLedger):
        self.workspace_root = Path(workspace_root)
        self.ledger = ledger
        self.validator = SpecValidator()

    def advance_stage(
        self,
        project_id: str,
        current_stage: FactoryStage,
        spec: UniversalAgentSpec,
        risk: RiskClassification,
        stage_artifacts: Optional[Dict[str, Any]] = None,
        approval_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validates exit criteria for current stage and advances to the next stage."""
        idx = self.STAGE_ORDER.index(current_stage)
        next_stage = self.STAGE_ORDER[idx + 1] if idx + 1 < len(self.STAGE_ORDER) else current_stage

        # Verify Stage-Specific Gate Invariants
        if current_stage == FactoryStage.SPEC_REVIEW:
            val_res = self.validator.validate_spec(spec.model_dump(mode="json"), approval_token=approval_token)
            if not val_res.is_valid:
                error_msg = f"Spec Review Failed: {'; '.join(val_res.errors)}"
                self.ledger.record_task(
                    task_id=f"{project_id}_{current_stage.value}",
                    project_id=project_id,
                    stage=current_stage.value,
                    status="BLOCKED",
                    error_message=error_msg,
                )
                return {"success": False, "stage": current_stage.value, "error": error_msg}

        elif current_stage == FactoryStage.EVALUATE:
            # Check Evaluation Verdict
            if stage_artifacts and not stage_artifacts.get("eval_passed", False):
                error_msg = "Evaluation gate failed: Score did not satisfy minimum thresholds."
                self.ledger.record_task(
                    task_id=f"{project_id}_{current_stage.value}",
                    project_id=project_id,
                    stage=current_stage.value,
                    status="FAILED",
                    error_message=error_msg,
                )
                return {"success": False, "stage": current_stage.value, "error": error_msg, "trigger_remediation": True}

        elif current_stage == FactoryStage.PACKAGE:
            # Approval Gate Check
            is_approved = ApprovalGate.verify_token(approval_token, project_id, "RELEASE_PROMOTION", risk)
            if not is_approved:
                error_msg = f"Release Gate Blocked: Project requires valid approval token for risk '{risk.value}'."
                self.ledger.record_task(
                    task_id=f"{project_id}_{current_stage.value}",
                    project_id=project_id,
                    stage=current_stage.value,
                    status="BLOCKED",
                    error_message=error_msg,
                )
                return {"success": False, "stage": current_stage.value, "error": error_msg}

        # Calculate artifact digest if present
        output_hash = None
        if stage_artifacts:
            serialized = json.dumps(stage_artifacts, sort_keys=True).encode("utf-8")
            output_hash = hashlib.sha256(serialized).hexdigest()

        # Record successful completion of current stage
        self.ledger.record_task(
            task_id=f"{project_id}_{current_stage.value}",
            project_id=project_id,
            stage=current_stage.value,
            status="COMPLETED",
            output_hash=output_hash,
        )

        # Transition to next stage
        self.ledger.record_task(
            task_id=f"{project_id}_{next_stage.value}",
            project_id=project_id,
            stage=next_stage.value,
            status="QUEUED",
        )

        return {
            "success": True,
            "previous_stage": current_stage.value,
            "current_stage": next_stage.value,
            "output_hash": output_hash,
        }
