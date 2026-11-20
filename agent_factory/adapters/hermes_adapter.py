"""
Hermes Agent Harness Adapter (CLI Delegation Interface).
"""

import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from agent_factory.adapters.base import HarnessAdapter
from agent_factory.security.redactor import SecretRedactor


class HermesHarnessAdapter(HarnessAdapter):
    """Integrates with the installed Hermes Agent CLI (v0.22.6)."""

    def __init__(self, hermes_executable: Optional[str] = None):
        self.hermes_exe = hermes_executable or shutil.which("hermes") or r"C:\Users\rajaj\.local\bin\hermes.cmd"

    def is_available(self) -> bool:
        return Path(self.hermes_exe).exists() or shutil.which("hermes") is not None

    def get_version(self) -> str:
        if not self.is_available():
            return "NOT_INSTALLED"
        try:
            res = subprocess.run([self.hermes_exe, "--version"], capture_output=True, text=True, timeout=5)
            return res.stdout.strip()
        except Exception as e:
            return f"ERROR: {e}"

    def run_bounded_task(self, query: str, workdir: str, timeout_seconds: int = 60) -> Dict[str, Any]:
        """Runs a bounded non-interactive Hermes task using `hermes chat -q`."""
        if not self.is_available():
            return {"success": False, "error": "Hermes executable not found"}

        cmd = [self.hermes_exe, "chat", "-q", query, "--in", workdir]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return {
                "success": (res.returncode == 0),
                "exit_code": res.returncode,
                "stdout": SecretRedactor.redact_text(res.stdout),
                "stderr": SecretRedactor.redact_text(res.stderr),
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "exit_code": 124, "error": "Hermes command timed out"}
        except Exception as e:
            return {"success": False, "exit_code": 1, "error": str(e)}
