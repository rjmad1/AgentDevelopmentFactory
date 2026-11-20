"""
Unit tests for Control Plane: Task Ledger, Request Intake, and Orchestrator.
"""

from pathlib import Path
from agent_factory.control_plane.task_ledger import TaskLedger
from agent_factory.control_plane.intake import RequestIntake
from agent_factory.control_plane.orchestrator import FactoryOrchestrator, FactoryStage
from agent_factory.specs.schema import RiskClassification


def test_task_ledger_operations(tmp_path):
    db_file = tmp_path / "test_state.db"
    events_file = tmp_path / "test_events.jsonl"
    ledger = TaskLedger(db_file, events_file)

    task = ledger.record_task(
        task_id="t1",
        project_id="p1",
        stage="INTAKE",
        status="COMPLETED",
        output_hash="hash123",
    )
    assert task.status == "COMPLETED"

    # Query back from SQLite
    queried = ledger.get_task("t1")
    assert queried is not None
    assert queried.stage == "INTAKE"
    assert queried.output_hash == "hash123"

    # Event log exists and recorded event
    assert events_file.exists()
    assert "t1" in events_file.read_text(encoding="utf-8")


def test_request_intake_risk_heuristics():
    # Low risk
    res_low = RequestIntake.process_request("Analyze CSV files and produce a summary table")
    assert res_low.risk_level == RiskClassification.LOW
    assert res_low.spec.agent_id is not None

    # High risk
    res_high = RequestIntake.process_request("Execute payments and delete old database records")
    assert res_high.risk_level == RiskClassification.HIGH


def test_orchestrator_stage_advancement(tmp_path):
    db_file = tmp_path / "state.db"
    ledger = TaskLedger(db_file)
    orch = FactoryOrchestrator(tmp_path, ledger)

    intake_res = RequestIntake.process_request("Test data anomaly agent")
    p_id = intake_res.project_id

    # Advance from INTAKE -> SPEC_DRAFT
    res = orch.advance_stage(
        project_id=p_id,
        current_stage=FactoryStage.INTAKE,
        spec=intake_res.spec,
        risk=intake_res.risk_level,
    )
    assert res["success"] is True
    assert res["current_stage"] == "SPEC_DRAFT"

    # Verify task status in ledger
    t = ledger.get_task(f"{p_id}_INTAKE")
    assert t.status == "COMPLETED"
