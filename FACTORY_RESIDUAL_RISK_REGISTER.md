# Factory Residual Risk Register

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Status:** BASELINED  
**Owner:** Antigravity 2.0 (Security & Platform Architect)  

---

## 1. Residual Risk Assessment

While the Agent Development Factory establishes robust deterministic security boundaries, secret redaction, and bounded execution guardrails, operating autonomous AI systems on local host infrastructure entails known residual risks. This register explicitly identifies and quantifies those risks.

---

## 2. Residual Risk Table

| Risk ID | Risk Description | Inherent Severity | Applied Mitigations | Residual Likelihood | Residual Impact | Residual Risk Level | Operational Guidance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RR-01** | **Host CPU Inference Latency** | HIGH | Fast quantized models (2B-4B) prioritized; OmniRoute gateway used for complex reasoning. | Medium | Medium | **MEDIUM** | Avoid executing 32B+ local models directly on CPU; use OmniRoute for complex tasks. |
| **RR-02** | **Windows Subprocess Isolation Limits** | HIGH | Environment sanitization, explicit working directory lockdown, path traversal checks. | Low | Medium | **LOW** | Do not execute untrusted third-party binaries outside the factory runtime. |
| **RR-03** | **Gateway Connection Drop** | MEDIUM | Retry backoff (max 3), offline fallback to local process runtime, clear error mapping. | Low | Low | **LOW** | Monitor port 20128/31415 status via `factory status`. |
| **RR-04** | **Hermes Cron Retry Failures** | MEDIUM | Factory does not depend on Hermes cron; uses internal durable SQLite state ledger. | Low | Low | **LOW** | Existing cron jobs in Hermes remain monitored separately; factory jobs are independent. |
| **RR-05** | **Supply-Chain Compromise in External Skills** | CRITICAL | Skill Quarantine AST scanner; prohibits dynamic calls (`eval`, `exec`, arbitrary shell). | Very Low | High | **LOW** | All external skills must undergo quarantine review before registry promotion. |
