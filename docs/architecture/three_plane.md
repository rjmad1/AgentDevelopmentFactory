# The Three-Plane Separation Model

The Agent Development Factory prevents operational hazards by enforcing strict decoupling across three operational planes:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. CONTROL PLANE                                │
│  - Request Intake & Semantic Classification                            │
│  - Universal Agent Specification Enforcement (JSON Schema / Pydantic)  │
│  - Finite State Machine Orchestration (11 Discrete Stages)             │
│  - Risk-Based Human Approval Enforcement (Low / Medium / High)         │
│  - Resource Quota & Budgetary Guardrails                               │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Dispatches Tasks / Injects Config
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        2. EXECUTION PLANE                              │
│  - Isolated Workspace Sandbox (Per-Project Directory Isolation)        │
│  - Code Synthesis & Scaffold Generation (Deterministic Templates)      │
│  - Deterministic Test Suite Synthesis (pytest fixtures & contracts)    │
│  - Subprocess Execution Management (Non-blocking, Timeouts, Streaming) │
│  - Automated Diagnostic & Remediation Loop (Bounded Retry Budget)      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Emits Artifacts & Execution Ledgers
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        3. EVIDENCE PLANE                               │
│  - Multi-Metric Evaluation Graders (Efficacy, Safety, Cost)            │
│  - Cryptographic Verification & Checksum Manifests (SHA-256)           │
│  - Append-Only Audit Ledger (SQLite WAL + JSONL Event Stream)          │
│  - Versioned Release Packaging & Rollback Strategy                     │
│  - Provider-Agnostic Capability & Tool Registries                      │
└────────────────────────────────────────────────────────────────────────┘
```

## Plane 1: Control Plane (Governance & Orchestration)
The Control Plane is the authoritative system of record and governance. It:
- Ingests unstructured or structured business requirements.
- Validates inputs against `agent.yaml` specifications.
- Drives the 11-stage finite state machine (`REQUEST_INGESTED` to `DEPLOYMENT_COMPLETED`).
- Prevents unauthorized actions through risk policies.

## Plane 2: Workbench / Execution Plane
The Workbench Plane isolates code synthesis and execution:
- Creates sandboxed workspaces with `artifacts/`, `fixtures/`, `src/`, `tests/`.
- Synthesizes robust agent code and automated pytest suites.
- Runs local processes with CPU/memory quotas and timeouts.
- Manages the remediation loop with a bounded 3-attempt diagnostic repair cycle.

## Plane 3: Evidence & Verification Plane
The Evidence Plane ensures no agent moves to release without observable proof:
- Executes deterministic graders (`FileExistenceGrader`, `ByteSizeGrader`, `JsonStructureGrader`, `MarkdownStructureGrader`, `SecretLeakGrader`, `ExitCodeGrader`).
- Calculates normalized score vectors (Efficacy, Safety, Efficiency).
- Dispatches telemetry to LangSmith Free Tier and local Deep Evaluator ledgers.
- Signs release bundles with SHA-256 digests.
