# Factory Security Assessment

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Lead Security Architect:** Antigravity 2.0  
**Scope:** Factory Host, Subprocess Isolation, Gateways, Runtimes & Registries  
**Status:** COMPLETED & BASELINED  

---

## 1. Security Baseline Audit

A comprehensive security assessment of the host environment and proposed Agent Development Factory architecture was conducted on 3 November 2026. The assessment examined OS boundaries, credential handling, listening ports, supply-chain risks, and execution sandboxes.

### Summary Assessment Matrix:

| Domain | Baseline Status | Risk Level | Factory Mitigation |
| :--- | :--- | :--- | :--- |
| **OS & Host Process** | Windows 11 Pro, single-user admin context. Subprocesses inherit user privileges by default. | **HIGH** | Dedicated workspace isolation; environment variable sanitization; path traversal validation before all file operations. |
| **Local AI Gateways** | OmniRoute (Port 20128) and FreeLLMAPI (Port 31415) listening on loopback (`127.0.0.1`). | **MEDIUM** | Both services enforce Bearer token authentication. External exposure blocked by host firewall. |
| **Credential Storage** | Hermes pooled credentials stored in user configuration with hashed IDs. | **LOW** | Factory never reads or copies credential files; uses named references only and scrubs secrets from memory after socket establishment. |
| **Skill / Package Intake** | Hermes has 165+ installed skills; npm/uv packages used by MCP servers. | **HIGH** | Mandatory AST static security scanner (`agent_factory.security.quarantine`) blocks unvetted dynamic code execution (`eval`, `exec`, arbitrary subprocesses). |
| **Logging & Telemetry** | Potential leakage of sensitive prompts or tokens into log files. | **HIGH** | Active `SecretRedactor` stream filter scrubs API tokens, JWTs, and passwords before disk writes. |
| **Autonomous Self-Modification**| Potential for runaway self-healing loops to widen permissions or disable guards. | **CRITICAL** | Anti-forgery approval tokens; immutable golden fixtures; hard-coded 3-attempt ceiling on remediation loops. |

---

## 2. Supply-Chain & Dependency Analysis

The factory core implementation relies exclusively on established, high-maturity open-source libraries already verified in the host Hermes environment:
* `pydantic` (v2.13.0): Data validation and settings management.
* `pyyaml` (v6.0.3): Specification parsing.
* `jsonschema` (v4.25.0): Strict JSON Schema compliance checking.
* `pytest` (v9.1.1): Deterministic test execution.
* `rich` (v15.0.0): Structured CLI presentation.
* `requests` / standard library `urllib`: Local HTTP gateway client.

Zero untrusted or unvetted third-party packages are introduced. All new agent dependencies must be pinned in an explicit `requirements.lock` file accompanied by SHA-256 hashes.
