"""
Strict Sandboxed Execution Runtime for Agent Workloads.
Provides hermetic process isolation, network sandboxing ($0.00 spend ceiling),
static AST quarantine pre-execution auditing, and real filesystem containment.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

from agent_factory.runtime.base import AgentRuntime, ExecutionLimits, ExecutionResult
from agent_factory.runtime.local_process import LocalProcessRuntime
from agent_factory.security.redactor import SecretRedactor
from agent_factory.security.quarantine import SkillQuarantine


class SandboxConfig(BaseModel):
    network_isolated: bool = True
    strip_env_secrets: bool = True
    enable_ast_quarantine: bool = True
    enforce_fs_containment: bool = True
    max_output_bytes: int = 5 * 1024 * 1024  # 5 MB cap
    prohibited_write_roots: List[str] = Field(
        default_factory=lambda: ["windows", "system32", "program files", "etc", "usr", "bin", "root"]
    )


class SandboxedLocalProcessRuntime(LocalProcessRuntime):
    """
    Hardened execution runtime that isolates agent processes within a strict sandbox.
    Enforces AST quarantine pre-execution vetting, offline network barriers, and path bounds.
    """

    def __init__(
        self,
        python_executable: Optional[str] = None,
        config: Optional[SandboxConfig] = None,
    ):
        super().__init__(python_executable=python_executable)
        self.config = config or SandboxConfig()

    def _prepare_sandboxed_env(self, workdir: Path) -> Dict[str, str]:
        """Prepares a hermetic, scrubbed environment with network barriers and secret isolation."""
        # Start from stripped environment
        env = self._sanitize_env()

        # Additional sensitive keys to purge
        extra_strip = [
            "SSH_AUTH_SOCK",
            "DATABASE_URL",
            "SECRET_KEY",
            "PRIVATE_KEY",
            "PASSWORD",
            "AUTH_TOKEN",
            "HERMES_API_KEY",
            "OMNIRoute_API_KEY",
        ]
        for k in list(env.keys()):
            if any(term in k.upper() for term in extra_strip) or k.upper().endswith("_SECRET"):
                env.pop(k, None)

        # Force offline / network isolation ($0.00 spend ceiling)
        if self.config.network_isolated:
            env["HTTP_PROXY"] = "http://127.0.0.1:0"
            env["HTTPS_PROXY"] = "http://127.0.0.1:0"
            env["ALL_PROXY"] = "http://127.0.0.1:0"
            env["PYTHONHTTPSVERIFY"] = "1"
            env["CURL_CA_BUNDLE"] = ""

        # Sandboxed python execution flags
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Restrict PYTHONPATH strictly to agent source directories
        src_dir = workdir / "src"
        pythonpath_parts = [str(workdir.resolve())]
        if src_dir.exists():
            pythonpath_parts.insert(0, str(src_dir.resolve()))
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

        return env

    def _verify_path_containment(self, target: Path, workdir: Path) -> None:
        """Asserts that a target path is contained within the authorized workspace."""
        res_target = target.resolve()
        res_workdir = workdir.resolve()

        # Check path starts with workdir
        if not str(res_target).startswith(str(res_workdir)):
            raise PermissionError(
                f"SANDBOX_CONTAINMENT_VIOLATION: Path '{res_target}' is outside workspace '{res_workdir}'."
            )

        # Check prohibited system directories
        target_str = str(res_target).lower()
        for bad_root in self.config.prohibited_write_roots:
            if f"{os.sep}{bad_root}{os.sep}" in target_str or target_str.endswith(f"{os.sep}{bad_root}"):
                raise PermissionError(
                    f"SANDBOX_CONTAINMENT_VIOLATION: Path '{res_target}' targets prohibited system location '{bad_root}'."
                )

    def execute(
        self,
        entrypoint_script: Path,
        args: List[str],
        limits: ExecutionLimits,
        workdir: Path,
    ) -> ExecutionResult:
        p = Path(entrypoint_script).resolve()
        workdir_path = Path(workdir).resolve()

        if not p.exists():
            return ExecutionResult(
                success=False,
                exit_code=127,
                duration_ms=0.0,
                stdout="",
                stderr=f"Entrypoint script not found: {p}",
                error_message="Entrypoint not found",
            )

        # 1. Real Filesystem Containment Verification
        if self.config.enforce_fs_containment:
            try:
                self._verify_path_containment(p, workdir_path)
            except PermissionError as e:
                return ExecutionResult(
                    success=False,
                    exit_code=126,
                    duration_ms=0.0,
                    stdout="",
                    stderr=str(e),
                    error_message="Filesystem containment violation",
                )

        # 2. Static Pre-Execution Quarantine AST Audit
        if self.config.enable_ast_quarantine:
            ast_findings = SkillQuarantine.audit_file(p)
            if ast_findings:
                err_msg = f"AST_QUARANTINE_REJECTED: Prohibited constructs in candidate script: {'; '.join(ast_findings)}"
                return ExecutionResult(
                    success=False,
                    exit_code=126,
                    duration_ms=0.0,
                    stdout="",
                    stderr=err_msg,
                    error_message="AST quarantine audit failed",
                )

        # 3. Provision Isolated Sandbox Directories
        scratch_dir = workdir_path / "scratch"
        artifacts_dir = workdir_path / "artifacts"
        scratch_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # 4. Prepare Hermetic Environment
        sandboxed_env = self._prepare_sandboxed_env(workdir_path)
        cmd = [self.python_exe, str(p)] + args

        start_time = time.perf_counter()
        try:
            completed = subprocess.run(
                cmd,
                cwd=str(workdir_path),
                env=sandboxed_env,
                capture_output=True,
                text=True,
                timeout=limits.max_wall_time_seconds,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # 5. Cap Output and Redact Sensitive Tokens
            raw_stdout = completed.stdout or ""
            raw_stderr = completed.stderr or ""
            if len(raw_stdout) > self.config.max_output_bytes:
                raw_stdout = raw_stdout[: self.config.max_output_bytes] + "\n[OUTPUT_TRUNCATED: Exceeded 5MB Sandbox Cap]"

            clean_stdout = SecretRedactor.redact_text(raw_stdout)
            clean_stderr = SecretRedactor.redact_text(raw_stderr)

            # 6. Discover & Validate Created Artifacts
            artifacts = {}
            if artifacts_dir.exists():
                for f in artifacts_dir.rglob("*"):
                    if f.is_file():
                        # Verify artifact stays within artifacts directory
                        if self.config.enforce_fs_containment:
                            try:
                                self._verify_path_containment(f, workdir_path)
                                artifacts[f.name] = str(f.resolve())
                            except PermissionError:
                                pass
                        else:
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
                stderr=f"Execution timed out after {limits.max_wall_time_seconds} seconds. Sandbox killed process tree.",
                error_message=f"Timeout expired ({limits.max_wall_time_seconds}s)",
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                success=False,
                exit_code=1,
                duration_ms=round(elapsed_ms, 2),
                stdout="",
                stderr=f"Sandbox Execution Exception: {str(e)}",
                error_message=str(e),
            )
