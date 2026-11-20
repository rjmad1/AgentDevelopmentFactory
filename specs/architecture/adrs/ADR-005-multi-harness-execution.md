# ADR-005: Multi-Harness Execution & Vendor Agnosticism

**Status:** ACCEPTED  
**Date:** 2026-11-03  
**Deciders:** Principal Software Architect, DevSecOps Engineer  

---

## Context
Deploying agents exclusively into a proprietary platform runtime binds the entire project to that vendor's lifecycle, licensing, and infrastructure changes.

## Decision
The factory must support multi-harness compilation and execution (`REQ-GOV-01`). Agents synthesized by the workbench must run cleanly as standalone Python processes (`LocalProcessRuntime`) or inside autonomous agent orchestrators (such as Hermes Agent or Docker containers) without changing the core specification (`agent.yaml`).

## Consequences
* **Positive:** Complete vendor neutrality and maximum deployment flexibility.
* **Negative:** Requires maintaining multiple runtime adapters and environment parity tests.
