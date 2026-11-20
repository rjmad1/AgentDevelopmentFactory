# Specification Naming & Formatting Conventions

**Policy ID:** POL-SPEC-03  
**Version:** 1.0.0  
**Effective Date:** November 20, 2026  
**Status:** MANDATORY & ENFORCEABLE  

---

## 1. Directory & File Naming Rules

All files and directories under `specs/` must adhere to strict, deterministic naming conventions to ensure cross-platform compatibility and machine readability.

### Rules:
1. **Lowercase with Hyphens:** All filenames and directory names must use lowercase alphanumeric characters separated by hyphens (kebab-case). Example: `master-architecture.md`, `001-bounded-authoring-slice`.
2. **Numeric Ordering Prefixes:** Where chronological or logical ordering is essential, use three-digit zero-padded numeric prefixes:
   - Features: `specs/features/001-feature-name/`
   - Audit Reports: `specs/audit/01-repository-discovery.md`
   - ADRs: `specs/architecture/adrs/ADR-001-title.md`
3. **No Special Characters or Spaces:** No spaces, underscores, periods (except `.md`/`.json`), or URI-reserved characters are permitted in filenames.

---

## 2. Requirement Identifier Syntax

Every requirement across the project must bear a unique, permanent, structured identifier conforming to the following regular expression:

$$\text{REQ}-[A-Z]{2,4}-[0-9]{2,3}$$

### Domain Taxonomy:
* `REQ-GOV-XX`: Governance, vendor agnosticism, reproducibility, zero-cost rules.
* `REQ-SPEC-XX`: Universal Agent Specification schema, authority, and quotas.
* `REQ-CTL-XX`: Control Plane, finite state machine, intake, task ledger.
* `REQ-WB-XX`: Workbench, workspace provisioning, code/test generation, packaging.
* `REQ-ADP-XX`: Provider adapters, Hermes harness, OmniRoute.
* `REQ-RT-XX`: Runtime execution, process isolation, resource ceilings.
* `REQ-EVAL-XX`: Evaluation framework, Deep Evaluator, LangSmith telemetry.
* `REQ-SEC-XX`: Security architecture, secret redactor, AST quarantine, approval gates.
* `REQ-OPS-XX`: Operational runbooks, watcher loops, packet bundlers, CI/CD.

---

## 3. GitHub Spec Kit Feature Folder Standard

Each feature specification within `specs/features/` must use the official Spec Kit four-artifact structure:

```
specs/features/NNN-feature-name/
├── spec.md         # What & Why (User stories, functional requirements, acceptance criteria)
├── plan.md         # How (Architecture, technology, data model, testing approach)
├── tasks.md        # Execution breakdown (Sequential, dependency-ordered work units)
└── checklist.md    # Intent quality verification (Unit tests of requirements)
```
