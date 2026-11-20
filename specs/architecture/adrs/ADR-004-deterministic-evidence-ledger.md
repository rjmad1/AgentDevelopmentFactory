# ADR-004: Deterministic Append-Only Evidence Ledger

**Status:** ACCEPTED  
**Date:** 2026-11-03  
**Deciders:** Staff Software Engineer, Independent Architecture Auditor  

---

## Context
AI agents often report conversational claims of success ("I have finished the task and verified it") without tangible evidence. Narrative assertions are vulnerable to hallucination and unverified regressions.

## Decision
All state transitions, evaluation outcomes, and triage determinations must be permanently recorded to an append-only JSON Lines event ledger (`check_events.jsonl` / `task_events.jsonl`). Materialized state (`evidence.json`) must be mathematically derivable from the event stream. A state transition cannot succeed unless supporting cryptographic artifacts (SHA-256 digests, output files) exist on disk.

## Consequences
* **Positive:** Cryptographically verifiable audit trails; zero tolerance for phantom successes.
* **Negative:** Modest disk overhead for event storage and hash verification.
