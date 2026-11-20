# ADR-002: Three-Plane Separation Model

**Status:** ACCEPTED  
**Date:** 2026-11-03  
**Deciders:** Principal Software Architect, Staff Software Engineer  

---

## Context
Monolithic agent frameworks often combine state management, agent code generation, process execution, and quality evaluation in a single execution context. When errors occur, state becomes corrupted, debugging is difficult, and security boundaries blur.

## Decision
We enforce a strict Three-Plane Separation Model across all factory operations:
1. **Control Plane:** Governs state machine progression, tracks resource ceilings, and records transitions in an atomic SQLite database and append-only event stream.
2. **Workbench Plane:** Generates code, synthesizes tests, and packages release candidates in isolated ephemeral workspaces.
3. **Verification & Runtime Plane:** Executes synthesized code in sandboxed local processes and scores quality against objective multi-metric graders.

## Consequences
* **Positive:** High testability, fault isolation, and clear audit boundaries. Crashes in agent code cannot corrupt factory orchestration state.
* **Negative:** Requires inter-plane serialization and file-based state handoffs.
