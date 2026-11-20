# Factory Recovery Runbook

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** BASELINED & APPROVED  

---

## 1. Disaster Recovery & Rollback Protocols

This runbook establishes operational recovery procedures for unexpected host crashes, failed releases, agent behavioral drifts, and state corruption.

---

## 2. Recovery Scenarios and Action Steps

### Scenario 1: Host Crash During Active Factory Build
* **Symptom:** Machine rebooted or process terminated while an agent build, test, or eval was in progress.
* **Recovery Procedure:**
  1. Inspect the Task Ledger to determine in-flight state:
     ```powershell
     python -m agent_factory.cli resume --inspect
     ```
  2. The Control Plane identifies tasks with status `RUNNING` that lack a completed heartbeat.
  3. The orchestrator rolls back uncommitted files in `workspaces/<project_id>/` to the last verified stage checkpoint.
  4. Resume workflow from the beginning of the interrupted stage:
     ```powershell
     python -m agent_factory.cli resume <project_id>
     ```

### Scenario 2: Deployed Agent Fails in Production
* **Symptom:** A deployed agent experiences runtime crashes, output corruption, or unexpected latency spikes.
* **Recovery Procedure:**
  1. Immediately suspend the running agent to halt active task dispatch:
     ```powershell
     python -m agent_factory.cli suspend <agent_id>
     ```
  2. Query available prior verified releases:
     ```powershell
     Get-ChildItem releases/<agent_id>-v*.zip
     ```
  3. Execute automated rollback to the previous known-good version:
     ```powershell
     python -m agent_factory.cli rollback <agent_id> --version <previous_version>
     ```
  4. Verify deployment health:
     ```powershell
     python -m agent_factory.cli test-deployment <agent_id>
     ```
  5. Lift suspension once health checks pass.

### Scenario 3: Database or State Ledger Corruption
* **Symptom:** SQLite database `data/factory_state.db` fails integrity check or raises `DatabaseError`.
* **Recovery Procedure:**
  1. Restore the SQLite database from the latest verified snapshot (see `FACTORY_BACKUP_AND_RESTORE.md`):
     ```powershell
     Copy-Item data/backups/factory_state_latest.db data/factory_state.db -Force
     ```
  2. Replay all event entries from the append-only JSON Line log (`data/task_events.jsonl`) that occurred after the backup timestamp:
     ```powershell
     python -m agent_factory.cli replay-events --from-backup
     ```
  3. Verify database consistency:
     ```powershell
     python -m agent_factory.cli verify-state
     ```
