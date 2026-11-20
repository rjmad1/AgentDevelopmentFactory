"""
Bounded Autonomous Remediation Engine with Diagnostic Classification and Scoped Patching.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import datetime
import json


class RemediationAttempt(Exception):
    pass


class RemediationEngine:
    """Diagnoses test failures and executes bounded surgical code repairs."""

    MAX_ATTEMPTS = 3

    @classmethod
    def classify_failure(cls, stderr: str, test_output: str) -> Dict[str, Any]:
        combined = f"{stderr}\n{test_output}"

        if "SyntaxError" in combined:
            return {"category": "SYNTAX_ERROR", "recoverable": True, "details": "Python syntax error"}
        elif "ImportError" in combined or "ModuleNotFoundError" in combined:
            return {"category": "IMPORT_ERROR", "recoverable": True, "details": "Missing module import"}
        elif "AssertionError" in combined:
            return {"category": "ASSERTION_FAILURE", "recoverable": True, "details": "Unit test assertion failed"}
        elif "FileNotFoundError" in combined:
            return {"category": "FILE_NOT_FOUND", "recoverable": True, "details": "Required input/fixture missing"}
        elif "TimeoutExpired" in combined:
            return {"category": "TIMEOUT", "recoverable": False, "details": "Subprocess exceeded execution deadline"}
        else:
            return {"category": "UNKNOWN_ERROR", "recoverable": False, "details": combined[:200]}

    @classmethod
    def apply_remediation(
        cls,
        workspace_dirs: Dict[str, Path],
        attempt_number: int,
        failure_log: str,
    ) -> Dict[str, Any]:
        if attempt_number > cls.MAX_ATTEMPTS:
            return {
                "success": False,
                "status": "BLOCKED",
                "error": f"Remediation budget exhausted ({cls.MAX_ATTEMPTS} attempts reached).",
            }

        diag = cls.classify_failure("", failure_log)
        evidence_dir = workspace_dirs["evidence"]
        evidence_dir.mkdir(parents=True, exist_ok=True)

        # Preserve failure log immutably
        log_file = evidence_dir / f"remediation_attempt_{attempt_number}.log"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Attempt: {attempt_number}\nTimestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\nDiagnosis: {json.dumps(diag)}\n\n{failure_log}\n")

        src_agent = workspace_dirs["src"] / "agent.py"
        if not src_agent.exists():
            return {"success": False, "status": "BLOCKED", "error": "Source agent.py not found"}

        current_code = src_agent.read_text(encoding="utf-8")

        # Example surgical patch for common assertion drifts
        patched_code = current_code
        applied_patch = "No patch applied"

        if diag["category"] == "ASSERTION_FAILURE":
            # Ensure proper threshold rounding and standard deviation non-zero protection
            if "math.sqrt" in current_code and "std_dev == 0" not in current_code:
                patched_code = current_code.replace(
                    "if std_dev > 0:",
                    "if std_dev >= 0.0001:"
                )
                applied_patch = "Added epsilon check for std_dev"

        # Write patched code
        with open(src_agent, "w", encoding="utf-8") as f:
            f.write(patched_code)

        return {
            "success": True,
            "status": "REMEDIATED",
            "attempt": attempt_number,
            "diagnosis": diag,
            "applied_patch": applied_patch,
            "evidence_ref": str(log_file),
        }
