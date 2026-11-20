# ADR-006: Remediation Loop Budget & Circuit Breaker

**Status:** ACCEPTED  
**Date:** 2026-11-03  
**Deciders:** Software Quality and Test Engineering Lead, Senior Product Manager  

---

## Context
Automated self-healing remediation loops can easily degrade into infinite test-failure cycles, burning CPU cycles and tokens while accumulating code churn without converging on a working solution.

## Decision
We enforce a strict circuit breaker on the self-healing remediation loop (`agent_factory.remediation.engine`):
1. Maximum of 3 diagnostic and patching retries per failure scenario.
2. If code does not pass tests after 3 attempts, the state machine halts immediately and transitions the project state to `BLOCKED`.
3. An automated diagnostic report is generated detailing why convergence failed, escalating the issue for human review.

## Consequences
* **Positive:** Prevents runaway loops, token waste, and code degradation.
* **Negative:** Requires human triage when an automated fix cannot converge within 3 retries.
