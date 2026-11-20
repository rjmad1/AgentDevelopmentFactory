# Audit Report 02: Master Specification Register

**Audit ID:** AUD-02-SPEC-REGISTER  
**Date:** November 20, 2026  
**Auditors:** Specification-Driven Development (SDD) Specialist, Senior Product Manager  
**Status:** BASELINED  

---

## 1. Specification Taxonomy & Classification Key

Every specification in the repository is evaluated and assigned one of the 9 official classifications:

* `Valid`: Accurate, sufficiently complete, and consistent.
* `Incomplete`: Missing important requirements or supporting details.
* `Outdated`: No longer represents approved intent.
* `Contradictory`: Conflicts with other specifications or decisions.
* `Duplicate`: Substantially overlaps another authoritative document.
* `Orphaned`: Has no identifiable relationship to current functionality.
* `Unverified`: Insufficient evidence to establish accuracy.
* `Missing`: Required specification does not exist.
* `Historical`: Retained for historical or decision-traceability purposes.

---

## 2. Master Specification Register

| ID | Specification | Current Status | Quality Assessment | Implementation Evidence | Recommended Action | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SPEC-01** | `FACTORY_AGENT_SPECIFICATION_STANDARD.md` | Valid | Comprehensive schema definitions; covers identity, permissions, quotas, tools, policies. | `agent_factory/specs/schema.py`, `agent_factory/specs/validator.py`, `tests/test_schema.py` | Promote to `specs/contracts/agent.schema.json` and `specs/architecture/master-architecture.md`. | P1 |
| **SPEC-02** | `FACTORY_API_SPECIFICATION.md` | Incomplete | Draft API endpoints; lacks OpenAPI 3.1 schema and error codes. | `agent_factory/cli.py`, `src/cli.js` | Enrich with OpenAPI specs in `specs/contracts/`. | P2 |
| **SPEC-03** | `FACTORY_APPROVAL_POLICY.md` | Valid | Clear risk-based approval matrix (Low/Med/High effect operations). | `agent_factory/security/approval_gate.py`, `tests/test_security.py` | Promote to `specs/governance/approval-policy.md`. | P1 |
| **SPEC-04** | `FACTORY_AUTONOMY_POLICY.md` | Valid | Rigorous 5-level autonomy classification and containment bounds. | `agent_factory/control_plane/orchestrator.py`, `agent_factory/security/policy.py` | Promote to `specs/governance/autonomy-policy.md`. | P1 |
| **SPEC-05** | `FACTORY_BACKUP_AND_RESTORE.md` | Duplicate | Overlaps significantly with recovery runbook and data architecture. | SQLite `.backup` procedures in `agent_factory/control_plane/task_ledger.py` | Merge into `specs/architecture/data-architecture.md` and archive baseline. | P3 |
| **SPEC-06** | `FACTORY_CHANGELOG.md` | Historical | Initial bootstrap log dated 2026-11-03. | None (Documentation artifact). | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-07** | `FACTORY_COMPONENT_ARCHITECTURE.md` | Valid | Modular blueprint of 8 core subsystems (Intake, Control, Workbench, etc.). | `agent_factory/` module layout; 100% component correspondence. | Promote to `specs/architecture/component-architecture.md`. | P1 |
| **SPEC-08** | `FACTORY_DATA_ARCHITECTURE.md` | Valid | Detailed data store models (Task Ledger, Registry, Workspace, Store). | `agent_factory/control_plane/task_ledger.py`, `data/capability_registry.json` | Promote to `specs/architecture/data-architecture.md`. | P1 |
| **SPEC-09** | `FACTORY_DEPLOYMENT_ARCHITECTURE.md` | Valid | Target topologies for Local Process, Hermes Agent, and Docker. | `agent_factory/runtime/local_process.py`, `deployments/` | Promote to `specs/architecture/deployment-architecture.md`. | P2 |
| **SPEC-10** | `FACTORY_ENVIRONMENT_DISCOVERY_REPORT.md` | Historical | Discovery snapshot of system hardware/software from 2026-11-03. | System config and ports (20128, 31415). | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-11** | `FACTORY_EVALUATION_FRAMEWORK.md` | Valid | Detailed multi-metric scoring model (ExitCode, JSON, Markdown, AST). | `agent_factory/evals/graders.py`, `agent_factory/evals/runner.py`, `tests/test_evals.py` | Promote to `specs/architecture/evaluation-framework.md`. | P1 |
| **SPEC-12** | `FACTORY_EXECUTIVE_SUMMARY.md` | Historical | High-level synthesis from 2026-11-03 bootstrap. | Summarizes early acceptance criteria. | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-13** | `FACTORY_HANDBOOK_GAP_ANALYSIS.md` | Historical | Gap analysis reconciling the 52-page advisory handbook. | References `extracted_handbook.txt`. | Retain in archive as primary design rationale. | P3 |
| **SPEC-14** | `FACTORY_IMPLEMENTATION_PLAN.md` | Historical | 5-phase initial implementation plan (now completed). | Reflected across `agent_factory/` codebase. | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-15** | `FACTORY_IMPLEMENTATION_STATUS.md` | Historical | M1-M4 milestone scorecard from 2026-11-03. | Milestone test results. | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-16** | `FACTORY_INTEGRATION_ARCHITECTURE.md` | Valid | Integration specs for OmniRoute, FreeLLMAPI, and Hermes Harness. | `agent_factory/adapters/hermes_adapter.py`, `agent_factory/adapters/omniroute_adapter.py` | Promote to `specs/architecture/integration-architecture.md`. | P2 |
| **SPEC-17** | `FACTORY_MASTER_ARCHITECTURE.md` | Valid | Definitive Three-Plane Separation Model and system state machine. | `agent_factory/control_plane/orchestrator.py` lifecycle stages. | Promote to `specs/architecture/master-architecture.md`. | P1 |
| **SPEC-18** | `FACTORY_MONITORING_AND_OBSERVABILITY.md`| Incomplete | Runbook structure present; lacks Prometheus metrics and tracing spans. | Basic log output; LangSmith traces in `agent_factory/evals/langsmith_adapter.py`. | Enrich in `specs/architecture/master-architecture.md`. | P2 |
| **SPEC-19** | `FACTORY_OPERATIONS_RUNBOOK.md` | Valid | Operator runbooks for starting, monitoring, and debugging the factory. | CLI commands in `agent_factory/cli.py`. | Retain in `docs/guides/operations.md`. | P2 |
| **SPEC-20** | `FACTORY_PRODUCTION_READINESS_ASSESSMENT.md`| Historical | Point-in-time readiness audit against M4 milestone. | Verification logs. | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-21** | `FACTORY_PROVIDER_ADAPTER_SPECIFICATION.md` | Incomplete | Defines abstract adapter interface; missing concrete streaming protocol. | `agent_factory/adapters/base.py`. | Promote to `specs/architecture/integration-architecture.md`. | P2 |
| **SPEC-22** | `FACTORY_RECOVERY_RUNBOOK.md` | Valid | Step-by-step procedures for database recovery and workspace cleanup. | Automated cleanup in `agent_factory/workbench/workspace.py`. | Retain in `docs/guides/recovery.md`. | P2 |
| **SPEC-23** | `FACTORY_REGISTRY_SPECIFICATION.md` | Incomplete | High-level registry schema; missing dynamic capability indexing spec. | `agent_factory/registry/capability_registry.py`, `data/capability_registry.json`. | Promote to `specs/architecture/component-architecture.md`. | P2 |
| **SPEC-24** | `FACTORY_REGRESSION_REPORT.md` | Historical | Initial 28-test regression run output. | Test outputs in `FACTORY_TEST_RESULTS.md`. | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-25** | `FACTORY_REQUIREMENTS_CATALOG.md` | Valid | Definitive catalog of 28 structured requirements (`REQ-GOV-*` to `REQ-OPS-*`). | Unit and integration tests in `tests/`. | Promote to `specs/audit/02-specification-register.md` & `specs/governance/`. | P1 |
| **SPEC-26** | `FACTORY_REQUIREMENTS_TRACEABILITY_MATRIX.md` | Valid | Bi-directional traceability from requirements to code and tests. | 42 Python tests, 13 Node.js tests. | Promote to `specs/audit/03-implementation-traceability.md`. | P1 |
| **SPEC-27** | `FACTORY_RESIDUAL_RISK_REGISTER.md` | Duplicate | Overlaps with `FACTORY_RISK_REGISTER.md`. | Security tests in `tests/test_security.py`. | Consolidate into `specs/governance/risk-management.md`. | P2 |
| **SPEC-28** | `FACTORY_RISK_REGISTER.md` | Valid | Identifies 10 core risks, mitigations, and ownership. | Policy enforcement in `agent_factory/security/policy.py`. | Promote to `specs/governance/risk-management.md`. | P2 |
| **SPEC-29** | `FACTORY_SECURITY_ARCHITECTURE.md` | Valid | Three-layer security model: AST quarantine, redactor, approval gates. | `agent_factory/security/quarantine.py`, `agent_factory/security/redactor.py`. | Promote to `specs/architecture/security-architecture.md`. | P1 |
| **SPEC-30** | `FACTORY_SECURITY_ASSESSMENT.md` | Historical | Vulnerability scan and policy assessment dated 2026-11-03. | AST checks and secret scanning tests. | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-31** | `FACTORY_TEST_RESULTS.md` | Historical | Verifiable evidence output of 2026-11-03 test runs. | Stored test execution logs. | Preserve in `specs/archive/2026-11-03-baseline/`. | P4 |
| **SPEC-32** | `FACTORY_TEST_STRATEGY.md` | Valid | Test levels: unit, contract, integration, sandbox, evaluation. | `pytest.ini`, `tests/`, `test/runner.js`. | Promote to `specs/governance/traceability-policy.md`. | P1 |
| **SPEC-33** | `FACTORY_THREAT_MODEL.md` | Incomplete | STRIDE threat taxonomy; missing LLM prompt-injection threat vector. | Secret redactor and path traversal guards in `src/core.js`. | Enrich in `specs/architecture/security-architecture.md`. | P2 |
| **SPEC-34** | `docs/factory_product_contract.md` | Valid | Foundational product planning contract; v1 evaluation scope; hard gates. | `src/core.js`, `src/cli.js`, `test/evals/`. | Maintain as authoritative in `docs/` and link from `specs/`. | P1 |
| **SPEC-35** | `docs/factory_capability_and_acceptance_map.md` | Valid | 6 core capabilities, inputs/outputs, user decision points. | Node CLI check triage; Python lifecycle. | Maintain as authoritative in `docs/` and link from `specs/`. | P1 |
| **SPEC-36** | `docs/DEVELOPMENT_PIPELINE.md` | Valid | Tri-Tier pipeline, Hermes fleet protocol, token economics. | `scripts/autonomous-loop.js`, `.hermes/AUTONOMOUS_FLEET.md`. | Maintain as authoritative in `docs/` and link from `specs/`. | P1 |
| **SPEC-37** | `.specify/memory/constitution.md` | Missing | Project constitution required by GitHub Spec Kit. | Currently placeholder template. | Author definitive constitution in Stage 3. | P1 |
| **SPEC-38** | `specs/features/001-bounded-authoring-slice/` | Missing | Formal Spec Kit specification for the zero-dependency authoring engine. | Implemented in `src/core.js`, `src/cli.js`, `test/runner.js`. | Author Spec Kit feature pack in Stage 3. | P1 |
| **SPEC-39** | `specs/features/002-autonomous-watcher-loop/` | Missing | Formal Spec Kit specification for the autonomous engineering watcher loop. | Implemented in `scripts/autonomous-loop.js`. | Author Spec Kit feature pack in Stage 3. | P2 |
| **SPEC-40** | `specs/features/003-control-plane-orchestrator/` | Missing | Formal Spec Kit specification for the 20-stage Python lifecycle engine. | Implemented in `agent_factory/control_plane/`. | Author Spec Kit feature pack in Stage 3. | P1 |
| **SPEC-41** | `specs/features/004-evaluation-verification-harness/` | Missing | Formal Spec Kit specification for Deep Evaluator and LangSmith evals. | Implemented in `agent_factory/evals/` and `test/evals/`. | Author Spec Kit feature pack in Stage 3. | P1 |
