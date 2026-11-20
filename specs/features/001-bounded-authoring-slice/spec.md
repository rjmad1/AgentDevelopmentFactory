# Feature Specification: Bounded Factory Authoring Slice

**Feature Branch:** `001-bounded-authoring-slice`  
**Feature ID:** FEAT-001  
**Created:** 2026-11-20  
**Status:** Baselined  
**Classification:** Core Authoring Front-End  

---

## 1. Problem Statement & Objective

Authoring agent specifications in natural language often produces ambiguous, untestable requirements, leading to phantom successes, unauthorized scope expansion, and broken builds.

The **Bounded Factory Authoring Slice** solves this by introducing a zero-dependency, tamper-evident Node.js authoring engine that ingests plain-text briefs, triages structured requirements into explicit confirmation tiers (`CONFIRMED`, `PROPOSED`, `UNRESOLVED`), enforces real filesystem boundaries, and produces immutable revisions backed by an append-only event ledger.

---

## 2. User Scenarios & Prioritized User Stories

### User Story 1 — Initialize Immutable Revision from Brief & Requirements (Priority: P1)
As an Agent Developer, I want to initialize a new revision from a plain-text brief and structured JSON requirements, so that my specifications are permanently captured with cryptographic hashes and explicit parent linkages.

**Acceptance Criteria:**
* **Given** a valid brief file and structured requirements JSON file,
* **When** running `node src/cli.js init-revision --brief <path> --requirements <path> --revision-id <id>`,
* **Then** the CLI creates an immutable revision snapshot containing `spec.md`, `manifest.json`, and empty `evidence.json`, and writes an event to `check_events.jsonl`.
* **And** attempts to initialize an existing revision ID without `--parent-rev` fail with exit code `1`.

### User Story 2 — Triage Requirements by Confirmation Status (Priority: P1)
As a Platform Reviewer, I want requirements triaged into `CONFIRMED`, `PROPOSED`, and `UNRESOLVED` states, so that unverified model inferences cannot masquerade as human-approved intent.

**Acceptance Criteria:**
* **Given** a structured requirement with `status: CONFIRMED`,
* **When** it lacks an explicit, non-null `confirmed_by` human identifier,
* **Then** `CHK-REQUIREMENTS-TRIAGE` marks the check as `FAIL`, records the defect in `check_events.jsonl`, and exits with code `1`.
* **And** requirements with `PROPOSED` or `UNRESOLVED` status do not claim confirmed authority.

### User Story 3 — Real Filesystem Containment & Symlink Boundary Enforcement (Priority: P1)
As a DevSecOps Engineer, I want all store and revision writes restricted to canonical resolved paths within the authorized parent directory, so that directory traversal or symlink attacks cannot escape the workspace.

**Acceptance Criteria:**
* **Given** a `--store-dir` pointing outside the authorized workspace parent (e.g., `../../etc`),
* **When** any CLI command is executed,
* **Then** `assertRealFsContainment` throws `CONTAINMENT_VIOLATION` and terminates execution immediately before any disk reads or writes.

---

## 3. Functional Requirements

* **REQ-AUTH-01:** Pure Node.js built-ins only (`node:fs`, `node:path`, `node:crypto`). Zero external dependencies (`npm install` not permitted).
* **REQ-AUTH-02:** Deterministic JSON serialization with recursively sorted object keys.
* **REQ-AUTH-03:** Identifier validation: revision IDs must match `^[a-zA-Z0-9_-]{1,64}$` without path separators.
* **REQ-AUTH-04:** Append-only check event stream (`check_events.jsonl`) preserving historical execution failures.
* **REQ-AUTH-05:** Materialized ledger consistency audit (`verify-consistency` command).

---

## 4. Verification Approach

Verified by the repeatable synthetic test suite in `test/runner.js` (13 comprehensive assertions covering revision creation, parent invalidation, symlink rejection, check execution, and event log consistency).
