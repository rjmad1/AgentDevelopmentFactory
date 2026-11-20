# Agent Development Factory

[![Zero-Cost CI/CD](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/pipeline.yml/badge.svg)](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/pipeline.yml)
[![Pages Deployment](https://github.com/rjmad1/AgentDevelopmentFactory/actions/workflows/pipeline.yml/badge.svg?branch=gh-pages)](https://rjmad1.github.io/AgentDevelopmentFactory/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)

**Agent Development Factory** is an enterprise-grade meta-product that transforms business-workflow briefs into inspectable, portable, safe, and verifiable **Agent Build Packs**.

The platform is designed under a **Zero-Cost Software Architecture**, pairing GitHub Actions automation, Deep Evaluator local quality gates, LangSmith Free Tier telemetry, and evergreen MkDocs documentation deployed directly to GitHub Pages.

---

## 🏛️ Architecture Highlights

The factory operates a **Three-Plane Architecture** that enforces strict separation of responsibilities:

```
┌─────────────────────────────────────────────────────────────┐
│                       CONTROL PLANE                         │
│  - Request Intake & Triage                                  │
│  - Task Ledger (Append-Only Event Stream)                   │
│  - Orchestrator Engine & State Transitions                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      WORKBENCH PLANE                        │
│  - Ephemeral Isolated Workspaces                            │
│  - Deterministic Code Generator                             │
│  - Test Suite Synthesizer                                   │
│  - Candidate Release Packager                               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 VERIFICATION & RUNTIME PLANE                │
│  - Sandboxed Local Process Execution                        │
│  - Multi-Metric Graders (ExitCode, Markdown, JSON, AST)     │
│  - Deep Evaluator & LangSmith Free Tier Observability       │
│  - Self-Healing Remediation Loop (Max 3 Attempts)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Capabilities

1. **Deterministic Verification Engine (Deep Evaluator)**:
   Every agent candidate is rigorously evaluated against discrete quality gates: Efficacy ($\ge 0.95$), Safety ($= 1.00$, zero unredacted secrets), and Cost ($\$0.00$ software cost).
2. **LangSmith Free Tier Integration**:
   Native telemetry adapter capturing execution traces, inputs, outputs, and quality vectors into LangSmith Developer Tier (5,000 monthly traces at zero cost), with automatic offline fallback to local Deep Evaluator mode.
3. **Automated Source Documentation (`mkdocstrings`)**:
   Evergreen API documentation generated directly from Python source code type annotations and docstrings, continuously deployed to GitHub Pages on every push.
4. **Append-Only Evidence Ledger**:
   Cryptographic hashing (SHA-256) of requirements, specifications, artifacts, and test runs ensures full reproducibility and auditability without state loss.
5. **Defense-in-Depth Security**:
   Automated secret redactor, AST quarantine sandbox, and approval gates for elevated-effect operations (filesystem write, network, process execution).

---

## 📦 Quick Start

### 1. Installation
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/rjmad1/AgentDevelopmentFactory.git
cd AgentDevelopmentFactory
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Run Test Suite
Run the full 28-test verification suite:

```bash
pytest tests/
```

### 3. Run Automated Deep Evaluator
Evaluate deployed agents against quality gates:

```bash
python scripts/run_evals.py
```

### 4. Build & Preview Documentation
Launch local documentation server:

```bash
mkdocs serve
```
Visit `http://127.0.0.1:8000` to browse live documentation.
