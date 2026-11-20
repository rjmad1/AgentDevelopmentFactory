# Factory Implementation Plan

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** APPROVED & ACTIVE  

---

## 1. Implementation Strategy and Phasing

To achieve the goals of the Master Directive and satisfy all 20 Acceptance Criteria (AC-01 through AC-20) without speculative scope creep, implementation follows a strict 8-stage sequence. Every stage has verifiable preconditions, concrete deliverables, and automated regression checks.

```
Stage A: Environment Discovery (COMPLETED)
   │
   ▼
Stage B: PDF Requirements & Gap Analysis (COMPLETED)
   │
   ▼
Stage C: Architecture Baselining (COMPLETED)
   │
   ▼
Stage D: Factory Foundation & Core Engine (CURRENT)
   ├── Universal Agent Spec & Semantic Validator
   ├── Unified Typed Capability Registry & Live Discovery
   ├── Control Plane State Machine & SQLite Ledger
   └── Security Redaction, Approval Gates & Policy Enforcer
   │
   ▼
Stage E: Autonomous Engineering Workbench & Adapters
   ├── Workspace Sandbox Manager
   ├── Modular Code & Test Synthesizers
   ├── Standalone Local Process Runtime
   ├── OmniRoute & Hermes Harness Adapters
   └── Multi-Metric Evaluation Engine (Efficacy, Safety, Efficiency)
   │
   ▼
Stage F: Bounded Autonomous Remediation Loop
   ├── Traceback Diagnosis & Error Classifier
   ├── Surgical Patch Synthesizer
   └── 3-Attempt Budget & Holdout Verifier
   │
   ▼
Stage G: Unit & Integration Test Suite Verification
   └── 100% Passing Pytest Execution Across Factory Modules
   │
   ▼
Stage H: Mandatory End-to-End Acceptance Test & Final Release
   ├── Ingest CSV Data Quality Anomaly Analyzer Requirement
   ├── Autonomously Build, Test, Remediate, Evaluate & Package
   ├── Execute Standalone Release on Real Data & Verify Evidence
   └── Final Assessment & Production Readiness Delivery
```

---

## 2. Workstream Breakdown & Deliverables

### Workstream 1: Foundation & Specifications
* Target Files:
  * `agent_factory/specs/schema.py`
  * `agent_factory/specs/validator.py`
  * `agent_factory/registry/capability_registry.py`
  * `agent_factory/registry/discovery.py`
* Acceptance Check: Rejects invalid schemas; parses and validates universal spec; discovers live host capabilities.

### Workstream 2: Control Plane & Persistence
* Target Files:
  * `agent_factory/control_plane/task_ledger.py`
  * `agent_factory/control_plane/intake.py`
  * `agent_factory/control_plane/orchestrator.py`
  * `agent_factory/control_plane/lifecycle.py`
* Acceptance Check: Atomic SQLite state transitions; crash-recovery resumption; stage advance validation.

### Workstream 3: Security & Governance
* Target Files:
  * `agent_factory/security/policy.py`
  * `agent_factory/security/redactor.py`
  * `agent_factory/security/approval_gate.py`
  * `agent_factory/security/quarantine.py`
* Acceptance Check: Redacts secret references from streams; blocks unauthorized tool effects; halts for human approval tokens.

### Workstream 4: Workbench & Runtime Adapters
* Target Files:
  * `agent_factory/workbench/workspace.py`
  * `agent_factory/workbench/code_generator.py`
  * `agent_factory/workbench/test_generator.py`
  * `agent_factory/workbench/packager.py`
  * `agent_factory/runtime/base.py`
  * `agent_factory/runtime/local_process.py`
  * `agent_factory/adapters/base.py`
  * `agent_factory/adapters/omniroute_adapter.py`
  * `agent_factory/adapters/hermes_adapter.py`
* Acceptance Check: Synthesizes valid Python code and test suites; executes subprocesses cleanly with timeouts.

### Workstream 5: Evaluation & Bounded Remediation
* Target Files:
  * `agent_factory/evals/runner.py`
  * `agent_factory/evals/graders.py`
  * `agent_factory/evals/metrics.py`
  * `agent_factory/remediation/engine.py`
* Acceptance Check: Computes multi-metric scores; diagnoses failed runs and applies surgical fixes within attempt ceiling.

### Workstream 6: Operations, CLI & End-to-End Acceptance
* Target Files:
  * `agent_factory/cli.py`
  * End-to-end representative project: `workspaces/project_csv_anomaly_analyzer/`
* Acceptance Check: Complete autonomous execution of CSV Anomaly Analyzer producing verifiable artifact and report.
