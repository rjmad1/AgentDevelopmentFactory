# Factory Risk Management Policy & Register

**Policy ID:** POL-SPEC-07  
**Version:** 1.0.0  
**Effective Date:** November 20, 2026  
**Status:** MANDATORY & ENFORCEABLE  
**Provenance:** Consolidated from `FACTORY_RISK_REGISTER.md` & `FACTORY_RESIDUAL_RISK_REGISTER.md`  

---

## 1. Risk Governance Framework

The Factory operates a proactive, defense-in-depth risk management framework that categorizes failure modes across four severity levels:

* **CRITICAL:** Threatens host system integrity, exposes API credentials, corrupts persistent state, or bypasses financial boundaries.
* **HIGH:** Causes agent hallucination in production, introduces unverified code, or breaks reproducible builds.
* **MEDIUM:** Impacts throughput, inflates inference latency, or requires manual developer intervention.
* **LOW:** Cosmetic discrepancies, formatting variations, or minor telemetry drops.

---

## 2. Master Risk Register

| Risk ID | Threat Scenario | Initial Risk | Architectural Mitigation | Residual Risk | Verification Method |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **RSK-01** | Surprise API cloud billing spike. | CRITICAL | Hard stop at $0.00 spend ceiling (`REQ-GOV-05`); zero unapproved paid fallback. | LOW | Quota exhaustion canary probe. |
| **RSK-02** | Accidental credential leakage in code or logs. | CRITICAL | Active Regex Secret Redactor (`agent_factory/security/redactor.py`) masks tokens in real-time. | LOW | Automated regex secret injection tests. |
| **RSK-03** | Malicious or runaway agent execution. | CRITICAL | AST Quarantine Sandbox (`agent_factory/security/quarantine.py`) blocks unsafe primitives (`exec`, `eval`, `os.system`). | LOW | Static AST violation tests. |
| **RSK-04** | Filesystem traversal or symlink escape. | CRITICAL | Real filesystem containment guard (`src/core.js` `assertRealFsContainment`) checks resolved canonical paths. | LOW | Symlink & directory traversal test suite. |
| **RSK-05** | Hallucinated "Done" claims without artifacts. | HIGH | State machine requires cryptographically verified execution evidence (`check_events.jsonl`, `evidence.json`). | LOW | Negative artifact omission tests. |
| **RSK-06** | Vendor lock-in to proprietary runtime. | HIGH | Strict decoupling of agent contracts from runtime prompts (`REQ-GOV-01`); multi-runtime adapters. | LOW | Multi-target compilation tests. |
| **RSK-07** | State database corruption during crash. | HIGH | Append-only event streams paired with SQLite atomic snapshot backups. | LOW | Crash recovery and DB integrity tests. |
| **RSK-08** | Infinite self-healing remediation loops. | MEDIUM | Fixed remediation budget (max 3 diagnostic retries); automatic escalation to `BLOCKED`. | LOW | Remediation retry exhaustion test. |
| **RSK-09** | Untracked requirement drift. | MEDIUM | Mandatory GitHub Spec Kit feature specifications (`specs/features/`) and bi-directional traceability matrix. | LOW | CI contract & spec consistency linting. |
| **RSK-10** | Divergent local and remote documentation. | LOW | Automated GitHub Actions Wiki and Pages synchronization on every push. | LOW | CI/CD automated deployment verification. |
