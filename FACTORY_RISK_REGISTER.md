# Factory Risk Register

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Status:** BASELINED  
**Owner:** Antigravity 2.0 (Supervising Principal Platform Architect)  

---

## 1. Risk Matrix Overview

| Risk ID | Category | Description | Likelihood | Impact | Inherent Risk | Mitigating Control(s) | Residual Risk | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | Cost / Billing | Accidental routing of batch jobs to paid commercial APIs. | Medium | High | **HIGH** | Zero Unapproved Paid Fallback policy ($0 paid ceiling hard cap). | **LOW** | Controlled |
| **RSK-02** | Integrity | False "Verified Done" claims due to model hallucination. | High | High | **CRITICAL** | Three-Plane Separation; Cryptographic Evidence Ledger; Deterministic Byte & Hash Graders. | **LOW** | Controlled |
| **RSK-03** | Reliability | Runaway autonomous remediation loops consuming excessive compute/tokens. | Medium | Medium | **MEDIUM** | Strict 3-attempt ceiling; circuit breaker tripping on repeated failure. | **LOW** | Controlled |
| **RSK-04** | Security | Secret leakage into logs, reports, or test fixtures. | Medium | Critical | **CRITICAL** | Named secret references only; active regex secret redaction filter; environment sanitization. | **LOW** | Controlled |
| **RSK-05** | Security | Prompt injection or jailbreak via untrusted document inputs. | High | High | **HIGH** | Strict effect level boundaries (`READ_PUBLIC`, `DRAFT_ONLY`); human approval for external actions. | **LOW** | Controlled |
| **RSK-06** | Vendor Lock-in | Architectural coupling to specific prompt format or orchestrator. | High | Medium | **HIGH** | Universal Agent Specification Standard (`agent.yaml`); multi-target runtime adapters. | **LOW** | Controlled |
| **RSK-07** | Performance | CPU-bound model inference causing unacceptable pipeline latency. | High | Medium | **HIGH** | Remote gateway routing for heavy reasoning; CPU-optimized local models (2B-4B) for light tasks. | **MEDIUM** | Monitored |
| **RSK-08** | Operations | Host crash corrupting in-flight factory workflows. | Low | High | **HIGH** | Atomic SQLite task ledger; transactional checkpointing and crash recovery. | **LOW** | Controlled |
