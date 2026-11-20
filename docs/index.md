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

```text
┌─────────────────────────────────────────────────────────────┐
│                 CONTROL PLANE (Governance)                  │
│  - Request Intake & Triage (CONFIRMED vs PROPOSED)          │
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
* **[Capability Roadmap](ADF_Capability_Map_Roadmap.md)**: Honest implemented / planned / pending status for every capability, measured against Baseline v1.0.0 (ADF-001…ADF-040).
* **[Evals and Guardrails Specification](adf-evals-and-guardrails.md)**: Operating spec for evals, guardrails, and release criteria.
* **[Product Contract](factory_product_contract.md)**: Reconciled v1 scope, supervised evaluation capability, multi-dimensional evidence architecture, and hard disqualification gates.
* **[Capability & Acceptance Map](factory_capability_and_acceptance_map.md)**: Core capabilities, inputs/outputs, user decision points, and observable criteria.
* **[Paper Interaction Walkthrough](factory_paper_interaction_walkthrough.md)**: Concrete interaction dialogue tracing intake, clarification, spec sign-off, and revision cycles.
* **[Development Pipeline Playbook](DEVELOPMENT_PIPELINE.md)**: The Tri-Tier architecture, Hermes agent fleet, ZipAI token protocol, and developer SOP.
* **[Persona Opportunity Map](factory_persona_opportunity_map.md)**: Persona analysis, Builderpack competitive assessment, and progressive disclosure model.

### API & Engine References
* **[Authoring Core API (`src/core.js`)](api/core.md)**: Zero-dependency hashing, containment, and triage engine.
* **[Command-Line Interfaces](api/cli.md)**: Complete usage guides for both Node.js and Python CLIs.
* **[Control Plane API](api/control_plane.md)**: Intake, lifecycle, orchestrator, and task ledger.
* **[Evaluations API](api/evals.md)**: Deep Evaluator, LangSmith adapter, metrics, and test runner.
* **[Security Architecture](api/security.md)**: Quarantine sandbox, approval gates, and secret redactor.

---

## 📦 Quick Start

### 1. Authoring CLI (Node.js)
```bash
# Run integrity tests
node test/runner.js

# Run doctor diagnostic
node src/cli.js doctor

# Scaffold new requirements template
node src/cli.js scaffold-requirements --output ./requirements.json

# Initialize a new revision
node src/cli.js init-revision --brief fixtures/synthetic_brief_v1.txt --requirements fixtures/synthetic_requirements_v1.json --revision-id rev-001

# Export Universal Agent Spec YAML
node src/cli.js export-agent-spec --revision rev-001
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
