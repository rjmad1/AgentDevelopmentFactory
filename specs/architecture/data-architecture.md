# Factory Data Architecture

**Document Version:** 1.1.0  
**Date:** November 20, 2026  
**Status:** BASELINED & APPROVED  
**Provenance:** Promoted from historical baseline `FACTORY_DATA_ARCHITECTURE.md`  

---

## 1. Conceptual Data Stores

The Factory partitions persistence into four dedicated conceptual data stores with clear boundaries:

1. **Control Plane State Store (`data/factory_state.db` & `data/task_events.jsonl`):**
   - SQLite relational database for transactional state machine queries.
   - Append-only JSON Lines event stream recording immutable lifecycle transitions.
2. **Capability Registry (`data/capability_registry.json`):**
   - Catalog of reusable agent skills, tools, and schemas indexed by capability tokens.
3. **Ephemeral Workspaces (`workspaces/`):**
   - Temporary file hierarchies holding synthesized agent source code, tests, and local run outputs.
4. **Release Store (`releases/`):**
   - Immutable packaged ZIP releases, cryptographically sealed with `manifest.json` and `checksums.sha256`.

---

## 2. Five-Tier Data Sensitivity Classification

| Tier | Classification | Examples | Storage Location | Retention / Policy |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | Public / Synthetic Data | Public web scrapes, synthetic benchmarks, sample CSVs. | `fixtures/`, `workspaces/*/fixtures/` | Retained indefinitely with release packages. |
| **D2** | Internal Agent Metadata | Agent specifications, lifecycle state, test logs. | `data/factory_state.db`, `specs/` | Permanent audit retention. |
| **D3** | Ephemeral Workspace Code | Intermediate syntheses, draft scripts, debug dumps. | `workspaces/proj_*/` | Ephemeral; auto-pruned upon release or failure. |
| **D4** | Evaluation Telemetry | Latency vectors, grading breakdowns, execution traces. | `reports/eval_results.json`, LangSmith | Retained for regression tracking (90 days). |
| **D5** | Sensitive Credentials | API keys, tokens, signing certificates. | Environment variables only; **never persisted**. | Masked by Secret Redactor before logging. |
