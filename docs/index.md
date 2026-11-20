# Agent Development Factory

[![Zero-Cost CI/CD](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/ci.yml/badge.svg)](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/ci.yml)
[![Pages Deployment](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/docs.yml/badge.svg?branch=gh-pages)](https://rjmad1.github.io/AgentDevelopmentFactory/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Welcome to the **Agent Development Factory** documentation portal.

The Factory transforms natural-language workflow briefs into inspectable, portable, safe, and verifiable **Agent Build Packs**, backed by an append-only evidence ledger, deterministic verification gates, and an asynchronous multi-agent pipeline.

$$\text{Brief} \longrightarrow \text{Structured Requirements} \longrightarrow \text{Inspectable Specification \& Manifest} \longrightarrow \text{Append-Only Evidence Ledger} \longrightarrow \text{Deterministic Verification \& Build}$$

---

## 🏛️ Tri-Tier & Three-Plane Architecture

The factory operates a dual-tier modular architecture that enforces strict separation of responsibilities:

1. **Tier 1 — Fast Authoring & Triage Front-End (`src/core.js`, `src/cli.js`)**:
   - Zero-dependency Node.js CLI.
   - Lexical and real filesystem containment validation.
   - Deterministic SHA-256 requirement triage (`CONFIRMED`, `PROPOSED`, `UNRESOLVED`).
   - Append-only check event stream (`check_events.jsonl`) and immutable revision store.
2. **Tier 2 — Industrial Execution & Verification Back-End (`agent_factory/`)**:
   - Three-Plane Architecture (Control Plane, Workbench Plane, Runtime & Verification Plane).
   - Universal Agent Spec validation (Pydantic & JSONSchema).
   - Ephemeral isolated workspaces and code/test synthesis.
   - Deep Evaluator local grading and LangSmith Free Tier telemetry.
3. **Tier 3 — Autonomous Fleet Governance (`.hermes/AUTONOMOUS_FLEET.md`, `scripts/`)**:
   - Watcher loop (`scripts/autonomous-loop.js`) and pre-commit hooks.
   - Deterministic packet bundlers for Critic, Verifier, and Documentation agents.
   - GitHub Actions CI/CD and automated Wiki sync.

```
┌─────────────────────────────────────────────────────────────┐
│              AUTHORING & CONTROL PLANE (Tier 1 & 2)         │
│  - Brief Intake, Triage (CONFIRMED / PROPOSED)              │
│  - Immutable Revision Stores (SHA-256)                      │
│  - Task Ledger (Append-Only Event Stream)                   │
│  - Orchestrator Engine & State Transitions                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 WORKBENCH PLANE (Execution)                 │
│  - Ephemeral Isolated Workspaces                            │
│  - Deterministic Code Generator & Test Synthesizer          │
│  - Candidate Release Packager & Checksum Verifier           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 VERIFICATION & RUNTIME PLANE                │
│  - Sandboxed Local Process Execution                        │
│  - Multi-Metric Graders (ExitCode, Markdown, JSON, AST)     │
│  - Deep Evaluator & LangSmith Observability                 │
│  - Self-Healing Remediation Loop                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 Quick Navigation

### Product Contracts & Specifications
* **[Product Contract](factory_product_contract.md)**: Reconciled v1 scope, supervised evaluation capability, multi-dimensional evidence architecture, and hard disqualification gates.
* **[Capability & Acceptance Map](factory_capability_and_acceptance_map.md)**: Core capabilities, inputs/outputs, user decision points, and observable criteria.
* **[Paper Interaction Walkthrough](factory_paper_interaction_walkthrough.md)**: Concrete interaction dialogue tracing intake, clarification, spec sign-off, and revision cycles.
* **[Development Pipeline Playbook](DEVELOPMENT_PIPELINE.md)**: The Tri-Tier architecture, Hermes agent fleet, ZipAI token protocol, and developer SOP.
* **[Persona Opportunity Map](factory_persona_opportunity_map.md)**: Persona analysis, Builderpack competitive assessment, and progressive disclosure model.

### API & Engine References
* **[Authoring Core API (`src/core.js`)](api/core.md)**: Zero-dependency hashing, containment, and triage engine.
* **[Command-Line Interfaces](api/cli.md)**: Usage guides for both Node.js and Python CLIs.
* **[Control Plane API](api/control_plane.md)**: Intake, lifecycle, orchestrator, and task ledger.
* **[Evaluations API](api/evals.md)**: Deep Evaluator, LangSmith adapter, metrics, and test runner.
* **[Security Architecture](api/security.md)**: Quarantine sandbox, approval gates, and secret redactor.

---

## 📦 Quick Start

### 1. Authoring CLI (Node.js)
```bash
# Run integrity tests
node test/runner.js

# Initialize a new revision
node src/cli.js init-revision --brief fixtures/sample_brief.txt --requirements fixtures/sample_reqs.json --revision-id rev-001
```

### 2. Platform Back-End (Python)
```bash
# Set up Python virtual environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run Python verification suite
pytest tests/

# Run automated Deep Evaluator
python scripts/run_evals.py
```
