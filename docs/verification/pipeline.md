# Zero-Cost CI/CD Automation Pipeline

The Agent Development Factory integrates **GitHub Actions** as its central, zero-cost automation engine.

---

## ⚡ Zero-Cost Architecture Overview

Public GitHub repositories receive unlimited GitHub Actions runner minutes (`ubuntu-latest`) at zero cost. By combining this with Python open-source tools and LangSmith's Free Developer Tier (5,000 monthly traces), continuous validation and evergreen documentation are achieved without recurring subscription fees.

```
                    ┌────────────────────────┐
                    │      git push / PR     │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  GitHub Actions Runner │
                    │    (ubuntu-latest)     │
                    └───────────┬────────────┘
                                │
            ┌───────────────────┴───────────────────┐
            │                                       │
┌───────────▼───────────┐               ┌───────────▼───────────┐
│     Job 1: verify     │               │      Job 2: docs      │
│  - Python 3.11 Env    │               │  - MkDocs + Plugins   │
│  - py_compile Syntax  │               │  - mkdocstrings Auto  │
│  - 28 Pytest Tests    │               │  - Strict HTML Build  │
│  - Deep Evaluator     │               │  - Deploy Pages       │
│  - LangSmith Free Trc │               └───────────┬───────────┘
└───────────┬───────────┘                           │
            │                                       │
            ▼                                       ▼
  Quality Gate Verdict                    GitHub Pages Live Site
 (Pass: Deploy / Fail: Halt)             (Continuous Evergreen Docs)
```

---

## 🛠️ Workflow Architecture (`pipeline.yml`)

The pipeline defines two chained jobs:

1. **`verify`**:
   - Executes across Ubuntu Linux runners.
   - Compiles all Python sources using `py_compile`.
   - Runs the 28-test automated verification test suite via `pytest`.
   - Runs `scripts/run_evals.py` (Deep Evaluator + LangSmith Free Tier telemetry).
   - Injects the verification matrix directly into the GitHub Actions Step Summary (`$GITHUB_STEP_SUMMARY`).

2. **`docs`**:
   - Depends on `verify` (executes only when all tests and evaluation gates pass).
   - Generates static documentation using `mkdocs build --strict`.
   - Uses `mkdocstrings[python]` to pull docstrings directly from Python code.
   - Deploys the built HTML bundle directly to GitHub Pages via official `actions/deploy-pages`.

---

## 🔐 Environment & Secrets Configuration

| Variable / Secret | Required? | Purpose | Free Tier Limit |
|---|---|---|---|
| `GITHUB_TOKEN` | Auto-provided | Deploys documentation to GitHub Pages | Included with GitHub Actions |
| `LANGSMITH_API_KEY` | Optional | Dispatches traces to LangSmith Free Tier | 5,000 traces/month ($0.00) |
| `LANGSMITH_PROJECT` | Optional | Project namespace (`agent-development-factory`) | Unlimited projects ($0.00) |
