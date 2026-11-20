# Factory Operations Runbook

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** BASELINED & APPROVED  

---

## 1. Daily Operations & System Health

The Agent Development Factory operates as a reliable, quality-gated production line. This runbook details operational procedures for inspecting factory health, driving agent projects, managing active workflows, and retiring agents.

### 1.1 Checking Factory Health
To inspect the overall health of the factory, registered capabilities, and running projects:
```powershell
python -m agent_factory.cli status
```
*Expected Output:*
* Status of Control Plane database (`data/factory_state.db`).
* Total active, unverified, and deprecated capabilities in the Capability Registry.
* Count of active projects, completed builds, and in-flight tasks.
* Status of local gateway listeners (OmniRoute on 20128, FreeLLMAPI on 31415).

---

## 2. Standard Agent Manufacturing Workflow

### Step 1: Ingest New Agent Requirement
```powershell
python -m agent_factory.cli intake "Build an agent that analyzes CSV files for data quality anomalies" --owner "Raja" --risk "LOW"
```
*Output:* Creates project directory in `workspaces/<project_id>/` and generates baselined `agent.yaml`.

### Step 2: Build Agent Source Code & Tests
```powershell
python -m agent_factory.cli build <project_id>
```
*Output:* Synthesizes Python implementation in `src/agent.py` and automated test suite in `tests/test_agent.py`.

### Step 3: Run Automated Tests
```powershell
python -m agent_factory.cli test <project_id>
```
*Output:* Executes isolated pytest run. Returns exit code, passing assertions, and captures stdout/stderr to evidence ledger.

### Step 4: Run Independent Evaluation
```powershell
python -m agent_factory.cli eval <project_id>
```
*Output:* Computes Efficacy, Safety, and Efficiency score vectors against golden benchmarks.

### Step 5: Package Release
```powershell
python -m agent_factory.cli package <project_id>
```
*Output:* Bundles code, locked dependencies, test suite, and frozen spec into `releases/<agent_id>-v1.0.0.zip` with `manifest.json` and `checksums.sha256`.

### Step 6: Deploy & Execute Agent
```powershell
python -m agent_factory.cli run <agent_id> --input '{"dataset_path": "fixtures/data.csv"}'
```
*Output:* Executes deployed agent in target runtime and prints path to generated report and ledger.

---

## 3. Incident Management & Operator Procedures

### 3.1 Handling Remediation Failures (Circuit Breaker Tripped)
If an agent fails tests and exceeds the 3-attempt remediation ceiling:
1. Inspect the diagnostic failure log:
   ```powershell
   Get-Content workspaces/<project_id>/evidence/remediation_failure.log
   ```
2. Review the failing test assertion in `workspaces/<project_id>/tests/test_agent.py`.
3. If the requirement was ambiguous, update `agent.yaml` with clarified constraints and re-trigger:
   ```powershell
   python -m agent_factory.cli build <project_id> --clean
   ```

### 3.2 Retiring a Deployed Agent
To decommission an agent when its business objective is completed:
1. Revoke active permissions and mark status as `RETIRED` in registry:
   ```powershell
   python -m agent_factory.cli retire <agent_id>
   ```
2. Archive the final release bundle to cold storage.
3. Remove workspace scratch directories while permanently preserving the cryptographic evidence ledger.
