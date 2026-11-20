# Factory Monitoring and Observability Guide

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** BASELINED & APPROVED  

---

## 1. Observability Principles: Focus on Outcomes

In accordance with Section 17 of the *Full-Lifecycle Engineering Handbook*, the factory observes **accepted outcomes, not vanity activity**. More tool calls, larger token counts, or continuous looping do not indicate better performance.

The fundamental unit of observability is an **authorized request resulting in a cryptographically verified, accepted deliverable**.

---

## 2. Telemetry and Trace Hierarchy

Every operation within the factory emits structured, correlated events across a 4-level trace hierarchy:

```
[Level 1: Project Request]  (request_id: req_01H...)
     │
     ▼
[Level 2: Factory Stage]    (stage: BUILD, TEST, EVALUATE)
     │
     ▼
[Level 3: Agent Run]        (run_id: run_01H..., runtime: local_process)
     │
     ▼
[Level 4: Tool / Model]     (tool: read_csv, duration_ms: 12, exit_code: 0)
```

### Structured Event Format:
```json
{
  "timestamp": "2026-11-03T11:25:00.123Z",
  "request_id": "req_01H89XYZ",
  "run_id": "run_01H89ABC",
  "stage": "TEST",
  "agent_id": "csv_data_anomaly_analyzer",
  "version": "1.0.0",
  "event_type": "TOOL_INVOCATION",
  "component": "agent_factory.runtime.local_process",
  "details": {
    "tool_name": "read_local_csv",
    "parameters_redacted": {"path": "fixtures/sample_data.csv"},
    "duration_ms": 14.2,
    "exit_code": 0,
    "bytes_read": 1420
  },
  "secret_redaction_applied": true
}
```

---

## 3. Service Level Objectives (SLOs) & Indicators

### 3.1 Factory Operations SLOs
* **Build Success Rate:** $\ge 95\%$ of valid specifications progress through testing and packaging without human intervention.
* **Remediation Resolution Rate:** $\ge 80\%$ of recoverable test failures resolved within 3 remediation attempts.
* **Evidence Ledger Integrity:** $100\%$ of completed tasks have matching cryptographic SHA-256 artifact hashes.

### 3.2 Agent Performance SLOs
* **Efficacy Score:** $\ge 0.95$ across all standard evaluation suites.
* **Safety Violation Rate:** **0.00%** (zero unauthorized side effects, zero secret leaks).
* **Execution Latency:** $\le 2000\text{ ms}$ for standard CSV anomaly scans up to 50,000 rows.

---

## 4. Failure Classification & Alerting

When an error occurs, the telemetry subsystem classifies it into one of eight distinct fault buckets:

1. `INPUT_INVALID`: Missing or malformed user parameters.
2. `SPEC_VIOLATION`: Universal specification violates schema or semantic policy.
3. `DEPENDENCY_UNAVAILABLE`: Required tool or model offline or unverified.
4. `RUNTIME_EXCEPTION`: Unhandled Python exception in agent code.
5. `ASSERTION_FAILED`: Test suite failure (candidate for remediation).
6. `TIMEOUT_EXCEEDED`: Subprocess exceeded wall-time quota.
7. `SECURITY_DENIAL`: Attempt to execute unauthorized effect (triggers critical alert).
8. `BUDGET_EXHAUSTED`: Paid spend ceiling or remediation retry ceiling reached.
