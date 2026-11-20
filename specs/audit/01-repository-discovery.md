# Audit Report 01: Repository Discovery & Baseline Assessment

**Audit ID:** AUD-01-REPO-DISCOVERY  
**Date:** November 20, 2026  
**Auditors:** Principal Software Architect, DevSecOps Engineer, Independent Architecture Auditor  
**Status:** COMPLETE & BASELINED  

---

## 1. Executive Summary

This repository discovery report establishes the empirical foundation for brownfield Specification-Driven Development (SDD) adoption in the **Agent Development Factory** project. It documents the directory hierarchy, git history, dual-stack codebase, toolchains, and environment state discovered prior to any structural modifications.

---

## 2. Repository Identification & Infrastructure

| Property | Value / Evidence |
| :--- | :--- |
| **Local Repository Root** | `D:\1_Hermes Working Folder_Directory\1_Projects\Agent Development Factory` (confirmed `.git` root) |
| **GitHub Remote URL** | `https://github.com/rjmad1/AgentDevelopmentFactory.git` |
| **Remote Slug** | `rjmad1/AgentDevelopmentFactory` |
| **Active Local Branch** | `sdd-adoption` (created from `main` @ `532c097`, merged with `origin/main` @ `e738157`) |
| **Merge Base** | Commit `dda69087748db556870dc85787dc4d606630ccae` |
| **Primary Languages** | Python 3.11+ (`agent_factory/`), JavaScript / Node.js 20+ (`src/`, `scripts/`) |
| **Package Managers** | `pip` (`requirements.txt`), `npm` (`package.json`, 0 external dependencies) |
| **Installed Spec Kit CLI**| `specify 1.3.0` located at `C:\Users\rajaj\.local\bin\specify.exe` |

---

## 3. Directory Hierarchy Inventory

```
AgentDevelopmentFactory/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Node.js tests + linter + contract validation
│       ├── docs.yml               # MkDocs documentation build & GitHub Pages publish
│       ├── pipeline.yml           # Python automated test + Deep Evaluator pipeline
│       └── wiki-sync.yml          # Automated bi-directional Wiki synchronization
├── .hermes/
│   ├── AUTONOMOUS_FLEET.md        # Hermes fleet protocols & agent packet contracts
│   └── packets/                   # Ephemeral packet storage (git-ignored)
├── .specify/                      # GitHub Spec Kit project configuration & scripts
│   ├── memory/constitution.md     # Project constitution
│   ├── templates/                 # spec, plan, tasks, checklist templates
│   └── scripts/powershell/        # Automation scripts for feature lifecycle
├── agent_factory/                 # Industrial Factory Back-End (Python)
│   ├── adapters/                  # Hermes, OmniRoute provider adapters
│   ├── control_plane/             # Intake, state machine orchestrator, task ledger
│   ├── evals/                     # Deep Evaluator, LangSmith adapter, graders, runner
│   ├── registry/                  # Capability registry, tool discovery
│   ├── remediation/               # Diagnostic engine and self-healing loop
│   ├── runtime/                   # LocalProcessRuntime, process sandboxing
│   ├── security/                  # Secret redactor, AST quarantine, approval gates
│   ├── specs/                     # Universal agent schema and validator
│   └── workbench/                 # Workspace generator, code/test generator, packager
├── data/                          # Seed data & registries (capability_registry.json)
├── deployments/                   # Reference agent deployment packages & test fixtures
├── docs/                          # MkDocs source documentation & contracts
│   ├── api/                       # API docs (cli.md, core.js, control plane, etc.)
│   ├── architecture/              # Promoted architecture markdown documents
│   ├── authoring/                 # Authoring contracts and maps
│   ├── guides/                    # Operations and recovery runbooks
│   └── verification/              # Deep Evaluator and pipeline documentation
├── schemas/                       # JSON Schemas for Hermes agent packets
│   └── hermes/                    # critic_packet, verifier_packet, doc_packet schemas
├── scripts/                       # Automation scripts, loop watchers, packet bundlers
├── specs/                         # Official GitHub Spec Kit directory
│   ├── README.md                  # Master specification index
│   ├── audit/                     # Audit deliverables (01-05)
│   ├── governance/                # SDD governance & lifecycle policies
│   ├── architecture/              # Promoted system architecture & ADRs
│   ├── contracts/                 # Machine-readable schemas
│   ├── features/                  # Spec Kit feature specs
│   └── archive/                   # Preserved 2026-11-03 baseline
├── src/                           # Zero-Dependency Authoring Front-End (Node.js)
│   ├── core.js                    # Deterministic hashing, containment & triage logic
│   └── cli.js                     # Standalone authoring CLI
├── test/                          # Node.js repeatable test suite (runner.js)
├── tests/                         # Python pytest suite (42 test cases)
├── mkdocs.yml                     # Unified MkDocs configuration
├── package.json                   # Node.js module configuration
├── requirements.txt               # Python dependencies
└── README.md                      # Repository root documentation
```

---

## 4. Git Divergence & Reconciliation Analysis

### Historical Divergence Trace
```
      o dda6908 (Merge Base: "Add product contracts, capability maps...")
     / \
    /   \
   /     * 57bd489 feat(infra): Hermes parallel agent pipeline
  /      * 873f811 docs: expand README with Tri-Tier architecture
 /       * b4c59cd feat(evals,docs): LangSmith eval harness & MkDocs CI
|        * e738157 feat(automation): autonomous watcher & wiki sync (origin/main)
* 532c097 feat(pipeline): implement Python platform & docs (local main)
 \      /
  \    /
   * 98ee60a chore(reconcile): merge origin/main into sdd-adoption (Reconciled)
```

### Reconciliation Findings
1. **Preservation of Dual-Stack Functionality:**
   - The Python platform (`agent_factory/`) and tests (`tests/`) were fully retained.
   - The Node.js authoring engine (`src/`), Hermes fleet scripts (`scripts/`), and evals (`test/evals/`) were fully retained.
2. **Unified Documentation Portal:**
   - Both stacks were merged into a single `mkdocs.yml` and `README.md`, eliminating conflicting configurations.
3. **Preserved Local Modifications:**
   - Uncommitted deployment artifacts in `deployments/develop_an_agent_that_analyzes/artifacts/` remained undisturbed throughout the reconciliation.
