# Factory Requirements Catalog

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** APPROVED & BASELINED  
**Scope:** Universal Agent Development Factory (Hermes Orchestrator & Multi-Harness Execution)  

---

## 1. Overview and Taxonomy

This requirements catalog establishes the definitive functional and non-functional specifications for the Agent Development Factory. Derived from the *Master Directive* and the 52-page *Full-Lifecycle Engineering Handbook*, it synthesizes all explicit constraints, implicit operational mandates, and rigorous risk boundaries into actionable engineering requirements.

### Risk Classifications:
* **CRITICAL:** Failure compromises host security, secret confidentiality, data boundaries, or causes irreversible state corruption.
* **HIGH:** Failure breaks agent reproducibility, runtime vendor neutrality, or produces unverified "Done" verdicts.
* **MEDIUM:** Failure impacts throughput, resource efficiency, latency, or requires manual human remediation.
* **LOW:** Minor cosmetic, reporting, or developer ergonomics degradation.

### Status Indicators:
* `MANDATED`: Required by contract/specification; ready for implementation.
* `IN_PROGRESS`: Currently being designed, wired, or integrated.
* `VERIFIED`: Implemented and backed by deterministic test evidence.
* `BLOCKED`: Dependency unresolved or requires explicit human authorization.

---

## 2. Comprehensive Requirements Catalog

### 2.1 Governance & Architecture Principles (GOV)

| Req ID | Description | Source Section | Business Importance | Technical Interpretation | Dependencies | Status | Validation Method | Acceptance Criteria | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-GOV-01** | **Strict Vendor Agnosticism** | Directive §2.1, Handbook §1, §8 | Prevents catastrophic vendor lock-in to any model, runtime, or orchestrator. | Decouple agent specification from prompt formats. Core contracts, registry, and evaluations must run across runtimes via adapters. | None | MANDATED | Multi-target compilation and test execution. | Agent runs across at least two independent runtimes (e.g., Local Process and Hermes Harness) without changing core spec. | CRITICAL |
| **REQ-GOV-02** | **Full-Lifecycle Autonomy** | Directive §2.2, Handbook §5, §11 | Reduces human engineering overhead from requirement to retirement. | Implement 20-stage automated lifecycle from intake to retirement with clear state machine transitions. | REQ-SPEC-01, REQ-REG-01 | MANDATED | Automated lifecycle progression test. | System executes from requirement to package without human stalls on approved paths. | HIGH |
| **REQ-GOV-03** | **100% Reproducible Artifacts** | Directive §2.3, Handbook §18, App F | Ensures auditability, compliance, and deterministic rollbacks. | Every agent release must bundle pinned spec, dependency lockfile, test fixtures, model ID, and adapter version with SHA-256 hashes. | REQ-SPEC-01 | MANDATED | Hash verification & clean-room build test. | Re-building a tagged package produces identical cryptographic digest and behavior. | HIGH |
| **REQ-GOV-04** | **Evidence-Based Completion** | Directive §2.5, Handbook §13, App P | Eliminates hallucinations, false "Done" claims, and phantom successes. | State transitions require cryptographically verifiable execution evidence (output files, exit codes, test logs). Narrative claims without artifacts are rejected. | REQ-EVAL-01 | MANDATED | Negative assertion test (simulate missing artifact). | State machine throws validation error if artifact bytes or exit codes are absent. | CRITICAL |
| **REQ-GOV-05** | **Zero Unapproved Paid Fallback** | Directive §8, Handbook §3, §16, ADR003 | Protects budget and prevents surprise cloud billing spikes. | Hard stop at paid ceiling ($0 unless overridden). No automatic promotion to paid proprietary models upon rate limit or failure. | REQ-PROV-01 | MANDATED | Quota exhaustion canary probe. | Execution parks in `BLOCKED` with budget error instead of routing to unverified paid API. | CRITICAL |

---

### 2.2 Universal Agent Specification Standard (SPEC)

| Req ID | Description | Source Section | Business Importance | Technical Interpretation | Dependencies | Status | Validation Method | Acceptance Criteria | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-SPEC-01** | **Machine-Readable Universal Schema** | Directive §5.B, Handbook §7, App C | Uniform contract for all agents across diverse toolchains. | Author JSON Schema and Pydantic models defining identity, purpose, inputs, outputs, policy, limits, state, and evaluation targets. | None | MANDATED | `jsonschema.validate()` and Pydantic parsing test. | Syntactically and semantically validates sample agent specs; rejects extra/malformed fields. | HIGH |
| **REQ-SPEC-02** | **Explicit Authority & Permission Boundaries** | Directive §5.B, Handbook §7, §15 | Enforces principle of least privilege in agent definitions. | Spec must classify tool effects into `READ_PUBLIC`, `READ_PRIVATE`, `WRITE_LOCAL_DRAFT`, `CHANGE_ACCOUNT`, `SEND_PUBLISH`, `SPEND_DELETE`. | REQ-SPEC-01 | MANDATED | Permission matrix verification test. | Agent requesting unapproved effect level fails validation before build. | CRITICAL |
| **REQ-SPEC-03** | **Execution Limits & Resource Quotas** | Directive §5.B, Handbook §7, §16 | Prevents runaway agent loops, disk exhaustion, and socket leaks. | Specify `max_steps`, `max_wall_time_seconds`, `max_tokens`, `paid_spend_ceiling`, and `max_workers` in spec. | REQ-SPEC-01 | MANDATED | Boundary threshold enforcement test. | Runtime terminates execution cleanly when step or wall-time ceiling is reached. | HIGH |
| **REQ-SPEC-04** | **Failure Handling & Denial Declarations** | Directive §5.B, Handbook §7 | Predictable, fail-safe degradation on permission denials. | Spec defines explicit `on_denial` policy (`stop_and_report`, `quarantine`, `human_escalate`). Bypassing denied guards is strictly forbidden. | REQ-SPEC-01 | MANDATED | Guard denial simulation test. | Agent reports structured denial status without attempting alternative prohibited commands. | HIGH |

---

### 2.3 Capability Registry & Dynamic Discovery (REG)

| Req ID | Description | Source Section | Business Importance | Technical Interpretation | Dependencies | Status | Validation Method | Acceptance Criteria | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-REG-01** | **Unified Typed Capability Registry** | Directive §5.C, Handbook §10 | Single source of truth for available infrastructure building blocks. | Registry manages typed entities: `MODEL`, `PROVIDER`, `FRAMEWORK`, `HARNESS`, `RUNTIME`, `TOOL`, `MCP`, `SKILL`, `EVALUATION`. | None | MANDATED | Registry CRUD & resolution test. | Capable of registering, querying, resolving dependency graphs, and deprecating capabilities. | HIGH |
| **REQ-REG-02** | **Live Environment Discovery** | Directive §3, Handbook §16 | Grounding in reality; prevents building against phantom tools. | Inspect actual host hardware, OS, installed Python/Node packages, active socket listeners (20128, 31415), and MCP servers. | REQ-REG-01 | VERIFIED | Live execution report inspection. | Complete factual report matching `FACTORY_ENVIRONMENT_DISCOVERY_REPORT.md`. | HIGH |
| **REQ-REG-03** | **Capability Verification Before Availability** | Directive §5.C, Handbook §10 | Prevents dispatching workloads to dead or unverified services. | Capabilities cannot be marked `ACTIVE` without a successful synthetic probe or health check. | REQ-REG-01 | MANDATED | Negative capability probe test. | Unreachable endpoints or unverified models are marked `UNVERIFIED` / `INELIGIBLE`. | HIGH |
| **REQ-REG-04** | **Governed Skill & MCP Quarantine** | Directive §9, Handbook §9, §15 | Defends host against malicious skills or rogue MCP servers. | Newly discovered skills undergo 5-step quarantine: Inspect -> License check -> AST security audit -> Sandbox test -> Promotion. | REQ-REG-01, REQ-SEC-01 | MANDATED | Malicious payload injection test. | Unsigned/unreviewed skills are isolated in quarantine and forbidden from execution. | CRITICAL |

---

### 2.4 Control Plane & Autonomous Engineering Workbench (CTL / WB)

| Req ID | Description | Source Section | Business Importance | Technical Interpretation | Dependencies | Status | Validation Method | Acceptance Criteria | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-CTL-01** | **Stateful 3-Plane Architecture** | Directive §5.A, Handbook §5, §11 | Prevents state corruption and ensures fault-tolerant resumption. | Architecturally separate **Control Plane** (decisions/gates), **Execution Plane** (sandboxed workers), and **Evidence Plane** (immutable ledger). | None | MANDATED | Crash-and-resume integration test. | Control plane recovers workflow state from durable SQLite/JSON ledger after process crash. | CRITICAL |
| **REQ-WB-01** | **Isolated Workspace Management** | Directive §5.D, Handbook §6, App F | Prevents concurrent agent file collisions and host contamination. | Create isolated workspace directories per project/run with dedicated `src`, `tests`, `fixtures`, `evidence`, and clean environment variables. | None | MANDATED | Concurrent workspace creation test. | Two builds run in separate workspaces without file or git state interference. | HIGH |
| **REQ-WB-02** | **Automated Code & Test Generation** | Directive §7, Handbook §5, §11 | Turns high-level specs into runnable, tested implementations. | Autonomous code synthesis producing executable Python modules, tool wrappers, and pytest unit suites matching the spec. | REQ-SPEC-01, REQ-WB-01 | MANDATED | Autonomous generation and pytest execution. | Generated code passes syntax validation, type checks, and basic unit assertions. | HIGH |
| **REQ-WB-03** | **Bounded Autonomous Remediation** | Directive §7, Handbook §14, App J | Enables autonomous bug fixing without unbounded spending loops. | Implement stateful repair loop (`DETECTED` -> `PROPOSED` -> `AUTHORIZED` -> `VERIFIED` -> `PROMOTED`) capped at max 3 retries. | REQ-WB-02, REQ-EVAL-01 | MANDATED | Synthetic failure injection & remediation test. | Engine diagnoses failure, applies surgical patch, verifies fix, or parks in `BLOCKED` on budget limit. | HIGH |

---

### 2.5 Multi-Target Provider & Runtime Adapters (ADP / RT)

| Req ID | Description | Source Section | Business Importance | Technical Interpretation | Dependencies | Status | Validation Method | Acceptance Criteria | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-ADP-01** | **Universal Adapter Contract** | Directive §8, Handbook §8, App L | Enables plugging in arbitrary model providers and agent harnesses. | Define `ProviderAdapter` and `AgentRuntime` abstract interfaces supporting P0 (Text), P1 (Tools), P2 (Policy), P3 (State), P4 (Ops). | None | MANDATED | Interface conformance test. | Implementations satisfy abstract interface methods with standardized input/output signatures. | HIGH |
| **REQ-ADP-02** | **OmniRoute Model Gateway Adapter** | Directive §8, Handbook §5, §8 | Leverages existing local multi-provider model routing. | Connect to OmniRoute loopback (`http://127.0.0.1:20128/v1`), handle OpenAI format, model selection, timeouts, and auth. | REQ-ADP-01 | MANDATED | Live socket probe & mocked test suite. | Successfully queries models and routes inference requests with proper error mapping. | MEDIUM |
| **REQ-ADP-03** | **Hermes Orchestrator Harness Adapter** | Directive §1, §3, Handbook §6, §8 | Integrates Hermes Agent as coordinating execution harness. | Map agent specs to Hermes profile tasks, worktrees, skills, and kanban entries; retrieve execution logs. | REQ-ADP-01 | MANDATED | Hermes CLI delegation test. | Factory can invoke Hermes tasks and parse output without altering core Hermes config. | HIGH |
| **REQ-RT-01** | **Standalone Local Process Runtime** | Directive §5.E, Handbook §8, §16 | Guarantees agents can run independently of any development harness. | Lightweight, direct Python runtime executing agents with timeout guards, secret injection, and stdout/stderr capture. | REQ-ADP-01 | MANDATED | End-to-end local process execution test. | Packaged agent executes independently via `python -m <agent_pkg>` and produces verifiable artifacts. | HIGH |

---

### 2.6 Evaluation, Quality Assurance & Security (EVAL / SEC)

| Req ID | Description | Source Section | Business Importance | Technical Interpretation | Dependencies | Status | Validation Method | Acceptance Criteria | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-EVAL-01** | **Multi-Metric Evaluation Engine** | Directive §5.F, Handbook §13, App G | Validates agent performance beyond simple code compilation. | Measure **Efficacy** (task correctness, claim support), **Safety** (zero unauthorized effects), and **Efficiency** (wall time, tokens). | REQ-RT-01 | MANDATED | Evaluation suite execution test. | Produces structured evaluation report with deterministic grades and exact metric denominators. | HIGH |
| **REQ-EVAL-02** | **Standard Evaluation Pack (A01-A15)** | Handbook §13, App G | Standardized quality benchmark covering edge and failure modes. | Implement core suite: A01 (Contract success), A02 (Missing evidence), A03 (Truncation), A04 (Approval), A05 (Recovery), A09 (Dedup). | REQ-EVAL-01 | MANDATED | Benchmark execution against baseline agent. | All core scenarios evaluated; passing and refusing cases verified. | HIGH |
| **REQ-SEC-01** | **Secret Isolation & Redaction** | Directive §10, Handbook §15, App H | Prevents catastrophic credential leaks in logs, prompts, or git. | Spec uses named references only (e.g. `API_KEY_REF`). Secrets injected only at execution boundary; logs filtered with regex redaction. | None | MANDATED | Redaction unit test with simulated secrets. | No secret tokens or authorization headers appear in logs, evidence files, or git commits. | CRITICAL |
| **REQ-SEC-02** | **Three-Tier Risk-Based Approval Gates** | Directive §10, Handbook §11, §15 | Balances autonomy with human control for consequential actions. | Low Risk (Autonomous approval); Medium Risk (Explicit policy check); High Risk (Mandatory human approval token before execution). | REQ-CTL-01 | MANDATED | Gate denial and approval bypass test. | High-risk actions park in `WAITING_FOR_APPROVAL` and refuse execution without valid human token. | CRITICAL |

---

### 2.7 Packaging, Release & Operations (OPS)

| Req ID | Description | Source Section | Business Importance | Technical Interpretation | Dependencies | Status | Validation Method | Acceptance Criteria | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-OPS-01** | **Reproducible Release Packaging** | Directive §11, Handbook §18, App I | Frictionless distribution and deterministic deployment. | Generate standardized release bundle: `manifest.json`, frozen `agent.yaml`, `src/`, `tests/`, `lockfile`, and `checksums.sha256`. | REQ-WB-02, REQ-EVAL-01 | MANDATED | Package build and extraction verification. | Release package can be unzipped in clean scratch directory and pass verification without network fetches. | HIGH |
| **REQ-OPS-02** | **Deterministic Rollback & Suspension** | Directive §11, Handbook §18, App K | Instant disaster recovery if deployed agent drifts or fails. | Provide rollback command restoring prior verified release bundle; support emergency `SUSPEND` state revoking execution. | REQ-OPS-01 | MANDATED | Simulated failure & rollback drill. | State reverts cleanly to previous version; active processes drained without orphaned locks. | HIGH |
| **REQ-OPS-03** | **Factory Operational CLI & Observability** | Directive §11, Handbook §17, App R | Developer visibility into factory state, projects, and queues. | Provide `factory` CLI with commands: `status`, `intake`, `build`, `test`, `eval`, `remediate`, `package`, `deploy`, `rollback`. | REQ-CTL-01 | MANDATED | CLI end-to-end command execution. | All CLI commands function, return structured tables/JSON, and update the persistent ledger. | MEDIUM |
