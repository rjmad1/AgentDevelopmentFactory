# LangSmith Free Tier Telemetry

The Agent Development Factory features native support for **LangSmith Developer / Free Tier** to enable enterprise-grade evaluation tracing and dataset observability at zero software cost.

---

## 🎁 Free Tier Overview

- **Included Traces:** 5,000 free traces per month.
- **Projects:** Unlimited projects and datasets.
- **Cost:** $0.00 / month (no credit card required).
- **Latency Impact:** Asynchronous or low-overhead REST dispatch (<15ms).

---

## ⚙️ Configuration & Activation

To activate LangSmith tracing in GitHub Actions:

1. Sign up for a free LangSmith account at [smith.langchain.com](https://smith.langchain.com).
2. Generate a Personal API Key.
3. Add the key to your GitHub repository secrets:
   - Navigate to `Settings` -> `Secrets and variables` -> `Actions`.
   - Name: `LANGSMITH_API_KEY`.
   - Value: `<your-api-key>`.

The GitHub Actions workflow will automatically inject:

```yaml
env:
  LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
  LANGSMITH_PROJECT: "agent-development-factory"
  LANGCHAIN_TRACING_V2: "true"
```

---

## 🛡️ Zero-Cost Offline Fallback

If `LANGSMITH_API_KEY` is not configured (e.g., local developer workstations or public fork pull requests), the `LangSmithAdapter` automatically detects the missing key and transitions to **Local Deep Evaluator Mode**:

- All tests and quality gates execute completely offline.
- Telemetry is recorded in structured local logs (`reports/eval_results.json`).
- Zero network requests are made.
- CI/CD builds pass with 100% reliability.
