"""
Agent Lifecycle Manager: Deployment, Suspension, Rollback, and Retirement.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import shutil
import zipfile
import json
import datetime


class AgentLifecycleManager:
    """Manages deployed agent states, rollback restores, and decommissioning."""

    def __init__(self, releases_dir: Path, deployment_dir: Path):
        self.releases_dir = Path(releases_dir)
        self.deployment_dir = Path(deployment_dir)
        self.releases_dir.mkdir(parents=True, exist_ok=True)
        self.deployment_dir.mkdir(parents=True, exist_ok=True)

    def deploy_release(self, agent_id: str, version: str, target: str = "local_process") -> Dict[str, Any]:
        """Deploys a release package to the active deployment directory."""
        bundle_name = f"{agent_id}-v{version}.zip"
        bundle_path = self.releases_dir / bundle_name
        if not bundle_path.exists():
            raise FileNotFoundError(f"Release package not found: {bundle_path}")

        target_dir = self.deployment_dir / agent_id
        if target_dir.exists():
            # Backup active deployment for immediate rollback
            backup_dir = self.deployment_dir / f"{agent_id}_prev"
            shutil.rmtree(backup_dir, ignore_errors=True)
            shutil.copytree(target_dir, backup_dir)
            shutil.rmtree(target_dir)

        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(bundle_path, "r") as zf:
            zf.extractall(target_dir)

        manifest_path = target_dir / "manifest.json"
        manifest = {}
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

        return {
            "success": True,
            "agent_id": agent_id,
            "version": version,
            "deployed_to": str(target_dir),
            "runtime_target": target,
            "deployed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "manifest": manifest,
        }

    def rollback(self, agent_id: str, target_version: Optional[str] = None) -> Dict[str, Any]:
        """Reverts deployment to the previous version or specific release archive."""
        if target_version:
            return self.deploy_release(agent_id, target_version)

        # Roll back to the local backup
        backup_dir = self.deployment_dir / f"{agent_id}_prev"
        target_dir = self.deployment_dir / agent_id
        if not backup_dir.exists():
            raise FileNotFoundError(f"No previous deployment backup found for agent: {agent_id}")

        shutil.rmtree(target_dir, ignore_errors=True)
        shutil.copytree(backup_dir, target_dir)

        return {
            "success": True,
            "agent_id": agent_id,
            "action": "rolled_back_to_previous_state",
            "restored_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def suspend(self, agent_id: str, reason: str = "Operator request") -> Dict[str, Any]:
        """Locks an agent deployment, marking it suspended."""
        lock_file = self.deployment_dir / agent_id / "SUSPENDED"
        if not lock_file.parent.exists():
            raise FileNotFoundError(f"Agent '{agent_id}' is not currently deployed.")
        with open(lock_file, "w", encoding="utf-8") as f:
            f.write(f"Suspended on {datetime.datetime.now(datetime.timezone.utc).isoformat()}: {reason}\n")
        return {"success": True, "agent_id": agent_id, "status": "SUSPENDED", "reason": reason}

    def retire(self, agent_id: str) -> Dict[str, Any]:
        """Decommissions an agent deployment and marks it retired."""
        target_dir = self.deployment_dir / agent_id
        if target_dir.exists():
            shutil.rmtree(target_dir)
        return {"success": True, "agent_id": agent_id, "status": "RETIRED"}
