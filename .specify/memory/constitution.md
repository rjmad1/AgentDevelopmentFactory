# Agent Development Factory Constitution

**Effective Date:** November 20, 2026  
**Status:** ENFORCEABLE & BASELINED  
**Governing Standard:** GitHub Spec Kit Constitution Framework  

---

## I. Core Engineering Principles

### 1. Specification-First Development (NON-NEGOTIABLE)
No application code shall be authored, modified, or refactored without prior specification alignment. Every feature begins with an explicit, reviewed specification (`spec.md`, `plan.md`, `tasks.md`, `checklist.md`) in `specs/features/`.

### 2. Strict Vendor Agnosticism & Harness Decoupling
Agent specifications must remain completely decoupled from prompt formats and proprietary runtime harnesses (`REQ-GOV-01`). Agents synthesized by the factory must execute identically across Standalone Local Processes, Hermes Harness, and containerized runtimes via standardized provider adapters.

### 3. Evidence-Based Completion
Narrative assertions, conversational summaries, or plain-text claims of success do not constitute verification (`REQ-GOV-04`). State transitions require cryptographically verifiable execution evidence: exit code `0`, output files, SHA-256 digests, and append-only check event records (`check_events.jsonl`). If evidence is absent, the state machine halts in `BLOCKED`.

### 4. Zero Unapproved Paid Spend
The factory operates under a hard stop at a `$0.00` paid software/inference ceiling (`REQ-GOV-05`). Automatic promotion to paid commercial APIs upon rate limit or free-tier exhaustion is strictly forbidden without an explicit, human-signed spend authorization token.

### 5. Deletion Before Addition & Ponytail Minimalism
Before introducing new abstractions, libraries, or files, engineers must evaluate whether existing code can be refactored, simplified, or deleted. Keep the codebase lean. Every line of code is a liability. Abstractions for single-use code are prohibited.

---

## II. Security & Sandbox Invariants

### 1. Real Filesystem Containment
All file reading, writing, and workspace provisioning must resolve to canonical paths strictly contained within authorized parent boundaries (`REQ-SEC-03`). Lexical path traversals (`../`) and resolved symlink escapes must be rejected before disk operations occur.

### 2. Active Secret Redaction
All execution logs, error traces, and telemetry streams must pass through real-time regex pattern scanning (`REQ-SEC-01`) to mask OpenAI, Anthropic, AWS, GitHub, and bearer credentials prior to storage or display.

### 3. Static AST Quarantine
Synthesized Python agent code must undergo Abstract Syntax Tree (AST) inspection (`REQ-SEC-02`) before execution. Arbitrary subprocess execution (`os.system`, `subprocess.Popen`) and dynamic evaluation (`eval`, `exec`) trigger immediate AST quarantine.

---

## III. Dual-Stack Operational Model

### Tier 1: Authoring Front-End (Node.js)
* Pure Node.js built-ins (`node:fs`, `node:path`, `node:crypto`). Zero external npm dependencies.
* Owns fast requirement intake, confirmation triage (`CONFIRMED`, `PROPOSED`, `UNRESOLVED`), and surgical packet bundling for the Hermes fleet.

### Tier 2: Industrial Factory Back-End (Python)
* Python 3.11+ modular platform (`agent_factory/`).
* Owns the 11-stage FSM Control Plane, Capability Registry, Workbench synthesis, isolated process runtime, and Deep Evaluator quality gates.

---

## IV. Quality Gates & Release Criteria

Every candidate agent must satisfy the five mandatory release gates before promotion:
1. **Efficacy Gate:** Score $\ge 0.95$ across deterministic benchmark fixtures.
2. **Safety Gate:** Score $= 1.00$ (zero unredacted secrets, zero AST quarantine violations).
3. **Cost Gate:** Score $= \$0.00$ software cost.
4. **Reproducibility Gate:** Rebuilding a packaged release from its manifest and lockfile yields identical cryptographic SHA-256 digests.
5. **Approval Gate:** High-risk capabilities require an explicit, structured human approval record.
