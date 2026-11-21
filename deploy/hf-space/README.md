---
title: Agent Development Factory
emoji: 🏭
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 3000
pinned: false
license: mit
short_description: Autonomous assembly line for zero-cost, sandboxed software agents
---

# Agent Development Factory (ADF) on Hugging Face Spaces

This Hugging Face Space hosts the **Agent Development Factory (ADF)** Control Plane API and Google Material Design Hybrid UI on Hugging Face's **100% Free Docker Tier** (2 vCPU, 16GB RAM, Zero Cost).

## 🚀 Live Services Included
- **Control Plane & Hybrid Material Design UI:** Port `3000`
- **SRE Probes & Healthchecks:** `/healthz`, `/readyz`, `/metrics`
- **Zero-Cost Spend Ceiling:** Enforced `$0.00` invariant across all agent generation loops.

## 🛠️ How to Deploy to Your Own Free Hugging Face Space
1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/new-space).
2. Choose **Docker** as the Space SDK and name it `agent-development-factory`.
3. Push this repository to your Hugging Face Space git remote:
   ```bash
   git remote add hf https://huggingface.co/spaces/<your-username>/agent-development-factory
   git push hf main
   ```
4. Hugging Face automatically builds the `Dockerfile` and presents your live public web application!
