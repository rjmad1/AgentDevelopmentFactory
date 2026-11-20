# Change Log — Self-Verification Review & Defect Remediation

**Date:** 2026-11-20  
**Target Root:** `C:\Users\rajaj\.gemini\antigravity\scratch\factory-authoring-slice-20261120-c8f391`  
**Pre-Inspection Baselines:**
- Initial Baseline: `review-pre-inspection-20261120-070800` (17 files, inventory with full SHA-256)
- Integrity Milestone Baseline: `review-integrity-milestone-20261120-071500` (19 files, inventory with full SHA-256)

---

## Remediated Defects & Integrity Implementations

### 1. Real Filesystem Containment
* **Issue:** Prior lexical check (`path.resolve().startsWith()`) could be bypassed by symbolic links, junctions, or reparse points pointing outside the allowed store directory.
* **Remediation:**
  - Implemented `assertRealFsContainment(allowedParentDir, targetPath)` in `src/core.js`.
  - Performs lexical containment check, resolves native filesystem realpaths via `fs.realpathSync.native()`, and walks existing ancestor paths with `fs.lstatSync()` to reject any symlink or junction escapes.
  - Verified with synthetic sentinel fixture (`forbidden-sibling/secret_sentinel.txt`): link escapes are trapped with `SYMLINK_ESCAPE_DETECTED` / `FILESYSTEM_ESCAPE_DETECTED` and sentinel bytes remain 100% unaltered.

### 2. Consistent Evidence History & Divergence Detection
* **Issue:** In-place evidence mutations lost prior check outcomes, and multi-file writes (`check_events.jsonl` + `evidence.json`) could silently diverge if interrupted.
* **Remediation:**
  - Designated `check_events.jsonl` as the authoritative append-only execution event log.
  - Designated `evidence.json` as the materialized ledger recording `initialStatus`, `executionCount`, `history`, and `events`.
  - Implemented `verifyEvidenceConsistency(revDir)` in `src/core.js`: audits parity between `check_events.jsonl` and `evidence.json` (event count, event IDs, check statuses, exit codes, and execution counts).
  - Explicitly detects divergence (`EVENT_COUNT_MISMATCH` / `EVENT_DATA_MISMATCH`) and exits with code 1 instead of silently repairing, truncating, or replacing historical records.

### 3. Check-Implementation Dependencies & Invalidation Rules
* **Issue:** Evidence records previously tracked only artifact inputs, allowing a `PASSED` status to remain active even if the checker implementation logic or schema rules changed.
* **Remediation:**
  - Implemented `getCheckerImplementationHash()` and `evaluateEvidenceApplicability(check, currentArtifactHashes, currentCheckerHash)`.
  - Each check now records `checker.version`, `checker.implementationSha256`, and includes `checkerImplementationSha256` in its dependency inputs.
  - Invalidation rules:
    - If artifact hashes (brief, requirements, spec) change: active applicability is marked `STALE` (`ARTIFACT_DEPENDENCY_CHANGED`).
    - If checker implementation hash changes: active applicability is marked `STALE` (`CHECKER_IMPLEMENTATION_CHANGED`).
    - Historical records in `check_events.jsonl` and parent revisions remain untouched as immutable historical evidence.
    - Self-hashing circularity is avoided: `manifest.json` does not hash `evidence.json`, and the checker hash is computed over checker rules prior to evaluation.

### 4. Repeatable Test Harness Isolation
* **Issue:** Hardcoded `test-store` directory with `rmSync` startup deletion destroyed historical test artifacts and prevented multi-run repeatability verification.
* **Remediation:**
  - Test runner exclusively creates fresh unique run directories (`test-runs/run-<label>-<timestamp>-<random>/`) without deleting or overwriting any previous stores.
  - Automated dual execution (`run1` and `run2`) verifies 100% metric repeatability across completely independent filesystem stores.
