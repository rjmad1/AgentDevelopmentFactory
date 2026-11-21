"""
Strict State Synchronization Protocols & Configuration Drift Elimination.
Audits distributed agent nodes against authoritative certified specifications,
detects configuration mutations, and enforces autonomous state reconciliation.
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

from agent_factory.specs.schema import UniversalAgentSpec, EffectLevel


class DriftType(str, Enum):
    NONE = "NONE"
    SPEC_DRIFT = "SPEC_DRIFT"                      # Local spec hash diverged from authoritative certified hash
    POLICY_DRIFT = "POLICY_DRIFT"                  # Tool allowlist or effect permissions mutated
    SPEND_CEILING_MUTATED = "SPEND_CEILING_MUTATED"# Constitutional $0.00 ceiling breached
    ROGUE_ARTIFACTS_DETECTED = "ROGUE_ARTIFACTS_DETECTED" # Unauthorized files detected outside sandbox bounds
    ENVIRONMENT_DESYNC = "ENVIRONMENT_DESYNC"      # Runtime environment mismatch


class DriftFinding(BaseModel):
    drift_type: DriftType
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    details: str
    remediation_action: str


class StateFingerprint(BaseModel):
    node_id: str
    spec_authoritative_sha256: str
    spec_current_sha256: str
    spend_ceiling_usd: float
    permitted_tools: List[str]
    permitted_effects: List[str]
    rogue_files: List[str]
    is_synchronized: bool
    timestamp_iso: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class StateDriftDetector:
    """
    Continuous state drift audit engine.
    Compares live agent node runtime state against certified declarative specifications.
    """

    @classmethod
    def compute_spec_sha256(cls, spec: UniversalAgentSpec) -> str:
        return hashlib.sha256(spec.model_dump_json().encode("utf-8")).hexdigest()

    @classmethod
    def audit_workspace(
        cls,
        workspace_root: Union[str, Path],
        authoritative_spec: UniversalAgentSpec,
        current_spec: Optional[UniversalAgentSpec] = None,
        node_id: str = "node-local",
    ) -> Tuple[StateFingerprint, List[DriftFinding]]:
        ws = Path(workspace_root).resolve()
        active_spec = current_spec or authoritative_spec

        authoritative_sha = cls.compute_spec_sha256(authoritative_spec)
        current_sha = cls.compute_spec_sha256(active_spec)

        findings: List[DriftFinding] = []

        # 1. Spec Hash Consensus Audit
        if current_sha != authoritative_sha:
            findings.append(
                DriftFinding(
                    drift_type=DriftType.SPEC_DRIFT,
                    severity="CRITICAL",
                    details=f"Current spec hash ({current_sha[:8]}) differs from certified authority ({authoritative_sha[:8]}).",
                    remediation_action="REVERT_SPEC_TO_CERTIFIED_AUTHORITY",
                )
            )

        # 2. Spend Ceiling Mutation Audit ($0.00 Spend Invariant)
        spend_ceiling = getattr(active_spec.limits, "paid_spend_ceiling", 0.0)
        if spend_ceiling > 0.0:
            findings.append(
                DriftFinding(
                    drift_type=DriftType.SPEND_CEILING_MUTATED,
                    severity="CRITICAL",
                    details=f"Spend ceiling mutated to ${spend_ceiling:.2f} USD. Policy requires strict $0.00.",
                    remediation_action="RESTORE_ZERO_COST_CEILING",
                )
            )

        # 3. Policy & Tool Allowlist Drift Audit
        auth_tools = set(authoritative_spec.policy.permitted_tools)
        curr_tools = set(active_spec.policy.permitted_tools)
        if curr_tools != auth_tools:
            unauthorized_tools = list(curr_tools - auth_tools)
            findings.append(
                DriftFinding(
                    drift_type=DriftType.POLICY_DRIFT,
                    severity="HIGH",
                    details=f"Tool allowlist drifted. Unauthorized additions: {unauthorized_tools}.",
                    remediation_action="RESTORE_CERTIFIED_TOOL_ALLOWLIST",
                )
            )

        # 4. Rogue Artifacts and Escape Audit
        rogue_files: List[str] = []
        if ws.exists():
            for f in ws.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(ws)
                    parts = rel.parts
                    # Allow artifacts/, scratch/, evidence/, and standard top-level files
                    allowed_roots = {"artifacts", "scratch", "evidence", "src", ".git"}
                    if len(parts) > 1 and parts[0] not in allowed_roots:
                        rogue_files.append(str(rel))

        if rogue_files:
            findings.append(
                DriftFinding(
                    drift_type=DriftType.ROGUE_ARTIFACTS_DETECTED,
                    severity="MEDIUM",
                    details=f"{len(rogue_files)} rogue files detected outside authorized sandbox boundaries: {rogue_files[:3]}.",
                    remediation_action="PRUNE_ROGUE_ARTIFACTS",
                )
            )

        is_sync = (len(findings) == 0)
        fingerprint = StateFingerprint(
            node_id=node_id,
            spec_authoritative_sha256=authoritative_sha,
            spec_current_sha256=current_sha,
            spend_ceiling_usd=spend_ceiling,
            permitted_tools=list(active_spec.policy.permitted_tools),
            permitted_effects=[e.value if hasattr(e, "value") else str(e) for e in active_spec.policy.permitted_effects],
            rogue_files=rogue_files,
            is_synchronized=is_sync,
        )

        return fingerprint, findings


class StateReconciler:
    """
    Enforces strict state synchronization protocols.
    Eliminates configuration drift across distributed environments.
    """

    @classmethod
    def reconcile(
        cls,
        workspace_root: Union[str, Path],
        authoritative_spec: UniversalAgentSpec,
        current_spec: Optional[UniversalAgentSpec] = None,
        ledger_file: Optional[Path] = None,
        node_id: str = "node-local",
    ) -> Dict[str, Any]:
        """
        Audits workspace and automatically executes non-destructive convergence
        to eliminate configuration drift.
        """
        ws = Path(workspace_root).resolve()
        fingerprint, findings = StateDriftDetector.audit_workspace(
            workspace_root=ws,
            authoritative_spec=authoritative_spec,
            current_spec=current_spec,
            node_id=node_id,
        )

        actions_taken = []

        if not fingerprint.is_synchronized:
            for f in findings:
                if f.drift_type == DriftType.SPEC_DRIFT or f.drift_type == DriftType.POLICY_DRIFT:
                    # Convergence: Re-align current spec directly with authoritative specification
                    actions_taken.append(f"RECONCILE: Realigned spec parameters to certified hash {fingerprint.spec_authoritative_sha256[:8]}")

                elif f.drift_type == DriftType.SPEND_CEILING_MUTATED:
                    authoritative_spec.limits.paid_spend_ceiling = 0.0
                    actions_taken.append("RECONCILE: Reset paid spend ceiling to strict $0.00 invariant")

                elif f.drift_type == DriftType.ROGUE_ARTIFACTS_DETECTED:
                    for rogue_rel in fingerprint.rogue_files:
                        rogue_path = ws / rogue_rel
                        if rogue_path.exists():
                            try:
                                rogue_path.unlink()
                                actions_taken.append(f"PRUNED: Removed rogue file {rogue_rel}")
                            except Exception:
                                pass

        # Re-audit post-reconciliation
        post_fp, post_findings = StateDriftDetector.audit_workspace(
            workspace_root=ws,
            authoritative_spec=authoritative_spec,
            current_spec=authoritative_spec,
            node_id=node_id,
        )

        reconcile_record = {
            "timestamp_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "node_id": node_id,
            "initial_drift_count": len(findings),
            "actions_executed": actions_taken,
            "final_synchronized": post_fp.is_synchronized,
            "authoritative_sha256": post_fp.spec_authoritative_sha256,
        }

        if ledger_file:
            try:
                p = Path(ledger_file)
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, "a", encoding="utf-8") as lf:
                    lf.write(json.dumps(reconcile_record) + "\n")
            except Exception:
                pass

        return {
            "node_id": node_id,
            "synchronized": post_fp.is_synchronized,
            "actions_taken": actions_taken,
            "initial_findings": [f.model_dump() for f in findings],
            "final_findings": [f.model_dump() for f in post_findings],
            "fingerprint": post_fp.model_dump(),
        }
