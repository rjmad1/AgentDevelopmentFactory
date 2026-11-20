# Getting Started with Agent Development Factory

This guide walks you through setting up, testing, evaluating, and documenting agents with the Agent Development Factory.

---

## 📋 Prerequisites

- **Python:** 3.11 or later
- **Git:** Standard git client
- **Optional:** Free LangSmith account for cloud tracing

---

## 🛠️ Step 1: Environment Setup

Clone and install dependencies:

```bash
git clone https://github.com/rjmad1/AgentDevelopmentFactory.git
cd AgentDevelopmentFactory

# Create and activate Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Step 2: Running Automated Verification Tests

Execute all 28 automated tests:

```bash
pytest
```

To run individual test domains:
```bash
pytest tests/test_control_plane.py
pytest tests/test_evals.py
pytest tests/test_verification_pipeline.py
```

---

## 📊 Step 3: Running Deep Evaluator

Run the evaluation runner across deployed candidate agents:

```bash
python scripts/run_evals.py
```

Inspect the generated evaluation ledger:
```bash
cat reports/eval_results.json
```

---

## 📚 Step 4: Previewing Documentation Locally

Launch the MkDocs live documentation server:

```bash
mkdocs serve
```

Browse to `http://localhost:8000` to inspect the generated API references and architecture specifications.

---

## 🚀 Step 5: Pushing to GitHub & Verifying GitHub Pages

When you push code to GitHub:
```bash
git add .
git commit -m "feat: enhance verification and docs pipeline"
git push origin main
```

GitHub Actions will automatically:
1. Run syntax verification (`py_compile`).
2. Run unit and integration tests (`pytest`).
3. Execute the Deep Evaluator verification suite.
4. Build MkDocs documentation with `mkdocstrings`.
5. Deploy documentation straight to `https://rjmad1.github.io/AgentDevelopmentFactory/`.
