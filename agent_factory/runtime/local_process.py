"""
Standalone Local Process Runtime for Agent Execution.
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from agent_factory.runtime.base import AgentRuntime, ExecutionLimits, ExecutionResult
from agent_factory.security.redactor import SecretRedactor


class LocalProcessRuntime(AgentRuntime):
    """Executes agents as isolated OS subprocesses with timeout and environment bounds."""

    # Sensitive environment variables to strip from child processes
    SENSITIVE_ENV_VARS = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "AWS_SECRET_ACCESS_KEY",
        "GITHUB_TOKEN",
        "GH_TOKEN",
    ]

    def __init__(self, python_executable: Optional[str] = None):
        self.python_exe = python_executable or sys.executable

    def _sanitize_env(self) -> Dict[str, str]:
        env = dict(os.environ)
        for var in self.SENSITIVE_ENV_VARS:
            env.pop(var, None)
        return env

    def execute(
        self,
        entrypoint_script: Path,
        args: List[str],
        limits: ExecutionLimits,
        workdir: Path,
    ) -> ExecutionResult:
        p = Path(entrypoint_script)
        if not p.exists():
            return ExecutionResult(
                success=False,
                exit_code=127,
                duration_ms=0.0,
                stdout="",
                stderr=f"Entrypoint script not found: {p}",
                error_message="Entrypoint not found",
            )

        cmd = [self.python_exe, str(p.resolve())] + args
        clean_env = self._sanitize_env()

        start_time = time.perf_counter()
        try:
            completed = subprocess.run(
                cmd,
                cwd=str(workdir.resolve()),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=limits.max_wall_time_seconds,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            clean_stdout = SecretRedactor.redact_text(completed.stdout)
            clean_stderr = SecretRedactor.redact_text(completed.stderr)

            # Detect created artifacts under workdir/artifacts
            artifacts = {}
            art_dir = workdir / "artifacts"
            if art_dir.exists():
                for f in art_dir.rglob("*"):
                    if f.is_file():
                        artifacts[f.name] = str(f.resolve())

            return ExecutionResult(
                success=(completed.returncode == 0),
                exit_code=completed.returncode,
                duration_ms=round(elapsed_ms, 2),
                stdout=clean_stdout,
                stderr=clean_stderr,
                artifacts_created=artifacts,
                error_message=clean_stderr if completed.returncode != 0 else "",
            )

        except subprocess.TimeoutExpired as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                success=False,
                exit_code=124,
                duration_ms=round(elapsed_ms, 2),
                stdout=SecretRedactor.redact_text(e.stdout or ""),
                stderr=f"Execution timed out after {limits.max_wall_time_seconds} seconds.",
                error_message="TimeoutExpired",
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                success=False,
                exit_code=1,
                duration_ms=round(elapsed_ms, 2),
                stdout="",
                stderr=SecretRedactor.redact_text(str(e)),
                error_message=str(e),
            )
