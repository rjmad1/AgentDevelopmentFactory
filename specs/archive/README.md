# Historical Specification Archive

**Archive Classification:** Informative / Historical Provenance  
**Last Updated:** November 20, 2026  
**Status:** ARCHIVED & READ-ONLY  

---

## 1. Overview

This directory preserves historical baseline specifications, point-in-time assessments, and architectural snapshots generated during earlier phases of the **Agent Development Factory** project.

Per our **Specification Governance & Preservation Policy** (Rule 4: *Do not delete specifications merely because they appear outdated*), no engineering artifact is discarded. Instead, superseded or point-in-time artifacts are retained here with explicit provenance links to their authoritative modern successors.

---

## 2. Archive Inventory: `2026-11-03-baseline/`

On 2026-11-03, 33 root `FACTORY_*.md` files were authored to synthesize the 52-page engineering handbook (`extracted_handbook.txt`) into an initial architecture and requirements baseline. These files have been migrated from the repository root into `specs/archive/2026-11-03-baseline/` to keep the root directory clean while preserving byte-for-byte historical auditability.

| Historical Document | Original Scope | Successor / Authoritative Document |
| :--- | :--- | :--- |
| `FACTORY_AGENT_SPECIFICATION_STANDARD.md` | Universal Agent Spec standard | [`specs/contracts/agent.schema.json`](../contracts/agent.schema.json) & [`specs/architecture/master-architecture.md`](../architecture/master-architecture.md) |
| `FACTORY_API_SPECIFICATION.md` | Initial REST / Python API draft | [`specs/architecture/component-architecture.md`](../architecture/component-architecture.md) & [`docs/api/`](../../docs/api/) |
| `FACTORY_APPROVAL_POLICY.md` | Human approval gate policy | [`specs/governance/approval-policy.md`](../governance/approval-policy.md) |
| `FACTORY_AUTONOMY_POLICY.md` | Autonomy levels and bounds | [`specs/governance/autonomy-policy.md`](../governance/autonomy-policy.md) |
| `FACTORY_BACKUP_AND_RESTORE.md` | SQLite & ledger backup rules | [`specs/architecture/data-architecture.md`](../architecture/data-architecture.md) & [`docs/guides/recovery.md`](../../docs/guides/recovery.md) |
| `FACTORY_CHANGELOG.md` | 2026-11-03 Changelog | Preserved in archive baseline. |
| `FACTORY_COMPONENT_ARCHITECTURE.md` | 8 core subsystems blueprint | [`specs/architecture/component-architecture.md`](../architecture/component-architecture.md) |
| `FACTORY_DATA_ARCHITECTURE.md` | 4 data stores and schemas | [`specs/architecture/data-architecture.md`](../architecture/data-architecture.md) |
| `FACTORY_DEPLOYMENT_ARCHITECTURE.md` | Local / Hermes / Docker targets | [`specs/architecture/deployment-architecture.md`](../architecture/deployment-architecture.md) |
| `FACTORY_ENVIRONMENT_DISCOVERY_REPORT.md` | 2026-11-03 Discovery snapshot | Preserved in archive baseline. |
| `FACTORY_EVALUATION_FRAMEWORK.md` | Multi-metric evaluation gates | [`specs/architecture/evaluation-framework.md`](../architecture/evaluation-framework.md) |
| `FACTORY_EXECUTIVE_SUMMARY.md` | 2026-11-03 Executive briefing | [`specs/audit/01-repository-discovery.md`](../audit/01-repository-discovery.md) |
| `FACTORY_HANDBOOK_GAP_ANALYSIS.md` | Advisory handbook reconciliation | [`specs/audit/04-specification-gaps.md`](../audit/04-specification-gaps.md) |
| `FACTORY_IMPLEMENTATION_PLAN.md` | 2026-11-03 Implementation plan | [`specs/features/`](../features/) |
| `FACTORY_IMPLEMENTATION_STATUS.md` | 2026-11-03 Status report | [`specs/audit/03-implementation-traceability.md`](../audit/03-implementation-traceability.md) |
| `FACTORY_INTEGRATION_ARCHITECTURE.md` | OmniRoute, FreeLLMAPI, Hermes | [`specs/architecture/integration-architecture.md`](../architecture/integration-architecture.md) |
| `FACTORY_MASTER_ARCHITECTURE.md` | Three-Plane separation model | [`specs/architecture/master-architecture.md`](../architecture/master-architecture.md) |
| `FACTORY_MONITORING_AND_OBSERVABILITY.md`| Observability runbook | [`specs/architecture/master-architecture.md`](../architecture/master-architecture.md) |
| `FACTORY_OPERATIONS_RUNBOOK.md` | Operations procedures | [`docs/guides/operations.md`](../../docs/guides/operations.md) |
| `FACTORY_PRODUCTION_READINESS_ASSESSMENT.md`| 2026-11-03 Readiness gates | Preserved in archive baseline. |
| `FACTORY_PROVIDER_ADAPTER_SPECIFICATION.md` | Adapter interfaces | [`specs/architecture/integration-architecture.md`](../architecture/integration-architecture.md) |
| `FACTORY_RECOVERY_RUNBOOK.md` | Disaster recovery runbook | [`docs/guides/recovery.md`](../../docs/guides/recovery.md) |
| `FACTORY_REGISTRY_SPECIFICATION.md` | Tool discovery & registry | [`specs/architecture/component-architecture.md`](../architecture/component-architecture.md) |
| `FACTORY_REGRESSION_REPORT.md` | 2026-11-03 Regression run | Preserved in archive baseline. |
| `FACTORY_REQUIREMENTS_CATALOG.md` | 28 formal baseline requirements | [`specs/audit/02-specification-register.md`](../audit/02-specification-register.md) |
| `FACTORY_REQUIREMENTS_TRACEABILITY_MATRIX.md` | Requirements-to-tests map | [`specs/audit/03-implementation-traceability.md`](../audit/03-implementation-traceability.md) |
| `FACTORY_RESIDUAL_RISK_REGISTER.md` | Residual risks | [`specs/governance/risk-management.md`](../governance/risk-management.md) |
| `FACTORY_RISK_REGISTER.md` | Primary risk register | [`specs/governance/risk-management.md`](../governance/risk-management.md) |
| `FACTORY_SECURITY_ARCHITECTURE.md` | Redactor, quarantine, gates | [`specs/architecture/security-architecture.md`](../architecture/security-architecture.md) |
| `FACTORY_SECURITY_ASSESSMENT.md` | Initial security assessment | [`specs/architecture/security-architecture.md`](../architecture/security-architecture.md) |
| `FACTORY_TEST_RESULTS.md` | 2026-11-03 Test results | Preserved in archive baseline. |
| `FACTORY_TEST_STRATEGY.md` | Quality assurance strategy | [`specs/governance/traceability-policy.md`](../governance/traceability-policy.md) |
| `FACTORY_THREAT_MODEL.md` | STRIDE threat model | [`specs/architecture/security-architecture.md`](../architecture/security-architecture.md) |

---

## 3. Immutability Invariant

Files in `2026-11-03-baseline/` are frozen. They must never be edited, pruned, or overwritten. Any future modifications to specifications must be executed against the active living documents in `specs/architecture/`, `specs/governance/`, or `specs/features/`.
