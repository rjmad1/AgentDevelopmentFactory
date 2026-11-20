# Universal Agent Specification Standard

**Standard Version:** 1.0.0  
**Date:** 2026-11-03  
**Status:** APPROVED & BASELINED  
**File Formats:** YAML (`agent.yaml`) and JSON (`agent.json`)  

---

## 1. Specification Purpose and Philosophy

The **Universal Agent Specification Standard** defines a portable, framework-agnostic contract for AI agents. It completely decouples the agent's behavioral definition, permission boundaries, and operational constraints from any vendor-specific prompt format, orchestration library, or execution harness.

An agent defined under this standard can be validated, compiled, tested, and deployed across different runtimes (such as Standalone Python, Hermes Agent, or Docker) with zero ambiguity regarding permissions, resource quotas, or evaluation criteria.

---

## 2. Specification Structure & Fields

```yaml
schema_version: 1
agent_id: "csv_data_anomaly_analyzer"
version: "1.0.0"
owner: "Raja"
purpose: "Analyze local CSV datasets for data-quality anomalies, null spikes, and format drifts, emitting a structured markdown report and JSON summary."

inputs:
  dataset_path:
    type: "string"
    description: "Absolute or workspace-relative path to input CSV file"
    required: true
  anomaly_threshold:
    type: "float"
    description: "Standard deviation Z-score threshold for outlier detection"
    default: 3.0

outputs:
  anomaly_report:
    type: "file"
    format: "markdown"
    path: "artifacts/anomaly_report.md"
  summary_ledger:
    type: "file"
    format: "json"
    path: "artifacts/summary_ledger.json"

policy:
  mode: "draft_only"
  data_classification: "public_or_synthetic"
  permitted_tools:
    - "read_local_csv"
    - "compute_statistics"
    - "write_workspace_artifact"
  permitted_effects:
    - "READ_PUBLIC"
    - "WRITE_LOCAL_DRAFT"
  secrets: "none"
  on_denial: "stop_and_report"

limits:
  max_steps: 15
  max_wall_time_seconds: 60
  max_tokens: 4000
  paid_spend_ceiling: 0.0
  max_parallel_workers: 1

state:
  durable_fields:
    - "project_id"
    - "stage"
    - "rows_processed"
    - "anomalies_detected"
    - "evidence_refs"

acceptance:
  suite: "evals/data_quality_pack"
  required_checks:
    - "functional_correctness"
    - "schema_compliance"
    - "zero_unauthorized_effects"
    - "reproducible_output"

targets:
  local_process: "candidate"
  hermes: "candidate"
  docker: "supported"
```

---

## 3. Strict Semantic Validation Rules

Beyond validating the JSON/YAML structure, the factory enforces the following semantic validation rules (`agent_factory.specs.validator`):

1. **Unknown Major Version Rejection:** If `schema_version > 1`, validation fails immediately; schema upgrades require an explicit migration tool.
2. **Permission Boundary Coherence:** If `policy.permitted_effects` contains `SPEND_DELETE` or `CHANGE_ACCOUNT`, the specification must have a valid `human_approval_token`. Otherwise, it fails with `PolicyViolationError`.
3. **Budget Consistency:** If `limits.paid_spend_ceiling > 0`, the agent risk classification must be escalated to `HIGH`, requiring explicit owner sign-off.
4. **Tool Existence:** Every tool declared in `policy.permitted_tools` must be registered in the Capability Registry and have a status of `ACTIVE`.
5. **No Secret Inlining:** The `policy.secrets` field can only contain named references (e.g., `["OMNIROUTE_KEY_REF"]`). Any value matching a raw API key regex (`sk-...`, `Bearer ...`) fails validation.
