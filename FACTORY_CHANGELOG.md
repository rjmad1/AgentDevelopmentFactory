# Factory Changelog

All notable changes, architectural baselines, and implementation milestones for the Agent Development Factory are documented in this file.

---

## [1.0.0] - 2026-11-03

### Initial Release: Operational Autonomous Agent Development Factory

#### Added - Architecture & Governance
* Established `FACTORY_MASTER_ARCHITECTURE.md` defining the Three-Plane Separation Model (Control, Execution, Evidence).
* Established `FACTORY_COMPONENT_ARCHITECTURE.md` detailing the 8 core logical subsystems.
* Established `FACTORY_DATA_ARCHITECTURE.md` formalizing the four separate conceptual data stores and 5-tier classification.
* Established `FACTORY_SECURITY_ARCHITECTURE.md` with active secret redaction, AST quarantine, and risk-based gates.
* Established `FACTORY_INTEGRATION_ARCHITECTURE.md` for OmniRoute (Port 20128), FreeLLMAPI (Port 31415), and Hermes v0.22.6.
* Established `FACTORY_DEPLOYMENT_ARCHITECTURE.md` for Standalone Local Process, Hermes Harness, and Docker targets.
* Formulated `FACTORY_REQUIREMENTS_CATALOG.md` (28 structured requirements) and `FACTORY_REQUIREMENTS_TRACEABILITY_MATRIX.md`.
* Authored `FACTORY_HANDBOOK_GAP_ANALYSIS.md` resolving inconsistencies and unrealistic assumptions from the advisory handbook.

#### Added - Software Core Implementation (`agent_factory/`)
* **Specification Engine:** Pydantic models and JSON Schema for Universal Agent Specification (`agent_factory.specs`).
* **Capability Registry:** Strongly typed, persistent catalog with live hardware, socket, and CLI discovery (`agent_factory.registry`).
* **Security & Governance:** Least-privilege `PolicyEnforcer`, active `SecretRedactor`, HMAC `ApprovalGate`, and AST `SkillQuarantine`.
* **Control Plane:** Atomic SQLite `TaskLedger`, JSON Lines event logging, `RequestIntake`, and 11-stage `FactoryOrchestrator`.
* **Engineering Workbench:** Isolated `WorkspaceManager`, automated `CodeGenerator`, `TestGenerator`, and reproducible `ReleasePackager`.
* **Runtimes & Adapters:** Standalone `LocalProcessRuntime` with environment sanitization, `OmniRouteModelAdapter`, and `HermesHarnessAdapter`.
* **Evaluation & QA:** Multi-metric scoring engine (`Efficacy`, `Safety`, `Efficiency`) with deterministic file, schema, size, and exit code graders.
* **Bounded Remediation:** Diagnostic error classifier with surgical code patching and a strict 3-attempt ceiling.
* **Operational CLI:** Unified command-line interface (`agent_factory.cli`) supporting status, intake, build, test, eval, package, deploy, and run.

#### Added - Testing & Empirical Verification
* Implemented 24 comprehensive unit and integration tests across all factory modules (`tests/`). Achieved 100% pass rate in 1.95s.
* Executed Mandatory End-to-End Acceptance Test (`proj_aa59a7bd89`): Autonomously developed, tested, evaluated, packaged, and deployed the CSV Data Quality Anomaly Analyzer agent on real data in 60.66 ms.
