# Factory Backup and Restore Guide

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** BASELINED & APPROVED  

---

## 1. Backup Strategy & Objectives

The backup policy for the Agent Development Factory is governed by strict Recovery Point Objective (RPO) and Recovery Time Objective (RTO) targets:

* **RPO (Recovery Point Objective):** $\le 1$ hour for active development state; $0$ loss for released agent packages and cryptographic evidence.
* **RTO (Recovery Time Objective):** $\le 15$ minutes for complete factory control plane restoration.

---

## 2. Backup Scope & Assets

| Asset Category | Location | Frequency | Retention | Backup Method |
| :--- | :--- | :--- | :--- | :--- |
| **Control Plane State** | `data/factory_state.db`<br>`data/task_events.jsonl` | Hourly snapshot + Real-time event append | 30 days | Atomic SQLite `.backup` command |
| **Capability Registry** | `data/capability_registry.json` | Daily snapshot / On change | 90 days | Versioned JSON snapshot |
| **Release Bundles** | `releases/*.zip` | Immediate on release | Indefinite | Immutable archive with SHA-256 manifests |
| **Evidence Ledger** | `evidence/evidence_ledger.jsonl` | Real-time append | Indefinite | Append-only immutable log |
| **Source Specifications** | `specs/*.yaml` | Daily snapshot / Git commits | Indefinite | Git version control |

*Excluded from Backup:* Ephemeral scratch folders, temporary virtual environments, and unredacted memory cache dumps.

---

## 3. Automated Backup Procedure

To take an atomic, non-blocking backup of the factory state and registries:
```powershell
python -m agent_factory.cli backup --destination data/backups/
```

This command performs:
1. SQLite online backup API to ensure a transactionally consistent copy of `factory_state.db`.
2. Flushes and syncs `task_events.jsonl` and `evidence_ledger.jsonl`.
3. Creates a timestamped ZIP archive: `data/backups/factory_backup_YYYYMMDD_HHMMSS.zip`.
4. Computes and records the SHA-256 digest of the backup archive in `data/backups/manifest.txt`.

---

## 4. Restore Drill Procedure (Tested & Validated)

1. **Staging Restoration:** Copy the backup archive to a scratch staging directory:
   ```powershell
   Expand-Archive -Path data/backups/factory_backup_latest.zip -DestinationPath scratch/restore_test/
   ```
2. **Checksum Verification:** Compute SHA-256 of extracted files and compare against recorded manifest:
   ```powershell
   Get-FileHash scratch/restore_test/factory_state.db -Algorithm SHA256
   ```
3. **Integrity Validation:** Run PRAGMA integrity check on the restored database:
   ```powershell
   python -c "import sqlite3; con = sqlite3.connect('scratch/restore_test/factory_state.db'); print(con.execute('PRAGMA integrity_check;').fetchall())"
   ```
4. **Promotion:** Overwrite corrupted database with restored file only after integrity verification confirms `[('ok',)]`.
