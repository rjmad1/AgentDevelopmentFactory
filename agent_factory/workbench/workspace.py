"""
Isolated Workspace Manager for Factory Builds and Sandboxes.
"""

from pathlib import Path
from typing import Dict, Any
import shutil


class WorkspaceManager:
    """Provisions and isolates project workspaces on the local filesystem."""

    def __init__(self, base_workspaces_dir: Path):
        self.base_dir = Path(base_workspaces_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def provision_workspace(self, project_id: str, clean: bool = False) -> Dict[str, Path]:
        ws_root = self.base_dir / project_id
        if clean and ws_root.exists():
            shutil.rmtree(ws_root)

        dirs = {
            "root": ws_root,
            "src": ws_root / "src",
            "tests": ws_root / "tests",
            "fixtures": ws_root / "fixtures",
            "artifacts": ws_root / "artifacts",
            "evidence": ws_root / "evidence",
            "scratch": ws_root / "scratch",
        }

        for p in dirs.values():
            p.mkdir(parents=True, exist_ok=True)

        return dirs

    def clean_workspace(self, project_id: str) -> None:
        ws_root = self.base_dir / project_id
        if ws_root.exists():
            shutil.rmtree(ws_root)
