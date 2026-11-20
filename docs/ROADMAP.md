# Agent Development Factory — Capability Roadmap

**Last updated:** 20 November 2026
**Measured against:** `Agent-Development-Factory-Baseline-v1.0.0` (requirements ADF-001 … ADF-040)
**Full requirement-by-requirement delta:** [`specs/audit/06-baseline-v1.0.0-delta.md`](https://github.com/rjmad1/AgentDevelopmentFactory/blob/main/specs/audit/06-baseline-v1.0.0-delta.md)

This page is the honest status of the Factory: what works today, what is designed but unbuilt, and what an enterprise agent factory needs that the baseline does not yet enumerate. It exists because the baseline requires full-lifecycle capability claims to carry an honest present/future status (ADF-002) and completion reports to match inspected outputs (ADF-039).

**How to read the status column**

| Status | Meaning |
|---|---|
| ✅ Implemented | Code exists and was inspected; behaves as described within the stated scope |
| 🟡 Partial | Some behavior exists with named missing pieces |
| 🔴 Planned | Specified or designed, no implementation found |
| ⚪ Pending decision | Target capability with no owner decision yet |

No row on this page claims a test result. The last full verification run is recorded in `reports/eval_results.json`; this audit executed nothing.

---

## 1. What is implemented today

### Authoring and integrity (Tier 1, Node.js)

| Capability | Status | Where |
|---|---|---|
| Zero-dependency SHA-256 hashing and deterministic JSON canonicalisation | ✅ | `src/core.js` |
| Lexical + realpath filesystem containment, traversal rejection | ✅ | `src/core.js`, `agent_factory/security/policy.py` |
| Immutable revision store preserving the original brief bytes | ✅ | `src/cli.js init-revision` |
| Requirement triage into `CONFIRMED` / `PROPOSED` / `UNRESOLVED` | ✅ | `src/core.js` |
| Append-only check event stream + history consistency verification | ✅ | `src/cli.js run-check`, `verify-consistency` |
| Universal MCP Tool Schema Importer | ✅ | `src/cli.js import-mcp-tool`, `src/core.js importMcpToolSchema` |
| Universal Agent Spec YAML compiler & Spec Compliance | ✅ | `src/cli.js export-agent-spec`, `src/core.js exportAgentSpecYaml` |
| Automated Requirements Scaffolder & Confirmation Rigor | ✅ | `src/cli.js scaffold-requirements`, `src/core.js scaffoldRequirementsTemplate` |
| Zero-Install Diagnostic Doctor & Port Canary | ✅ | `src/cli.js doctor`, `src/core.js runPlatformDoctor` |
| Solution Complexity Triage (S1/S2 Simplicity Rule) | ✅ | `src/cli.js triage-solution`, `src/core.js triageSolutionComplexity` |
| Token & Cost Feasibility Estimator (S5 Anthropic Benchmark) | ✅ | `src/cli.js estimate-cost`, `src/core.js estimateTokenAndCostFeasibility` |
| OWASP Agentic Top 10 Threat Modeler (ASI01-ASI05) | ✅ | `src/cli.js threat-model`, `src/core.js evaluateAgentThreatModel` |

### Control plane (Tier 2, Python)

| Capability | Status | Where |
|---|---|---|
| `UniversalAgentSpec` Pydantic model + JSON Schema export | 🟡 — core fields only; see §2 | `agent_factory/specs/schema.py` |
| 11-stage lifecycle finite state machine | ✅ | `agent_factory/control_plane/orchestrator.py` |
| SQLite task ledger + append-only JSONL event log | 🟡 — no divergence detection between the two | `agent_factory/control_plane/task_ledger.py` |
| Deploy / rollback / suspend / retire | ✅ | `agent_factory/control_plane/lifecycle.py` |
| Owner approval token gate for risk-classified work | ✅ | `agent_factory/security/approval_gate.py` |
| Policy enforcement: path access, tool allowlist, spend ceiling | ✅ | `agent_factory/security/policy.py` |
| Secret redaction | ✅ | `agent_factory/security/redactor.py` |
| Capability registry with verification status and quarantine | 🟡 — no schemas, effects or targets on a record | `agent_factory/registry/capability_registry.py` |
| Skill quarantine and security findings | ✅ | `agent_factory/security/` |
| Layer 1 Solution Complexity Triage (No-Agent, Workflow, Agent, Multi-Agent) | ✅ | `agent_factory/control_plane/intake.py` |
| Layer 1 Token & Cost Feasibility Estimator (15x multi-agent multiplier) | ✅ | `agent_factory/control_plane/intake.py` |
| Layer 1 Intent Capture & Clarification Engine | ✅ | `agent_factory/control_plane/intake.py` |
| Layer 2 Agent Pattern Library & A2A Topology Generator | ✅ | `agent_factory/workbench/pattern_library.py` |
| Layer 2 Skill Packaging (conforming to agentskills.io S8 specification) | ✅ | `agent_factory/workbench/skill_packager.py` |
| Layer 6 OWASP Top 10 for Agentic Applications Threat Modeler | ✅ | `agent_factory/security/threat_modeler.py` |

### Workbench and runtime

| Capability | Status | Where |
|---|---|---|
| Ephemeral isolated workspace provisioning | ✅ | `agent_factory/workbench/workspace.py` |
| Code and test synthesis | ✅ | Pattern-driven generator synthesizing architecture-specific implementations (`router`, `orchestrator_worker`, `evaluator_optimizer`, `prompt_chain`, `data_processor`) in `agent_factory/workbench/code_generator.py` |
| Sandboxed local OS process execution with wall-clock limit | ✅ | `agent_factory/runtime/local_process.py` |
| Deterministic graders (exit code, file existence, byte size, JSON structure, Markdown structure, secret leak) | ✅ | `agent_factory/evals/graders.py` |
| Evaluation runner | 🟡 — real process execution, but a single hardcoded case set | `agent_factory/evals/runner.py` |
| Release packaging, checksums, zip bundle | 🟡 — not an agent pack; records a perfect score when nothing ran | `agent_factory/workbench/packager.py` |
| Self-healing remediation loop | ✅ | `agent_factory/remediation/engine.py` |
| OmniRoute / Hermes adapters | 🟡 — HTTP interface only; no retained connection evidence, no streaming | `agent_factory/adapters/` |
| LangSmith free-tier telemetry adapter | 🟡 | `agent_factory/evals/langsmith_adapter.py` |

### Governance and operations

| Capability | Status | Where |
|---|---|---|
| Spec Kit SDD structure (features 001–004, four artifacts each) | ✅ | `specs/features/` |
| 7 binding governance policies, 7 architecture blueprints, 6 ADRs | ✅ | `specs/governance/`, `specs/architecture/` |
| Autonomous Hermes watcher loop, pre-commit hook, packet bundlers | ✅ | `scripts/`, `.hermes/` |
| CI (Node + Python), docs publishing, wiki sync | ✅ | `.github/workflows/` |
| MkDocs Material documentation portal | ✅ | `mkdocs.yml`, `docs/` |

---

## 2. Planned — the baseline delta

Ordered by severity. Each row names the proposed Spec Kit feature folder; none of these folders exist yet.

### Priority 1 — the Factory is not yet generic

| Item | Requirement | Feature |
|---|---|---|
| Replace the hardcoded generator with spec-driven synthesis: two different briefs must produce materially different agents | ADF-001 | `005-spec-driven-agent-synthesis` |
| Generate and revise **agent instructions**, not just Python — tailored to the brief, consistently re-derived when a rule changes | ADF-013 | `005` |
| Derive edge cases and guardrails from declared risks, and state which controls are instruction-level only | ADF-014 | `005` |
| Extend `UniversalAgentSpec` to the full universal field set (intended users, scope/exclusions, workflow and escalation, knowledge and freshness, memory and retention, confidentiality, human-intervention points, failure behavior, cost constraints, operations) with explicit `UNRESOLVED` / `N/A` markers | ADF-010 | `005` |

### Priority 1 — evidence honesty

| Item | Requirement | Feature |
|---|---|---|
| Never publish an unrun evaluation as a score. `NOT RUN` must propagate to the manifest and every report | ADF-022 | `006-evidence-applicability-ledger` |
| Report unobserved tokens, calls and cost as **unknown**, not `0`. Every metric carries its denominator, case set, mode, environment, model/config and sample count | ADF-023 | `006` |
| Attach dependency identities (requirement, instruction, tool contract, model config, dataset, rubric, checker version) to each result so a changed input marks prior evidence stale | ADF-027 | `006` |
| Detect SQLite↔JSONL ledger divergence; declare interrupted-write recovery | ADF-028 | `006` |
| Protect same-version release overwrite and workspace deletion | ADF-026 | `006` |

### Priority 2 — intake quality

| Item | Requirement | Feature |
|---|---|---|
| Adaptive clarification rounds that refine rather than repeat | ADF-007 | `007-clarification-and-certainty` |
| Conflict detection: contradictory consequential rules surface a visible choice instead of a silent precedence | ADF-009 | `007` |
| Carry `CONFIRMED` / `PROPOSED` / `UNRESOLVED` / synthetic provenance across the Node→Python boundary | ADF-008, ADF-005 | `007` |
| Machine-readable requirement↔artifact↔case↔result graph with an uncovered-requirement report | ADF-011 | `007` |

### Priority 2 — the pack is the product

| Item | Requirement | Feature |
|---|---|---|
| Emit the full agent pack contract: entry-point README, instructions, requirements, tool docs, setup notes, edge cases, evaluation assets, guardrails, review instructions, evidence status, unresolved items — complete and usable offline | ADF-012 | `008-agent-pack-contract` |
| Derive `requirements.lock` from the actual workspace instead of a literal | ADF-012 | `008` |
| Reviewer export that lets an independent reviewer challenge the actual claims | ADF-018 | `008` |
| Declare retention and deletion for transient Factory state | ADF-017 | `008` |

### Priority 2 — supervised evaluation

| Item | Requirement | Feature |
|---|---|---|
| `EvaluationPlan` / `EvaluationRun` entities with coverage counts: defined, executed, passed, failed, blocked, currently applicable | ADF-019 | `009-supervised-evaluation-control-plane` |
| Prerequisite verification that **blocks** a run; scoped authorization renewed when scope changes; stop semantics with partial results retained | ADF-021, ADF-020 | `009` |
| Boundary and false-claim case packs (unauthorized action, data-boundary breach, prompt injection, false verification) that cannot be averaged away | ADF-025 | `009` |
| Cross-target comparison on matched case sets with declared adapter differences | ADF-024 | `009` |

### Priority 3 — portability

| Item | Requirement | Feature |
|---|---|---|
| Target profiles declaring version, documentation reference, supported features, gaps, translation rules, semantic loss and export maturity — no false parity | ADF-015 | `010-target-profiles-and-adapters` |
| Google ADK target (named explicitly in the baseline) | ADF-015 | `010` |
| Full capability contracts: input/output schema, declared effects, data boundaries, credential reference, idempotency, timeout/retry, failure escalation, supported targets — so mismatch surfaces before integration | ADF-016 | `010` |
| Retain evidence of actual Hermes / OmniRoute / MCP behavior before relying on it | ADF-031, ADF-040 | `010` |
| SSE streaming in model adapters (carried from GAP-05) | — | `010` |

### Priority 3 — access and hosted use

| Item | Requirement | Feature |
|---|---|---|
| Guided non-coder authoring surface sharing one specification with the technical path | ADF-003 | `011-hosted-access-and-byok` |
| Wizard with back/edit, honest stage progress, saved-vs-generated distinction | ADF-006 | `011` |
| Server-side password enforcement; direct-route denial | ADF-030 | `011` |
| Guest sessions: expiry, revocation, isolation under replay and races | ADF-032 | `011` |
| BYOK: isolated, provider-compatible, secret-safe, with a credential-failure taxonomy and `SIMULATED` labelling | ADF-033 | `011` |
| Payer / limit / stop disclosure before any billable use | ADF-034 | `011` |
| Cloudflare hosted path, end-to-end tested at the hosted address, dependencies disclosed | ADF-035 | `011` |
| Error, reload, cancel and accessibility behavior without false success | ADF-037 | `011` |
| Release record naming build version, reviewer identity, test scope, raw evidence, unresolved defects, go/no-go | ADF-036 | `011` |
| Enforce `max_steps`, `max_tokens`, `max_parallel_workers` (declared today, unenforced) | ADF-038 | `009` |

---

## 3. Pending — enterprise capabilities beyond the baseline

The baseline defines a correct, honest agent factory. It does not yet enumerate what an enterprise fleet needs to operate one at scale. These are candidate capabilities, **not yet approved and not yet specified** — each needs an owner decision before it enters the roadmap above.

### Agent engineering depth
- **Agent pattern selection.** Choose between single-shot, tool-using, retrieval-grounded, stateful, workflow and multi-agent topologies from the brief, instead of always emitting one shape.
- **Prompt/instruction registry.** Versioned instruction artifacts with diffs, rollback and a link from each evaluation result to the exact instruction revision it tested.
- **Knowledge and retrieval engineering.** Ingestion with source provenance, freshness windows, index lifecycle, and evaluation of retrieval quality separately from agent quality.
- **Memory engineering.** Declared tiers (per-turn, per-session, durable), retention limits, and a deletion path.
- **Multi-agent contracts.** Handoff schemas, termination conditions, fan-out bounds and loop detection — currently nothing prevents an unbounded delegation chain.

### Evaluation maturity
- **Golden dataset management.** Versioned case sets with ownership, so a regression suite is an asset rather than a fixture folder.
- **LLM-as-judge with calibration.** Judge agreement measured against human labels, with the agreement rate published beside the score.
- **Adversarial and red-team pack.** Prompt injection, instruction override, data exfiltration, tool misuse and jailbreak cases run on every revision.
- **Regression gating.** Every revision evaluated in CI; nightly full regression; a score drop blocks promotion.
- **Cross-target benchmark parity.** The same case set run on every declared target, differences published.

### Observability and cost
- **Real usage telemetry.** Token, call and latency capture from the provider response, which is the precondition for ADF-023 being satisfiable at all rather than merely honest.
- **Distributed tracing.** OpenTelemetry spans per agent step and tool call, correlated with the evidence ledger.
- **Cost accounting and budget enforcement.** Per-project and per-run ceilings enforced at the router, with projections before a run starts.
- **Drift and alerting.** Detection of output-quality, cost and latency drift against a baseline, with an alert route.
- **Semantic caching and rate-limit handling.** Router-level fallback, retry budgets and cache for repeated deterministic calls.

### Security and supply chain
- **Secrets management.** Vault or OS keychain rather than literals and environment defaults — note the `api_key="local_omniroute_token"` default in `omniroute_adapter.py`.
- **Generated-code scanning.** SAST, dependency CVE and license scanning applied to synthesised agents before packaging.
- **SBOM per release.** Dependency and license inventory emitted with each pack.
- **Egress control.** Declared and enforced network destinations per agent, not just a tool allowlist.
- **Tenancy and RBAC.** Project-scoped roles; today every operation is the owner's.

### Governance and compliance
- **Agent catalog with lineage.** Every deployed agent discoverable with owner, version, dependencies, evaluation status and deprecation date.
- **Data governance.** PII classification on inputs and artifacts, retention schedules, and an erasure path.
- **Regulatory mapping.** EU AI Act risk classification, NIST AI RMF and ISO/IEC 42001 control mapping — an enterprise procurement prerequisite, and a natural extension of `RiskClassification`.
- **Human-in-the-loop review queue.** A durable queue with assignment and audit trail, rather than a single owner token.
- **Incident response.** Runbook, severity ladder and on-call path for a deployed agent causing an unintended effect.

### Delivery
- **Deployment targets beyond local process.** Container image, serverless function, Cloudflare Worker, with environment promotion dev → stage → prod.
- **Spec schema versioning and migration.** `schema_version` is pinned at `1`; there is no migration path for existing packs when it moves.

---

## 4. Known blocking defects

Three findings in §1–2 are defects rather than absent features, and gate any claim that the Factory works end to end:

1. **The generator is not generic** (`code_generator.py`, `test_generator.py`, `runner.py`) — one business workflow is hardcoded as the product. This is the exact drift the baseline names first.
2. **An unrun evaluation becomes a perfect score** (`packager.py`) — the release manifest defaults to `{"efficacy": 1.0, "safety": 1.0}` when no evaluation ran.
3. **Unobserved cost is reported as zero** (`runner.py`, `metrics.py`) — and the `cost_usd == 0.0` term in the pass gate is therefore vacuous.

---

## 5. Change control

This roadmap is derived from `specs/audit/06-baseline-v1.0.0-delta.md` and must be updated in the same change as any status transition. Status may only move to ✅ with a specification, a passing test and retained evidence, per the *No Spec without Verification* rule in [`specs/README.md`](https://github.com/rjmad1/AgentDevelopmentFactory/blob/main/specs/README.md).
