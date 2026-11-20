# ADR-003: Zero Unapproved Paid Fallback

**Status:** ACCEPTED  
**Date:** 2026-11-03  
**Deciders:** Senior Product Manager, DevSecOps Engineer  

---

## Context
Automated multi-agent pipelines risk catastrophic cloud billing spikes if local or free inference tiers fail and the framework automatically falls back to unmetered commercial APIs.

## Decision
We enforce a hard stop at a `$0.00` paid spend ceiling (`REQ-GOV-05`). When free or local models are rate-limited or exhausted, the system transitions immediately to `BLOCKED`. Automatic promotion to paid APIs is strictly prohibited without an explicit human-signed spend token.

## Consequences
* **Positive:** Complete protection against unexpected financial costs.
* **Negative:** Execution halts when free quotas are exhausted until human intervention or reset.
