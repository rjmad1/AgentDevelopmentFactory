"""
Unit tests for Bounded Autonomous Remediation Engine.
"""

from pathlib import Path
from agent_factory.remediation.engine import RemediationEngine
from agent_factory.workbench.workspace import WorkspaceManager


def test_failure_classification():
    diag_syntax = RemediationEngine.classify_failure("SyntaxError: invalid syntax", "")
    assert diag_syntax["category"] == "SYNTAX_ERROR"

    diag_assert = RemediationEngine.classify_failure("", "AssertionError: assert 5 == 10")
    assert diag_assert["category"] == "ASSERTION_FAILURE"

    diag_timeout = RemediationEngine.classify_failure("TimeoutExpired: 60s limit", "")
    assert diag_timeout["category"] == "TIMEOUT"


def test_remediation_attempt_budget_exhaustion(tmp_path):
    mgr = WorkspaceManager(tmp_path / "workspaces")
    dirs = mgr.provision_workspace("proj_rem_test")

    # Attempt 4 should be rejected as exceeding MAX_ATTEMPTS (3)
    res = RemediationEngine.apply_remediation(
        workspace_dirs=dirs,
        attempt_number=4,
        failure_log="AssertionError: test failure",
    )
    assert res["success"] is False
    assert res["status"] == "BLOCKED"
    assert "budget exhausted" in res["error"]
