# Tasks: Bounded Factory Authoring Slice

**Feature Branch:** `001-bounded-authoring-slice`  
**Feature ID:** FEAT-001  
**Status:** Completed  

---

## Task Breakdown

- [x] **TASK-001-01:** Implement pure deterministic SHA-256 and JSON key-sorting routines in `src/core.js`.
- [x] **TASK-001-02:** Implement real filesystem canonical containment check (`assertRealFsContainment`) rejecting path traversal and symlinks.
- [x] **TASK-001-03:** Implement `init-revision` routine creating immutable directory snapshots (`spec.md`, `manifest.json`, `evidence.json`).
- [x] **TASK-001-04:** Implement `CHK-STATIC-SCHEMA` and `CHK-REQUIREMENTS-TRIAGE` check handlers with explicit human confirmation validation.
- [x] **TASK-001-05:** Implement append-only check event logging in `check_events.jsonl` and ledger consistency auditor in `verify-consistency`.
- [x] **TASK-001-06:** Author CLI wrapper in `src/cli.js` with structured exit codes.
- [x] **TASK-001-07:** Author dual-run repeatable self-test runner in `test/runner.js` with 13 deterministic assertions.
