# Factory Requirements Traceability Matrix (RTM)

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** BASELINED  
**Scope:** Bidirectional Traceability from Directive/Handbook to Software Modules & Tests  

---

## 1. Traceability Architecture

The Requirements Traceability Matrix guarantees that every requirement established in `FACTORY_REQUIREMENTS_CATALOG.md`:
1. Maps to a specific logical architectural subsystem.
2. Traces directly to concrete source code implementation files in `agent_factory/`.
3. Binds to explicit, automated verification test cases in `tests/`.
4. Has an unambiguous verification verdict backed by empirical evidence.

---

## 2. Bidirectional Traceability Table

| Requirement ID | Requirement Summary | Architectural Subsystem | Implementation Artifact(s) | Verification Test(s) | Target Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-GOV-01** | Vendor Agnosticism | Multi-Adapter Runtime | `agent_factory/adapters/base.py`<br>`agent_factory/adapters/local_runtime.py`<br>`agent_factory/adapters/hermes_adapter.py` | `tests/test_adapters.py::test_multi_runtime_conformance` | VERIFIED |
| **REQ-GOV-02** | Full-Lifecycle Autonomy | Control Plane Orchestrator | `agent_factory/control_plane/orchestrator.py`<br>`agent_factory/control_plane/lifecycle.py` | `tests/test_lifecycle.py::test_full_lifecycle_execution` | VERIFIED |
| **REQ-GOV-03** | Reproducible Artifacts | Release Packaging | `agent_factory/workbench/packager.py`<br>`agent_factory/workbench/manifest.py` | `tests/test_packager.py::test_reproducible_checksums` | VERIFIED |
| **REQ-GOV-04** | Evidence-Based Completion | Evidence Ledger & Graders | `agent_factory/control_plane/evidence.py`<br>`agent_factory/evals/graders.py` | `tests/test_evidence.py::test_reject_missing_artifacts` | VERIFIED |
| **REQ-GOV-05** | Zero Unapproved Paid Fallback | Policy & Adapter Gateways | `agent_factory/security/policy.py`<br>`agent_factory/adapters/omniroute_adapter.py` | `tests/test_policy.py::test_paid_spend_ceiling_enforcement` | VERIFIED |
| **REQ-SPEC-01** | Universal Agent Schema | Agent Specification Core | `agent_factory/specs/schema.py`<br>`agent_factory/specs/validator.py` | `tests/test_schema.py::test_valid_agent_spec`<br>`tests/test_schema.py::test_reject_invalid_spec` | VERIFIED |
| **REQ-SPEC-02** | Explicit Permission Boundaries | Security & Spec Engine | `agent_factory/specs/schema.py`<br>`agent_factory/security/policy.py` | `tests/test_policy.py::test_unauthorized_effect_rejection` | VERIFIED |
| **REQ-SPEC-03** | Execution Limits & Quotas | Runtime Supervision | `agent_factory/runtime/local_process.py`<br>`agent_factory/specs/schema.py` | `tests/test_runtime.py::test_execution_timeout_and_step_cap` | VERIFIED |
| **REQ-SPEC-04** | Predictable Denial Handling | Runtime & Policy Engine | `agent_factory/security/policy.py`<br>`agent_factory/runtime/base.py` | `tests/test_policy.py::test_denial_stop_and_report` | VERIFIED |
| **REQ-REG-01** | Unified Typed Registry | Capability Registry | `agent_factory/registry/capability_registry.py` | `tests/test_registry.py::test_registry_crud_and_query` | VERIFIED |
| **REQ-REG-02** | Live Environment Discovery | Registry Discovery Engine | `agent_factory/registry/discovery.py` | `tests/test_discovery.py::test_live_system_probing` | VERIFIED |
| **REQ-REG-03** | Verification Before Availability | Capability Validator | `agent_factory/registry/capability_registry.py` | `tests/test_registry.py::test_unverified_capability_blocked` | VERIFIED |
| **REQ-REG-04** | Skill & MCP Quarantine | Security Quarantine Module | `agent_factory/security/quarantine.py` | `tests/test_quarantine.py::test_unvetted_skill_quarantine` | VERIFIED |
| **REQ-CTL-01** | Stateful 3-Plane Architecture | Control Plane Ledger | `agent_factory/control_plane/task_ledger.py`<br>`agent_factory/control_plane/orchestrator.py` | `tests/test_control_plane.py::test_state_persistence_and_resume` | VERIFIED |
| **REQ-WB-01** | Isolated Workspace Management | Workbench Workspace Engine | `agent_factory/workbench/workspace.py` | `tests/test_workspace.py::test_workspace_isolation` | VERIFIED |
| **REQ-WB-02** | Automated Code & Test Generation | Code Synthesis Workbench | `agent_factory/workbench/code_generator.py`<br>`agent_factory/workbench/test_generator.py` | `tests/test_generators.py::test_generate_agent_and_tests` | VERIFIED |
| **REQ-WB-03** | Bounded Autonomous Remediation | Self-Improvement & Repair | `agent_factory/remediation/engine.py` | `tests/test_remediation.py::test_bounded_remediation_loop` | VERIFIED |
| **REQ-ADP-01** | Universal Adapter Contract | Adapter Core Framework | `agent_factory/adapters/base.py` | `tests/test_adapters.py::test_base_adapter_contract` | VERIFIED |
| **REQ-ADP-02** | OmniRoute Gateway Adapter | Model Provider Adapter | `agent_factory/adapters/omniroute_adapter.py` | `tests/test_adapters.py::test_omniroute_adapter_live_or_mock` | VERIFIED |
| **REQ-ADP-03** | Hermes Harness Adapter | Orchestration Harness Adapter | `agent_factory/adapters/hermes_adapter.py` | `tests/test_adapters.py::test_hermes_harness_adapter` | VERIFIED |
| **REQ-RT-01** | Standalone Local Process Runtime | Core Execution Runtime | `agent_factory/runtime/local_process.py` | `tests/test_runtime.py::test_local_process_standalone_run` | VERIFIED |
| **REQ-EVAL-01** | Multi-Metric Evaluation Engine | QA & Evaluation Core | `agent_factory/evals/runner.py`<br>`agent_factory/evals/metrics.py` | `tests/test_evals.py::test_evaluation_metrics_calculation` | VERIFIED |
| **REQ-EVAL-02** | Standard Evaluation Pack (A01-A15) | Evaluation Test Fixtures | `agent_factory/evals/benchmarks.py`<br>`agent_factory/evals/graders.py` | `tests/test_evals.py::test_standard_benchmark_suite` | VERIFIED |
| **REQ-SEC-01** | Secret Isolation & Redaction | Security & Logging Engine | `agent_factory/security/secrets.py`<br>`agent_factory/security/redactor.py` | `tests/test_security.py::test_secret_redaction_in_logs` | VERIFIED |
| **REQ-SEC-02** | Three-Tier Approval Gates | Governance & Auth Engine | `agent_factory/security/approval_gate.py` | `tests/test_security.py::test_approval_gate_enforcement` | VERIFIED |
| **REQ-OPS-01** | Reproducible Release Packaging | Release Controller | `agent_factory/workbench/packager.py` | `tests/test_packager.py::test_package_extraction_and_verify` | VERIFIED |
| **REQ-OPS-02** | Deterministic Rollback & Suspend | Lifecycle & Ops Engine | `agent_factory/control_plane/lifecycle.py` | `tests/test_lifecycle.py::test_agent_rollback_and_suspension` | VERIFIED |
| **REQ-OPS-03** | Operational CLI & Observability | Operator Experience & Telemetry | `agent_factory/cli.py`<br>`agent_factory/control_plane/observability.py` | `tests/test_cli.py::test_cli_commands` | VERIFIED |

---

## 3. Acceptance Verification Mapping

Every test listed above is executed by the test suite and directly mapped into `FACTORY_TEST_RESULTS.md` and the final acceptance evaluation.
