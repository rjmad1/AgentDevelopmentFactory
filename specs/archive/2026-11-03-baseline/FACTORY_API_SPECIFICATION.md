# Factory API Specification

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** BASELINED & APPROVED  

---

## 1. Overview & Interface Contracts

The Agent Development Factory exposes a unified programmatic Python API and an accompanying CLI interface (`agent_factory.cli`). It enables automation scripts, orchestrators (Hermes Agent), and IDEs (Antigravity 2.0) to drive the agent manufacturing lifecycle deterministically.

---

## 2. Python Programmatic API (`agent_factory.api`)

### 2.1 Project Lifecycle API

```python
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class ProjectSummary(BaseModel):
    project_id: str
    name: str
    current_stage: str
    risk_level: str
    status: str
    created_at: str

class FactoryAPI:
    def create_project(self, prompt: str, owner: str = "Admin") -> ProjectSummary:
        """
        Ingests a business requirement prompt, initializes a project workspace, 
        generates the Universal Agent Specification, and registers the project.
        """
        ...

    def build_agent(self, project_id: str) -> Dict[str, Any]:
        """
        Synthesizes agent source code, unit test fixtures, and mock wrappers in the workspace.
        """
        ...

    def test_agent(self, project_id: str) -> Dict[str, Any]:
        """
        Executes pytest suite in the isolated workspace. Returns exit code, stdout, and test counts.
        """
        ...

    def evaluate_agent(self, project_id: str, suite_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs independent multi-metric evaluation (Efficacy, Safety, Efficiency).
        """
        ...

    def remediate_agent(self, project_id: str) -> Dict[str, Any]:
        """
        Executes bounded remediation loop if tests or evaluations failed.
        """
        ...

    def package_release(self, project_id: str, approval_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates reproducible release ZIP, manifest, and checksums. Enforces risk-based approval.
        """
        ...

    def deploy_agent(self, project_id: str, target: str = "local_process") -> Dict[str, Any]:
        """
        Deploys agent release package to the designated target runtime.
        """
        ...

    def rollback_agent(self, agent_id: str, target_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Reverts an active agent deployment to a prior verified release bundle.
        """
        ...

    def get_status(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns factory status, active projects, capabilities, and system health.
        """
        ...
```

---

## 3. Command-Line Interface (CLI) Specification

The CLI executable `factory` (invoked via `python -m agent_factory.cli` or `factory`) supports the following verified commands:

| Command | Arguments | Options | Description |
| :--- | :--- | :--- | :--- |
| `status` | None | `--full`, `--json` | Displays factory health, registered capabilities, and running workflows. |
| `intake` | `<prompt>` | `--owner`, `--risk` | Ingests a new agent request and generates `agent.yaml`. |
| `build` | `<project_id>` | `--clean` | Provisions workspace and synthesizes source code + test suite. |
| `test` | `<project_id>` | `--verbose` | Runs automated pytest suite in the isolated workspace. |
| `eval` | `<project_id>` | `--suite <id>` | Runs independent multi-metric evaluation pack. |
| `remediate` | `<project_id>` | `--max-attempts <n>` | Triggers bounded defect diagnosis and repair loop. |
| `package` | `<project_id>` | `--token <tok>` | Builds reproducible release bundle with SHA-256 manifest. |
| `deploy` | `<project_id>` | `--target <t>` | Deploys release bundle to `local_process` or `hermes`. |
| `rollback` | `<agent_id>` | `--version <v>` | Reverts deployed agent to previous known-good version. |
| `run` | `<agent_id>` | `--input <json>`, `--target <t>` | Executes deployed agent against input data. |
