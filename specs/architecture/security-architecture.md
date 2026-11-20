# Factory Security Architecture

**Document Version:** 1.1.0  
**Date:** November 20, 2026  
**Status:** BASELINED & APPROVED  
**Provenance:** Promoted from historical baseline `FACTORY_SECURITY_ARCHITECTURE.md`  

---

## 1. Defense-in-Depth Security Model

The Factory enforces a three-layer security model designed to eliminate credential leaks, unconstrained code execution, and unauthorized side effects:

```
┌─────────────────────────────────────────────────────────────┐
│             LAYER 1: REAL FILESYSTEM CONTAINMENT            │
│  - Path lexical validation (no '../', absolute escapes)     │
│  - Canonical path resolution checking parent boundary       │
│  - Symlink / reparse point escape rejection                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER 2: ACTIVE SECRET REDACTION               │
│  - Real-time regex pattern scanning across all logs & text  │
│  - Masks OpenAI, Anthropic, AWS, GitHub, and bearer tokens  │
│  - Replaces secrets with [REDACTED_API_KEY] markers         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           LAYER 3: STATIC AST QUARANTINE SANDBOX            │
│  - Python AST parsing prior to execution                    │
│  - Blocks arbitrary subprocess invocation (os.system, etc.) │
│  - Blocks unsafe dynamic evaluation (eval, exec, __import__)│
│  - Isolates non-compliant candidates in quarantine/         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Hard Security Boundaries

1. **Zero Unapproved Paid Spend (`REQ-GOV-05`):**
   - The factory operates under a hard stop at `$0.00` paid inference cost unless an explicit spend token is injected.
   - When quota or free models are exhausted, the state machine halts in `BLOCKED`; it never promotes silently to paid APIs.
2. **Real Path Containment (`REQ-SEC-03`):**
   - Implemented in `src/core.js` via `assertRealFsContainment(parentDir, targetPath)`.
   - Resolves canonical paths with `path.resolve` and verifies containment before any disk write.
3. **AST Quarantine Rules (`REQ-SEC-02`):**
   - Implemented in `agent_factory/security/quarantine.py`.
   - Scans AST syntax nodes for `Call`, `Import`, and `Attribute`. Flags forbidden functions (`os.system`, `subprocess.Popen`, `shutil.rmtree`) as `QUARANTINE_VIOLATION`.
