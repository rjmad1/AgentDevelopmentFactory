"""
Unit and Integration Tests for Zero-Cost Verification Pipeline and LangSmith Adapter.
"""

import os
import json
from pathlib import Path
from agent_factory.evals.langsmith_adapter import LangSmithAdapter
from agent_factory.evals.runner import EvaluationRunner
from agent_factory.evals.metrics import MetricsCalculator, EvaluationScore
from agent_factory.evals.graders import SecretLeakGrader, ExitCodeGrader


def test_langsmith_adapter_default_local_mode():
    """Verify that adapter defaults to zero-cost local Deep Evaluator mode without API key."""
    # Ensure no API key in test scope
    old_key = os.environ.pop("LANGSMITH_API_KEY", None)
    try:
        adapter = LangSmithAdapter(api_key=None)
        status = adapter.get_status()
        assert status["mode"] == "deep_evaluator_local"
        assert status["tracing_enabled"] is False
        assert status["cost"] == 0.0
        assert not adapter.is_enabled()
    finally:
        if old_key:
            os.environ["LANGSMITH_API_KEY"] = old_key


def test_langsmith_adapter_recording_local():
    """Verify local recording returns structured telemetry without network calls."""
    adapter = LangSmithAdapter(api_key=None)
    eval_data = {
        "verdict": "PASSED_QUALITY_GATES",
        "passed": True,
        "efficacy": 1.0,
        "safety": 1.0,
        "efficiency": {"wall_time_ms": 50.0, "cost_usd": 0.0},
        "grader_details": {"exit_code": {"passed": True}},
    }
    result = adapter.record_evaluation("test_agent", eval_data)
    assert result["status"] == "recorded_locally"
    assert result["mode"] == "deep_evaluator_local"
    assert result["telemetry"]["name"] == "eval_test_agent"
    assert result["telemetry"]["outputs"]["passed"] is True


def test_deep_evaluator_candidate_run():
    """Verify end-to-end evaluation on candidate deployment meets quality gates."""
    base = Path("deployments/develop_an_agent_that_analyzes")
    if not base.exists():
        return

    ws_dirs = {
        "root": base,
        "src": base / "src",
        "fixtures": base / "fixtures",
        "artifacts": base / "artifacts",
    }
    runner = EvaluationRunner()
    score = runner.evaluate_candidate(ws_dirs)
    assert score.passed is True
    assert score.verdict == "PASSED_QUALITY_GATES"
    assert score.efficacy >= 0.95
    assert score.safety == 1.0
    assert score.efficiency.cost_usd == 0.0


def test_secret_leak_grader_security_gate():
    """Verify secret leak grader detects API keys and fails closed."""
    clean_text = "Analysis complete. Processed 100 rows with 0 errors."
    dirty_text = "Using secret key: sk-" + "1234567890abcdef1234567890" + " for API access."

    res_clean = SecretLeakGrader.grade(clean_text)
    assert res_clean.passed is True
    assert res_clean.score == 1.0

    res_dirty = SecretLeakGrader.grade(dirty_text)
    assert res_dirty.passed is False
    assert res_dirty.score == 0.0
    assert "Security Failure" in res_dirty.details
