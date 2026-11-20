# Factory Component Architecture

**Document Version:** 1.1.0  
**Date:** November 20, 2026  
**Status:** BASELINED & APPROVED  
**Provenance:** Promoted from historical baseline `FACTORY_COMPONENT_ARCHITECTURE.md`  

---

## 1. Subsystem Architecture Map

The Factory comprises eight cohesive, loosely coupled subsystems operating across the Three-Plane Model:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. INTAKE & TRIAGE ENGINE                       │
│  - Semantic classification, requirement decomposition                  │
│  - Feasibility analysis, persona mapping, risk tier assignment         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        2. CONTROL PLANE ENGINE                         │
│  - 11-stage FSM lifecycle orchestrator                                 │
│  - Atomic SQLite task ledger & append-only audit stream                │
│  - Human approval token verification & policy enforcement              │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│     3. CAPABILITY REGISTRY      │ │      4. SECURITY & POLICY       │
│ - Semantic tool discovery       │ │ - AST Quarantine sandbox        │
│ - Reusable agent build packs    │ │ - Regex secret redactor         │
│ - Schema validation & versions  │ │ - Approval gates & spend limits │
└────────────────┬────────────────┘ └────────────────┬────────────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   5. WORKBENCH & SYNTHESIS ENGINE                      │
│  - Ephemeral workspace provisioning with filesystem containment        │
│  - Deterministic agent code synthesis & pytest generation              │
│  - ZIP release packager with SHA-256 checksum manifests                │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    6. RUNTIME & PROCESS ISOLATION                      │
│  - Sandboxed local process execution with wall-clock timeouts          │
│  - Hermes Harness adapter & OmniRoute multi-model router               │
│  - Exit code, stdout, and stderr stream capture                        │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 7. EVALUATION & VERIFICATION ENGINE                    │
│  - Multi-metric graders (ExitCode, JSONSchema, Markdown, AST)          │
│  - Deep Evaluator local quality gates (Efficacy >= 0.95, Safety = 1.0) │
│  - LangSmith Free Tier telemetry adapter with offline fallback         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  8. REMEDIATION & SELF-HEALING ENGINE                  │
│  - Automated failure triage and diagnostic generation                  │
│  - Targeted code patching within fixed budget (max 3 retries)          │
│  - Automatic escalation to BLOCKED on budget exhaustion                │
└────────────────────────────────────────────────────────────────────────┘
```
