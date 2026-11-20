# Audit Report 06: Baseline v1.0.0 Requirement Delta (ADF-001 … ADF-040)

**Audit ID:** AUD-06-BASELINE-DELTA
**Date:** November 20, 2026
**Indicative specification:** `Agent-Development-Factory-Baseline-v1.0.0` (20 November 2026) — documents 01–12, authoritative requirement set in `02_REQUIREMENTS.md`, verdict vocabulary and check IDs in `08_ACCEPTANCE_AND_DRIFT_MATRIX.md`.
**Status:** BASELINED
**Method:** Read-only source and documentation inspection. **No tests were executed for this audit.** Every row's execution outcome is therefore `NOT RUN here`.

---

## 1. Inspected scope

| Inspected | Not inspected |
|---|---|
| `agent_factory/**` (all 28 modules), `src/core.js`, `src/cli.js`, `scripts/**`, `tests/**` (names only), `specs/**`, `docs/**`, `mkdocs.yml`, `.github/workflows/**`, `requirements.txt`, `package.json` | Test execution, `extracted_handbook.txt`, full body text of every archived `specs/archive/2026-11-03-baseline/*.md`, `data/factory_state.db` contents, `releases/*.zip` contents |

Per the baseline's instruction: *not found in one file is not absent from the entire product*. `MISSING` below always names the inspected scope.

## 2. Verdict summary

| Verdict | Count | Requirements |
|---|---|---|
| ALIGNED | 0 | — |
| PARTIAL | 21 | ADF-002, 004, 005, 008, 010, 011, 012, 015, 016, 017, 018, 019, 020, 022, 025, 026, 028, 029, 031, 034, 036, 038, 039, 040 (24 incl. mixed rows) |
| MISSING | 11 | ADF-003, 006, 007, 009, 013, 014, 021, 024, 027, 030, 032, 033, 035, 037 |
| CONFLICT | 4 | ADF-001, 022 (manifest default), 023, 025 (cost gate) |

The authoritative per-requirement verdicts are in §3; the counts above are indicative only.

## 3. Requirement-to-check delta matrix

| Req | Check | Verdict | Implementation reference | Gap and user impact |
|---|---|---|---|---|
| ADF-001 | V01 | **CONFLICT** | `agent_factory/workbench/code_generator.py:11-60`, `test_generator.py:13-138`, `evals/runner.py:39-92` | The synthesiser emits a fixed `DataAnomalyAnalyzer` CSV-statistics class, fixed pytest fixtures and a fixed grader scenario (`anomaly_report.md`, `summary_ledger.json`, three literal Markdown headings) regardless of the brief. Two substantially different briefs produce the same agent. This is the exact "one business workflow is the product" drift the baseline forbids. |
| ADF-002 | V02 | PARTIAL | `control_plane/orchestrator.py:17` (`FactoryStage`), `control_plane/lifecycle.py:22-95` (deploy/rollback/suspend/retire) | Stages and retirement exist; monitoring, improvement and per-capability honest status are absent. Resolved by `docs/ROADMAP.md` (this change). |
| ADF-003 | V03 | MISSING | inspected: `src/`, `agent_factory/`, `scripts/` | No non-coder surface at all. Both entry points are CLIs requiring JSON/YAML fixtures. |
| ADF-004 | V04 | PARTIAL | `specs/architecture/adrs/ADR-001…006`, `security/approval_gate.py:29-50` | ADRs record rationale; an owner token gates risk. No per-project decision record separating architect rationale from owner instruction, and no machine barrier preventing an assistant-generated requirement from being recorded as confirmed. |
| ADF-005 | V05 | PARTIAL | `src/cli.js:76` (`init-revision` preserves brief bytes), `control_plane/intake.py:66` | Node path preserves the brief in an immutable revision store. The Python path copies the prompt into `spec.purpose` and keeps no separate original-brief record, so interpretation and source are the same field. |
| ADF-006 | V06 | MISSING | inspected: whole repo | No wizard, no stage UI, no back/edit, no saved-vs-generated distinction. |
| ADF-007 | V07 | MISSING | inspected: whole repo | No clarification engine, question bank, or adaptive rounds. Fixtures `fixtures/synthetic_requirements_*.json` exist but no consumer of ambiguity. |
| ADF-008 | V08 | PARTIAL | `specs/features/001-bounded-authoring-slice/spec.md`, `src/core.js` triage | `CONFIRMED`/`PROPOSED`/`UNRESOLVED` exist in the Node authoring tier only. `UniversalAgentSpec` has no certainty, source, decision-owner or confirmation-reference field, so certainty is lost at the Node→Python boundary (see GAP-06 in audit 04). |
| ADF-009 | V09 | MISSING | inspected: `agent_factory/`, `src/` | No conflict detection. Contradictory consequential rules would pass through `RequestIntake.process_request` silently. |
| ADF-010 | V10 | PARTIAL | `specs/schema.py:75-96` | `UniversalAgentSpec` covers identity, purpose, inputs, outputs, policy, limits, state, acceptance, targets. Absent: intended users, scope/exclusions, workflow and escalation, knowledge/freshness, memory/retention, confidentiality, human-intervention points, failure behavior, cost constraints, setup/operations, unresolved decisions. No mechanism for an explicit not-applicable or unresolved marker — a missing field is simply a Pydantic default. |
| ADF-011 | V11 | PARTIAL | `specs/audit/03-implementation-traceability.md`, `specs/governance/traceability-policy.md` | Traceability is a hand-maintained Markdown matrix. No machine-readable requirement↔artifact↔case↔result graph and no uncovered-requirement report, so drift is undetectable. |
| ADF-012 | V12 | PARTIAL | `workbench/packager.py:26-110` | The release bundle contains `src/`, `tests/`, `fixtures/`, `agent.yaml`, `requirements.lock`, `rollback.md`, `checksums.sha256`, `manifest.json`. It contains **none** of the pack-contract Markdown artifacts required by baseline doc 05: entry point README, evolved instructions, requirements, tool/capability docs, setup notes, edge cases, evaluation assets, guardrails, review instructions, evidence status, unresolved items. `requirements.lock` is a hardcoded literal (`pytest==9.1.1`), not derived from the workspace. |
| ADF-013 | V13 | MISSING | inspected: `workbench/`, `adapters/` | No system-prompt or instruction compilation anywhere. The Factory generates Python source, never agent instructions, so there is nothing to tailor or re-derive when a rule changes. |
| ADF-014 | V14 | MISSING | `workbench/test_generator.py:56-138` | Four fixed CSV tests. No risk→control→case derivation, no guardrail generation, no statement of which controls are instruction-level only. |
| ADF-015 | V15 | PARTIAL | `specs/schema.py:87` (`targets` dict), `adapters/base.py`, `hermes_adapter.py`, `omniroute_adapter.py` | `targets` is a free-text `Dict[str, str]` of maturity labels. No target profile declaring name/version, documentation reference and review date, supported features, gaps, translation rules, semantic loss or export maturity. No Google ADK target (named explicitly in the baseline). |
| ADF-016 | V16 | PARTIAL | `registry/capability_registry.py:34-50` | `CapabilityRecord` carries identity, kind, version, provider, license, status, permissions, dependencies, verification evidence. Absent: input/output schema, declared effects and data boundaries, credential reference, idempotency, timeout/retry, failure/escalation behavior, supported targets. Therefore schema/permission mismatch **cannot** be surfaced before integration. |
| ADF-017 | V17 | PARTIAL | `workbench/packager.py`, `releases/` | Local bundle export works without hosted storage. Retention and deletion behavior for transient state (`data/factory_state.db`, `data/task_events.jsonl`, `workspaces/`) is undeclared. |
| ADF-018 | V18 | PARTIAL | `scripts/bundle-critic-packet.js`, `specs/contracts/hermes-packets/critic_packet.schema.json` | Critic packets serve the Factory's own development, not an agent pack's independent review. No reviewer export containing the pack's requirements, coverage and sanitized evidence with instructions to produce findings. |
| ADF-019 | V19 | PARTIAL | `evals/graders.py`, `evals/runner.py` | Six graders execute. Coverage is not modelled: no counts of cases defined / executed / passed / failed / blocked / currently applicable. |
| ADF-020 | V20 | PARTIAL | `evals/runner.py:30-114`, `runtime/local_process.py` | Honest positive: a real OS process is executed and graded — this is not a mock. But the case set is hardcoded to one agent, and there is no scope review, authorized start, inspection or stop. Per baseline T07 this must be labelled a deterministic harness result, not supervised agent evaluation. |
| ADF-021 | V21 | MISSING | inspected: `evals/`, `control_plane/` | No `EvaluationPlan`/`EvaluationRun` entity, no prerequisite verification that blocks a run, no authorization bound to a named scope, no renewed authorization on scope change. |
| ADF-022 | V22 | **CONFLICT** | `workbench/packager.py:89` | `"evaluation_scores": eval_scores or {"efficacy": 1.0, "safety": 1.0}` — when no evaluation was run, the release manifest records a perfect score. This is `NOT RUN` published as `PASSED`, the baseline's primary honesty prohibition. Separately, `control_plane/task_ledger.py` provides an append-only event log (good) but no case-level applicability state. |
| ADF-023 | V23 | **CONFLICT** | `evals/runner.py:94-104`, `evals/metrics.py:36-53` | The runner passes `model_calls=0, tokens=0, cost_usd=0.0` as literals because nothing is observed, and `EfficiencyMetrics` publishes them as measured zeros. The baseline requires unobserved compute/cost to be reported as **unknown, not zero**. No metric names its denominator, case set, mode, environment, model/config or sample count. |
| ADF-024 | V24 | MISSING | inspected: `evals/`, `adapters/` | No cross-target comparison, matched case set or disclosed adapter difference. |
| ADF-025 | V25 | PARTIAL / CONFLICT | `evals/metrics.py:45,55` | Honest positive: `safety` is a hard `1.0`/`0.0` on violation count and `passed` requires `safety == 1.00`, so a safety violation cannot be averaged away. Conflict: the only safety signal wired in `runner.py` is secret leakage; unauthorized action, data-boundary breach, injection and false-verification cases do not exist. The `cost_usd == 0.0` term in the pass gate is vacuous because the caller always supplies `0.0`. |
| ADF-026 | V26 | PARTIAL | `src/core.js` immutable revision store + `check_events.jsonl`; `workbench/workspace.py:17` | Node tier preserves revisions and append-only events. Python tier's `provision_workspace(..., clean=True)` deletes a workspace, and `packager.package_release` overwrites `releases/<agent>-v<version>.zip` for the same version without a guard. |
| ADF-027 | V27 | MISSING | inspected: `control_plane/`, `evals/` | No dependency identity (requirement, instruction, tool contract, model config, dataset, rubric, checker version) attached to a result, therefore no applicability review. A changed checker silently inherits an old pass. Highest-severity integrity gap after ADF-001. |
| ADF-028 | V28 | PARTIAL | `src/cli.js:150` (`verify-consistency`), `control_plane/task_ledger.py:124` | Node tier detects history inconsistency. The Python ledger writes both SQLite rows and a JSONL event file with no divergence detection between them and no declared interrupted-write recovery policy. |
| ADF-029 | V29 | PARTIAL | `src/core.js` lexical + realpath containment; `security/policy.py:23-54` | Containment and traversal rejection are implemented in both tiers. No evidence of link/reparse-point escape testing (baseline T11) and no concurrency-scope claim boundary stated. |
| ADF-030 | V30 | MISSING | inspected: whole repo | No service, no password enforcement. |
| ADF-031 | V31 | PARTIAL | `adapters/omniroute_adapter.py:16-45` | An OmniRoute HTTP adapter with `check_health` exists and the gateway endpoint matches the owner's policy. No evidence of a successful connection is retained; the default `api_key="local_omniroute_token"` is a literal in source; no declared capability status per integration. |
| ADF-032 | V32 | MISSING | inspected: whole repo | No session, expiry, revocation or isolation. |
| ADF-033 | V33 | MISSING | `security/redactor.py` exists (redaction only) | No BYOK path, no OpenAI/Anthropic-compatible key handling, no credential-failure taxonomy, no SIMULATED labelling. |
| ADF-034 | V34 | PARTIAL | `specs/schema.py:60` (`paid_spend_ceiling=0.0`), `security/policy.py:68`, `ADR-003` | A zero-spend ceiling and a spend validator exist. No payer/limit/stop disclosure before billable use, and no live pricing or quota check. |
| ADF-035 | V35 | MISSING | inspected: `.github/workflows/`, repo root | No Cloudflare target, no `wrangler` configuration, no deployed-path test. `docs.yml` publishes GitHub Pages documentation only. |
| ADF-036 | V36 | PARTIAL | `.hermes/AUTONOMOUS_FLEET.md`, `scripts/bundle-verifier-packet.js` | A Hermes reviewer fleet protocol is defined. No release record naming exact build version, reviewer identity, test scope, raw evidence, unresolved defects and go/no-go decision. |
| ADF-037 | V37 | MISSING | inspected: whole repo | No UI, therefore no reload/cancel/accessibility behavior to assess. |
| ADF-038 | V38 | PARTIAL | `runtime/base.py` (`ExecutionLimits`), `runtime/local_process.py`, `specs/schema.py:56-61` | `max_wall_time_seconds` is enforced by the process runtime. `max_steps`, `max_tokens` and `max_parallel_workers` are declared in the spec but no inspected code enforces them. No tracing, alerting or monitoring layer. |
| ADF-039 | V39 | PARTIAL | `specs/governance/*`, `docs/verification/*` | Governance requires evidence before completion. The repository's own prose currently overstates what was inspected — `docs/index.md` and `code_generator.py` describe "production-grade" and "autonomously synthesised" agent code that this audit finds is a single hardcoded template. Corrected by this change. |
| ADF-040 | V40 | PARTIAL | `registry/discovery.py` (`EnvironmentDiscovery`), ADR-005 | Environment discovery and reuse ADRs exist. No retained evidence of actual Hermes / OmniRoute / MCP / registry behavior, as the baseline requires before relying on them. |

## 4. Severity-ranked remediation order

| # | Finding | Severity | Requirement |
|---|---|---|---|
| 1 | Generator, test synthesiser and grader hardcode one agent | **Critical** — the product is not yet a Factory | ADF-001, 013, 014 |
| 2 | Unrun evaluation becomes a perfect score in the release manifest | **Critical** — honesty gate | ADF-022 |
| 3 | Unobserved tokens/cost published as measured zeros | High | ADF-023 |
| 4 | No dependency identity, so no evidence invalidation | High | ADF-027 |
| 5 | Certainty (`CONFIRMED`/`PROPOSED`/`UNRESOLVED`) lost at the Node→Python boundary | High | ADF-008, 005 |
| 6 | No clarification, conflict detection or elicitation | High | ADF-007, 009 |
| 7 | Release bundle is not an agent pack (no instructions, guardrails, review material) | High | ADF-012, 018 |
| 8 | No evaluation plan, prerequisite block or scoped authorization | High | ADF-021, 020 |
| 9 | Capability contracts cannot express schemas, effects or targets | Medium | ADF-016 |
| 10 | `targets` is a label, not a target profile; no ADK | Medium | ADF-015, 024 |
| 11 | No access, guest, BYOK or hosted path | Medium — scope obligation, later increment | ADF-030, 032, 033, 035 |
| 12 | No authoring surface for non-coders | Medium | ADF-003, 006, 037 |
| 13 | Python tier can destroy workspaces and overwrite same-version releases | Medium | ADF-026 |
| 14 | SQLite/JSONL divergence undetected | Medium | ADF-028 |
| 15 | `max_steps` / `max_tokens` / `max_parallel_workers` declared but unenforced | Low | ADF-038 |

## 5. Delta allocated to feature specifications

The remediation above is allocated to proposed Spec Kit feature folders. These are **proposed, not authored**; create each with `.specify/scripts/powershell/create-new-feature.ps1` when the increment is approved.

| Proposed feature | Covers |
|---|---|
| `005-spec-driven-agent-synthesis` | ADF-001, 010, 013, 014 — replace the hardcoded generator with spec-driven instruction, code, guardrail and case synthesis |
| `006-evidence-applicability-ledger` | ADF-022, 023, 027, 028 — dependency identity, applicability states, `NOT RUN` propagation, unknown-vs-zero metrics |
| `007-clarification-and-certainty` | ADF-005, 007, 008, 009, 011 — elicitation rounds, conflict surfacing, certainty carried end-to-end, machine traceability graph |
| `008-agent-pack-contract` | ADF-012, 017, 018 — pack-contract Markdown artifacts, reviewer export, retention declaration |
| `009-supervised-evaluation-control-plane` | ADF-019, 020, 021, 024, 025 — evaluation plan/run entities, prerequisite gates, scoped authorization, stop semantics, boundary case packs |
| `010-target-profiles-and-adapters` | ADF-015, 016, 024, 031, 040 — target profiles with declared gaps, full capability contracts, verified integration evidence |
| `011-hosted-access-and-byok` | ADF-003, 006, 030, 032, 033, 034, 035, 037 — web surface, server-side password, guest expiry, BYOK isolation, Cloudflare target |

## 6. Audit authority statement

- **Inspected:** source and documentation listed in §1.
- **Executed:** nothing. No test suite, grader, adapter probe or CLI command was run for this audit.
- **Reported by others, not re-verified here:** every prior pass claim in `reports/eval_results.json`, `test-runs/**` and `specs/archive/2026-11-03-baseline/FACTORY_TEST_RESULTS.md`.
- **Not authorized / not attempted:** network calls, provider probes, deployment, filesystem-escape testing.

Supersedes nothing. Extends `specs/audit/04-specification-gaps.md` with the baseline v1.0.0 requirement set.
