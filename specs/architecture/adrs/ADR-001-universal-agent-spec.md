# ADR-001: Universal Agent Specification Standard

**Status:** ACCEPTED  
**Date:** 2026-11-03  
**Deciders:** Principal Software Architect, Senior Product Manager  

---

## Context
Agent frameworks commonly couple agent definitions to specific prompt templates, proprietary LLM APIs, or orchestrator runtimes. This creates severe vendor lock-in, prevents portability across harnesses, and makes automated testing difficult.

## Decision
We establish a declarative, vendor-agnostic Universal Agent Specification standard (`agent.yaml` backed by Pydantic v2 and JSONSchema). The specification defines:
1. Agent identity and semantic purpose.
2. Explicit input/output data schemas.
3. Permitted tool permissions (`READ_PUBLIC` to `SPEND_DELETE`).
4. Strict resource quotas (`max_steps`, `max_wall_time_seconds`, `paid_spend_ceiling`).
5. Policy-bound denial handling.

## Consequences
* **Positive:** Complete decoupling of agent capabilities from runtime models; allows identical agent specifications to compile across Local Process and Hermes Harness.
* **Negative:** Requires upfront specification modeling before code generation can occur.
