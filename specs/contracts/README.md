# Machine-Readable Contracts & Schemas

**Classification:** Normative Machine-Readable Contracts  
**Status:** ACTIVE & ENFORCEABLE  

---

## 1. Overview

This directory houses the authoritative machine-readable JSON schemas governing agent specifications, inter-agent communication packets, and verification ledgers.

---

## 2. Contracts Inventory

| Contract | Format | Target Subsystem | Description |
| :--- | :--- | :--- | :--- |
| **`agent.schema.json`** | JSON Schema (Draft 2020-12) | Control Plane & Workbench | Definitive schema for the Universal Agent Specification Standard (`agent.yaml`). |
| **`hermes-packets/critic_packet.schema.json`** | JSON Schema | Hermes Critic Agent | Contract for surgical criticism and security review packets. |
| **`hermes-packets/verifier_packet.schema.json`** | JSON Schema | Hermes Verifier Agent | Contract for independent verification and test failure bundles. |
| **`hermes-packets/doc_packet.schema.json`** | JSON Schema | Hermes Doc Agent | Contract for automated documentation generation packets. |

---

## 3. Validation

All contracts in this directory are validated during CI/CD using `npm run lint` and `pytest tests/test_schema.py`.
