# Agent Development Factory

[![Factory CI](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/ci.yml/badge.svg)](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/ci.yml)
[![Pages Deployment](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/docs.yml/badge.svg?branch=gh-pages)](https://rjmad1.github.io/AgentDevelopmentFactory/)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D20.0.0-brightgreen.svg)](https://nodejs.org/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/frontend%20deps-0-success.svg)](package.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mkdocs--material-purple.svg)](https://rjmad1.github.io/AgentDevelopmentFactory/)
[![Wiki](https://img.shields.io/badge/GitHub-Wiki-orange.svg)](https://github.com/rjmad1/AgentDevelopmentFactory/wiki)

The **Agent Development Factory** is an enterprise meta-product that transforms business-workflow briefs into inspectable, portable, safe, and verifiable **Agent Build Packs**.

It replaces ad-hoc prompt crafting and opaque agent generation with **specification discipline** (derived from GitHub Spec Kit) and **reusable capability contracts** (derived from modular action paradigms), backed by an **append-only evidence ledger**, **deterministic verification gates**, and an **asynchronous multi-agent pipeline**.

$$\text{Brief} \longrightarrow \text{Structured Requirements} \longrightarrow \text{Inspectable Specification \& Manifest} \longrightarrow \text{Append-Only Evidence Ledger} \longrightarrow \text{Deterministic Verification \& Release}$$

Designed under a **Zero-Cost Software Architecture**, the factory integrates **GitHub Actions** as its central automation engine, executes automated verification test suites using **Deep Evaluator** and **LangSmith's Free Tier**, and employs **MkDocs** with **mkdocstrings** and GitHub Pages to maintain evergreen documentation.

---

## 🏛️ Tri-Tier & Three-Plane System Architecture

The factory enforces strict separation of concerns across a dual-tier modular architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│             TIER 1: FAST AUTHORING & SPEC ENGINE (Node.js)             │
│  - Zero-dependency CLI (Node built-ins: fs, path, crypto)              │
│  - Real filesystem containment & symlink boundary enforcement          │
│  - Deterministic SHA-256 requirement triage (CONFIRMED / PROPOSED)     │
│  - Append-only check event stream (check_events.jsonl) & revisions     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Generates Spec & Manifest
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│             TIER 2: INDUSTRIAL FACTORY PLATFORM (Python)               │
│                                                                        │
│  [CONTROL PLANE]                                                       │
│  - Request Intake & Semantic Classification                            │
│  - Universal Agent Specification Standard (agent.yaml / Pydantic v2)   │
│  - State Machine Orchestrator (11 Lifecycle Stages)                    │
│  - Risk-Based Human Approval Enforcement (Low / Medium / High)         │
│  - Append-Only Task Ledger & Audit Event Stream                        │
│                                                                        │
│  [WORKBENCH PLANE]                                                     │
│  - Isolated Workspace Sandbox (Ephemeral Directory Containment)        │
│  - Deterministic Agent Code Generator & Test Suite Synthesizer         │
│  - Candidate Release Packager & Checksum Hasher                        │
│                                                                        │
│  [VERIFICATION & RUNTIME PLANE]                                        │
│  - Multi-Metric Graders (ExitCode, Markdown, JSON, AST)                │
│  - Deep Evaluator & LangSmith Observability Integration                │
│  - Local Process Sandboxed Execution & AST Quarantine                  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│             TIER 3: HERMES AUTONOMOUS FLEET GOVERNANCE                 │
│  - Autonomous Watcher Loop (scripts/autonomous-loop.js)                │
│  - Surgical Packet Bundlers (Critic, Verifier, Documentation)          │
│  - Pre-commit Hook & GitHub Wiki Automated Sync Pipeline               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
AgentDevelopmentFactory/
├── .github/workflows/          # CI/CD Workflows (ci.yml, docs.yml, wiki-sync.yml)
├── .hermes/                    # Hermes Autonomous Fleet protocols & packet schemas
├── agent_factory/              # Industrial Factory Platform (Python)
│   ├── control_plane/          # Intake, lifecycle state machine, task ledger
│   ├── workbench/              # Code generator, test generator, packager
│   ├── runtime/                # Sandboxed local process execution
│   ├── security/               # Secret redactor, quarantine manager, approval gates
│   ├── registry/               # Capability registry and tool discovery
│   ├── evals/                  # Deep Evaluator and LangSmith telemetry adapter
│   └── specs/                  # Universal Agent Spec schemas and validator
├── src/                        # Zero-Dependency Authoring Front-End (Node.js)
│   ├── core.js                 # Pure deterministic hashing, FS containment & triage
│   └── cli.js                  # Standalone authoring CLI
├── specs/                      # Specification-Driven Development (GitHub Spec Kit)
│   ├── README.md               # Master specification index & navigation
│   ├── audit/                  # Baseline discovery, register, and gap reports
│   ├── governance/             # Specification management policy & lifecycle rules
│   ├── architecture/           # Master, component, data, security architecture
│   ├── contracts/              # Machine-readable schemas (agent, packets)
│   ├── features/               # Spec Kit feature specifications (001, 002, ...)
│   └── archive/                # Preserved historical specification baselines
├── docs/                       # Evergreen documentation portal (MkDocs)
├── scripts/                    # Automation scripts & fleet packet bundlers
├── test/                       # Node.js repeatable authoring test suite
├── tests/                      # Python automated verification test suite
├── mkdocs.yml                  # MkDocs Material configuration
├── package.json                # Node.js workspace configuration
├── requirements.txt            # Python dependencies (Pydantic, pytest, mkdocs, jsonschema)
└── README.md
```

---

## 🚀 Quick Start

### 1. Authoring Front-End (Node.js)

The authoring front-end requires Node.js (`v18.0.0+` or `v20.0.0+`) with **zero external npm dependencies**.

```bash
# Run the dual-run repeatable test suite (13 comprehensive tests in ~1s)
npm test

# Run contract, JSON, and syntax linting (0 tokens / ~200ms)
npm run lint

# Initialize an immutable revision
node src/cli.js init-revision \
  --brief fixtures/sample_brief.txt \
  --requirements fixtures/sample_reqs.json \
  --revision-id rev-001

# Run deterministic triage and schema validation checks
node src/cli.js run-check --revision rev-001 --check CHK-STATIC-SCHEMA
node src/cli.js run-check --revision rev-001 --check CHK-REQUIREMENTS-TRIAGE

# Inspect revision and verify evidence consistency
node src/cli.js inspect --revision rev-001
node src/cli.js verify-consistency --revision rev-001

# Generate surgical packets for the Hermes Parallel Fleet
npm run packets
```

### 2. Platform Back-End (Python)

```bash
# Setup Python 3.11+ virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run full Python automated test suite
pytest tests/

# Run automated Deep Evaluator
python scripts/run_evals.py

# Launch live documentation server
mkdocs serve
```

---

## 📚 Documentation & Wiki Index

For in-depth architectural specifications and governance frameworks, consult:

| Document | Description |
| :--- | :--- |
| **[Master Specification Index](specs/README.md)** | Master navigation portal for Spec-Driven Development (GitHub Spec Kit). |
| **[Product Contract](docs/factory_product_contract.md)** | Reconciled v1 scope, supervised evaluation capability, and hard disqualification gates. |
| **[Development Pipeline Playbook](docs/DEVELOPMENT_PIPELINE.md)** | Production engineering guide to token optimization and the Hermes workforce. |
| **[Capability & Acceptance Map](docs/factory_capability_and_acceptance_map.md)** | Core capabilities, inputs/outputs, user decision points, and observable criteria. |
| **[Paper Interaction Walkthrough](docs/factory_paper_interaction_walkthrough.md)** | Concrete dialogue walkthrough: intake, clarification, spec sign-off, and revision cycles. |
| **[GitHub Wiki](https://github.com/rjmad1/AgentDevelopmentFactory/wiki)** | Searchable, cross-linked documentation portal covering specifications, architecture, and API references. |

---

## 📄 License & Notice

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
