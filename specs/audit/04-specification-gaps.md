# Audit Report 04: Specification Gaps & Architectural Discrepancies

**Audit ID:** AUD-04-SPEC-GAPS  
**Date:** November 20, 2026  
**Auditors:** Independent Architecture Auditor, DevSecOps Engineer, SDD Specialist  
**Status:** BASELINED  

---

## 1. Discrepancy Classification Framework

Discrepancies identified between specifications and the codebase are classified into eight categories:

1. **Implemented and Documented:** Code exists, behavior matches written spec, tests pass.
2. **Implemented but Undocumented:** Code exists and works, but no formal specification governs it.
3. **Documented but Not Implemented:** Specification mandates behavior that is not yet realized in code.
4. **Implemented Differently from Documented Intent:** Implementation diverges from written spec.
5. **Partially Implemented:** Scaffolding or stub exists; complete workflow incomplete.
6. **Duplicated Functionality:** Redundant implementations across modules.
7. **Obsolete Functionality:** Legacy code retaining no active purpose.
8. **Unclear or Unverifiable Functionality:** Ambiguous behavior lacking deterministic test evidence.

---

## 2. Identified Discrepancies & Recommended Remediations

### GAP-01: Undocumented Node.js Authoring Front-End
* **Classification:** Implemented but Undocumented (Cat 2).
* **Observed Reality:** `src/core.js` and `src/cli.js` implement pure-JS hashing, filesystem containment checking, immutable revisions, and check event ledgers. However, the existing 33 `FACTORY_*.md` specs only describe the Python architecture.
* **Remediation:** Authored Spec Kit feature specification `specs/features/001-bounded-authoring-slice/` detailing the Node.js authoring engine, inputs/outputs, and security guarantees.

### GAP-02: Undocumented Hermes Fleet Watcher Loop & Packet Bundlers
* **Classification:** Implemented but Undocumented (Cat 2).
* **Observed Reality:** `scripts/autonomous-loop.js` and `scripts/bundle-*-packet.js` automate file watching, test execution, and surgical JSON packet bundling for Critic, Verifier, and Doc agents.
* **Remediation:** Authored Spec Kit feature specification `specs/features/002-autonomous-watcher-loop/` and packet schema contracts in `specs/contracts/hermes-packets/`.

### GAP-03: Missing Runtime Dependency (`jsonschema`)
* **Classification:** Implemented Differently / Defect (Cat 4).
* **Observed Reality:** `agent_factory/specs/validator.py` imports `jsonschema`, but `jsonschema` was omitted from `requirements.txt`, causing an unhandled `ModuleNotFoundError` during system Python invocation.
* **Remediation:** Added `jsonschema>=4.20.0` directly to `requirements.txt` in the unified branch.

### GAP-04: Divergent CI/CD Workflow Pipelines
* **Classification:** Partially Implemented & Overlapping (Cat 5 & 6).
* **Observed Reality:** Local `main` created `.github/workflows/pipeline.yml` (Python-centric), while `origin/main` created `.github/workflows/ci.yml` and `docs.yml` (Node-centric).
* **Remediation:** Unified the CI pipeline to run both Node.js tests (`npm run ci`) and Python verification (`pytest tests/`), while standardizing documentation builds on `docs.yml`.

### GAP-05: Abstract Provider Adapters Lacking Live Streaming
* **Classification:** Partially Implemented (Cat 5).
* **Observed Reality:** `agent_factory/adapters/base.py` and `omniroute_adapter.py` establish HTTP POST interfaces, but streaming token responses (`SSE`) are modeled as synchronous single-payload returns.
* **Remediation:** Explicitly flag streaming support as an open enhancement in `specs/architecture/integration-architecture.md`.

### GAP-06: Disconnected Authoring-to-Factory Handoff
* **Classification:** Implemented Differently from Documented Intent (Cat 4).
* **Observed Reality:** The Node.js authoring CLI outputs Markdown specifications and JSON manifests for newly drafted agents, but does not yet emit the exact Pydantic-compatible `agent.yaml` consumed by `agent_factory.control_plane.intake`.
* **Remediation:** Formally specify the bridge contract in `specs/contracts/README.md` and feature spec `specs/features/001-bounded-authoring-slice/`.

---

## 3. Successor Report

Gaps measured against the external **Agent Development Factory Baseline v1.0.0** requirement set (ADF-001 … ADF-040) are recorded separately in [`06-baseline-v1.0.0-delta.md`](06-baseline-v1.0.0-delta.md), which extends this report rather than superseding it. The capability status derived from it is published at [`docs/ROADMAP.md`](../../docs/ROADMAP.md).
