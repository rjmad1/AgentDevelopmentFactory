# Agent Development Factory (Authoring Slice)

The **Agent Development Factory** is a meta-product that transforms business-workflow briefs into inspectable, portable, and verifiable Agent Build Packs.

This repository contains the bounded first **Authoring Slice** — a zero-dependency, pure Node.js CLI that exercises the foundational lifecycle:

$$\text{Brief} \longrightarrow \text{Structured Requirements} \longrightarrow \text{Inspectable Specification \& Manifest} \longrightarrow \text{Append-Only Evidence Ledger} \longrightarrow \text{Immutable Revisions}$$

---

## Key Invariants & Architectural Capabilities

1. **Explicit Triaged Requirements Ledger:**
   - **CONFIRMED:** Requires explicit supplied human confirmation assertions (`assertionType: "SUPPLIED_HUMAN_ASSERTION"`, `authenticated: false`). The CLI records supplied assertions for provenance; it does not authenticate human identity or assert unverified executive approvals.
   - **PROPOSED:** Inferred defaults or template-suggested rules, explicitly tagged with inference rationale and kept awaiting human sign-off.
   - **UNRESOLVED:** Explicit open ambiguities and candidate choices. The Factory strictly refuses to silently invent business rules or fill gaps with hidden defaults.

2. **Immutable Revisions by Policy:**
   - Snapshots are created exclusively and immutably (`exclusive` filesystem directory creation).
   - Revisions link to optional parent revisions via SHA-256 dependency chains.
   - A subsequent revision (`rev-002`) cannot mutate or overwrite any artifact in a prior revision (`rev-001`).

3. **Append-Only Evidence Ledger & Divergence Detection:**
   - `check_events.jsonl` serves as the authoritative append-only log of check executions.
   - `evidence.json` serves as the materialized ledger recording check definitions, initial statuses (`NOT RUN` / `BLOCKED`), execution counts, and run histories.
   - `verifyEvidenceConsistency()` performs line-by-line parity auditing between the event log and ledger, detecting and reporting discrepancies without silent repair or truncation.

4. **Checker Implementation Dependencies & Invalidation:**
   - Check definitions record the SHA-256 of the checker engine rules and version (`0.3.0`).
   - If either artifact inputs or the checker implementation change, active applicability is automatically invalidated to `STALE` while preserving immutable historical execution logs.

5. **Real Filesystem Containment:**
   - `assertRealFsContainment()` resolves native filesystem paths (`realpath`) and walks ancestor directories to trap and reject symbolic link, directory junction, or path traversal escapes.

---

## Directory Structure

```
.
├── src/
│   ├── core.js           # Core authoring engine, hashing, containment & evidence
│   └── cli.js            # Standalone Node.js CLI
├── fixtures/             # Synthetic test briefs and structured requirements
│   ├── synthetic_brief_v1.txt
│   ├── synthetic_requirements_v1.json
│   ├── synthetic_requirements_v2.json
│   ├── synthetic_requirements_unconfirmed.json
│   └── synthetic_requirements_forbidden_name.json
├── test/
│   └── runner.js         # 13-test repeatable verification test suite
├── docs/                 # Product contracts and planning architecture
├── package.json
└── README.md
```

---

## Getting Started

### Prerequisites
- Node.js (v20+ or v26+)
- Zero external package dependencies (uses `node:fs`, `node:path`, `node:crypto`, `node:child_process`).

### Running the CLI

#### 1. Initialize a Revision
```bash
node src/cli.js init-revision \
  --brief fixtures/synthetic_brief_v1.txt \
  --requirements fixtures/synthetic_requirements_v1.json \
  --revision-id rev-001
```

#### 2. Run Static Validation Checks
```bash
node src/cli.js run-check --revision rev-001 --check CHK-STATIC-SCHEMA
node src/cli.js run-check --revision rev-001 --check CHK-REQUIREMENTS-TRIAGE
```

#### 3. Inspect Revision & Verify Consistency
```bash
node src/cli.js inspect --revision rev-001
node src/cli.js verify-consistency --revision rev-001
```

#### 4. Initialize Child Revision with Parent Link
```bash
node src/cli.js init-revision \
  --brief fixtures/synthetic_brief_v1.txt \
  --requirements fixtures/synthetic_requirements_v2.json \
  --revision-id rev-002 \
  --parent-rev rev-001
```

---

## Running the Automated Test Suite

Run the full 13-test suite (executed twice across separate fresh stores to verify repeatability):
```bash
node test/runner.js
```

---

## Boundary Notice

This authoring slice implements static data flow, document generation, and evidence ledger mechanics. It produces **no executable agent code, live tool adapters, or candidate runners**. Supervised runtime evaluation is in v1 product scope, but is held as a `BLOCKED` prerequisite in this authoring slice.
