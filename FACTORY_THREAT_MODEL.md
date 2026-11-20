# Factory Threat Model

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Framework:** STRIDE Methodology  
**Author:** Antigravity 2.0 (Security Architect)  
**Status:** BASELINED  

---

## 1. System Boundary and Threat Actors

```
 [Threat Actors]
 ├── External Attacker (Untrusted Web Inputs / Poisoned Documents)
 ├── Rogue / Hallucinating Agent (Prompt Injection / Excessive Permissions)
 └── Malicious Dependency / Skill (Supply-Chain Compromise)
        │
        ▼ Crosses Boundary
 [Factory Security Perimeter]
 ├── AST Skill Quarantine Pipeline
 ├── Universal Specification Permission Matrix
 ├── Subprocess Environment Sanitizer
 └── Active Secret Redactor
        │
        ▼ Emits
 [Cryptographic Evidence Ledger]
```

---

## 2. STRIDE Threat Analysis & Defense Mapping

### 1. Spoofing
* **Threat:** A compromised subagent attempts to forge an owner approval token to deploy a high-risk package.
* **Impact:** Unauthorized deployment of privileged agents capable of system modifications.
* **Mitigation:** Approval tokens for high-risk actions require HMAC cryptographic verification using a host-local secret not accessible to the agent workspace. Plain-text claims or model summaries are rejected.

### 2. Tampering
* **Threat:** During autonomous remediation, an agent alters test assertions or golden test fixtures to make a failing candidate pass.
* **Impact:** False verified status; deployment of broken software.
* **Mitigation:** Test fixtures and grader scripts are hashed with SHA-256 before the build. The test runner asserts fixture hash equality before accepting test results.

### 3. Repudiation
* **Threat:** Actions are executed or files modified without traceable accountability.
* **Impact:** Inability to audit failures, security breaches, or unexpected cost spikes.
* **Mitigation:** Append-only Cryptographic Evidence Ledger logs every tool invocation, stage transition, duration, and output SHA-256 hash.

### 4. Information Disclosure
* **Threat:** Agent logs or error traces dump environment variables containing API keys (`ANTHROPIC_API_KEY`, etc.).
* **Impact:** Credential theft and account compromise.
* **Mitigation:** Subprocess environments are explicitly sanitized; `SecretRedactor` filters all logs via regex matching before disk persistence.

### 5. Denial of Service
* **Threat:** An agent enters an infinite loop, consumes all local RAM/CPU, or exhausts external model quotas.
* **Impact:** Host system instability and resource exhaustion.
* **Mitigation:** Universal spec enforces hard step limits (`max_steps`), process execution wall-time timeouts (60s), and a strict 3-iteration ceiling on remediation loops.

### 6. Elevation of Privilege
* **Threat:** An agent declared as `draft_only` attempts to execute shell commands to modify host OS files or registry settings.
* **Impact:** Host takeover.
* **Mitigation:** File write tools enforce workspace directory boundaries (`workspaces/<project_id>/`); attempts to write outside the workspace fail immediately with `SecurityViolation`.
