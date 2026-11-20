"""
Unit tests for Evaluation Graders, Metrics, and Evaluation Suite Runner.
"""

from pathlib import Path
from agent_factory.evals.graders import (
    FileExistenceGrader,
    ByteSizeGrader,
    JsonStructureGrader,
    MarkdownStructureGrader,
    SecretLeakGrader,
    ExitCodeGrader,
)
from agent_factory.evals.metrics import MetricsCalculator


def test_graders_and_metrics(tmp_path):
    # File existence & size
    test_file = tmp_path / "output.txt"
    test_file.write_text("Valid content for testing", encoding="utf-8")

    assert FileExistenceGrader.grade(test_file).passed is True
    assert ByteSizeGrader.grade(test_file, min_bytes=5).passed is True
    assert ByteSizeGrader.grade(test_file, min_bytes=1000).passed is False

    # JSON Structure
    json_file = tmp_path / "data.json"
    json_file.write_text('{"name": "test", "status": "ok"}', encoding="utf-8")
    assert JsonStructureGrader.grade(json_file, ["name", "status"]).passed is True
    assert JsonStructureGrader.grade(json_file, ["name", "missing_key"]).passed is False

    # Secret leak
    assert SecretLeakGrader.grade("Safe public log without keys").passed is True
    assert SecretLeakGrader.grade("Leaked key: sk-abcdef1234567890abcdef1234567890").passed is False

    # Exit code
    assert ExitCodeGrader.grade(0).passed is True
    assert ExitCodeGrader.grade(1).passed is False

    # Metrics calculation
    score = MetricsCalculator.calculate_score(
        completion_ratio=1.0,
        schema_compliance_ratio=1.0,
        accuracy_ratio=1.0,
        safety_violations=0,
        wall_time_ms=150.0,
    )
    assert score.passed is True
    assert score.efficacy == 1.0
    assert score.safety == 1.0
    assert score.verdict == "PASSED_QUALITY_GATES"
