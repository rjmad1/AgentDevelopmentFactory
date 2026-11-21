# Agent Development Factory — Production Deployment on Free Utilities

This guide explains how the **Agent Development Factory (ADF)** is deployed and operated across **100% free utilities**, maintaining the foundational **$0.00 spend ceiling invariant** without incurring hosting, API, or infrastructure fees.

---

## 1. Overview of Free Utility Deployment Topology

| Utility / Platform | Role / Component | Free Tier Capabilities | Cost |
| :--- | :--- | :--- | :---: |
| **GitHub Container Registry (GHCR)** | Multi-runtime container image distribution | Unlimited public container storage & bandwidth | **$0.00** |
| **GitHub Pages** | Live MkDocs technical documentation | Unlimited static web hosting | **$0.00** |
| **GitHub Wiki** | Architecture specs, runbooks & role diagrams | Free integrated Git-backed wiki | **$0.00** |
| **Hugging Face Spaces** | Cloud Web API & Material Design UI | 2 vCPU, 16GB RAM, Free persistent storage, HTTPS domain | **$0.00** |
| **Render / Koyeb** | Cloud Web Service (auto-deploy via `render.yaml`) | Free tier container hosting with auto-git trigger | **$0.00** |
| **Docker Compose** | Local / Self-Hosted Scaling Cluster | Runs ADF server + 4 worker replicas + Jaeger + Prometheus | **$0.00** |
| **Kubernetes (Minikube / K3s)** | Cloud-native pod auto-scaling (HPA v2) | 2 to 16 dynamically scaling pods via `deploy/k8s/hpa.yaml` | **$0.00** |

---

## 2. GitHub Container Registry (GHCR) Publishing

The repository includes an autonomous GitHub Actions workflow at `.github/workflows/docker-publish.yml`.
Whenever code is committed to `main` impacting the `Dockerfile`, `src/`, `agent_factory/`, or dependencies:
1. Docker Buildx compiles the multi-runtime container image (Python 3.11 + Node.js 20).
2. The image is tagged and published to:
   ```bash
   docker pull ghcr.io/rjmad1/agent-development-factory:latest
   ```
3. The image executes under unprivileged non-root user `UID 10001` and enforces `ADF_SPEND_CEILING_USD=0.00`.

---

## 3. Free Cloud Deployment on Hugging Face Spaces (Docker Tier)

Hugging Face Spaces provides 16GB RAM and 2 vCPUs at zero cost.

### How to Deploy in 3 Steps:
1. Navigate to **[huggingface.co/new-space](https://huggingface.co/new-space)**.
2. Select **Docker** as the Space SDK and enter `agent-development-factory` as the Space name.
3. Push this repository to your Hugging Face Space:
   ```bash
   git remote add hf https://huggingface.co/spaces/<your-username>/agent-development-factory
   git push hf main
   ```
4. Hugging Face reads `deploy/hf-space/README.md` and `Dockerfile`, starts the container on port `3000`, and provides a public HTTPS web address.

---

## 4. Free Cloud Deployment on Render.com

The repository root includes a declarative [render.yaml](../../render.yaml).

### How to Deploy on Render:
1. Sign up at [render.com](https://render.com) (Free Tier).
2. Click **New +** $\to$ **Blueprint**.
3. Connect `https://github.com/rjmad1/AgentDevelopmentFactory`.
4. Render automatically parses `render.yaml`, provisions the free Docker web service, wires health checks to `/healthz`, and deploys your live API and Material UI.

---

## 5. Local Enterprise Cluster Deployment (Docker Compose)

For local development or private self-hosted servers, ADF provides a complete multi-container scaling topology:
- **ADF Control Plane & Material UI:** `http://localhost:3000`
- **Background Worker Daemon:** Port `8000`
- **Distributed Tracing (Jaeger UI):** `http://localhost:16686`
- **Prometheus Telemetry Scraper:** `http://localhost:9090`

### One-Click Launch:
* **Windows (PowerShell):**
  ```powershell
  .\scripts\deploy-local.ps1
  ```
* **Linux / macOS (Bash):**
  ```bash
  ./scripts/deploy-local.sh
  ```

### Cluster Teardown:
```powershell
.\scripts\deploy-local.ps1 -Down
```

---

## 6. Local Kubernetes HPA v2 Auto-Scaling Deployment

To deploy on a local Kubernetes cluster (Minikube, Kind, Docker Desktop K8s, or K3s):

### One-Click Launch:
* **Windows (PowerShell):**
  ```powershell
  .\scripts\deploy-k8s.ps1
  ```
* **Linux / macOS (Bash):**
  ```bash
  ./scripts/deploy-k8s.sh
  ```

This provisions the `adf-runtime` namespace, starts the worker deployment with liveness and readiness probes, and activates the Horizontal Pod Autoscaler (`HPA v2`) to dynamically govern worker replicas between 2 and 16 pods based on queue depth and CPU pressure.

---

## 7. Secure Remote Accessibility & Zero-Trust Cloudflare Tunneling

When the Agent Development Factory is deployed for remote access across the public internet, enterprise-grade safety, encryption, and authorization are strictly enforced.

### 7.1 Architecture: Zero-Trust HTTPS Edge Tunnel
Rather than opening insecure firewall ports or configuring dynamic DNS, the factory utilizes **Cloudflare Quick Tunnels** via the official `cloudflare/cloudflared` utility:
* **Zero Firewall Configuration:** The tunnel initiates an outbound-only connection to Cloudflare's nearest edge server.
* **Full TLS Termination:** Cloudflare manages edge certificates and automatically serves your application over `https://<tunnel-id>.trycloudflare.com`.
* **Zero Operational Cost:** 100% free utility with no domain registration, credit card, or subscription required.

### 7.2 Defense-in-Depth Remote Security Gate
1. **Cryptographic Token Authorization:** Every non-public API endpoint strictly verifies the `ADF_ACCESS_TOKEN` using constant-time comparison (`crypto.timingSafeEqual`) to prevent timing attacks.
   - Supported via `Authorization: Bearer <token>`
   - Supported via header `X-ADF-Access-Token: <token>`
   - Supported via URL parameter `?token=<token>`
2. **Anti-DDoS Rate Limiting:** An in-memory sliding-window governor enforces a strict limit of 120 requests/minute per client IP to safeguard free resources from abusive traffic.
3. **Enterprise Security Headers:** All responses include `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and strict origin referrer policies.
4. **SRE Probe Isolation:** Public health and metrics endpoints (`/healthz`, `/readyz`, `/metrics`) remain accessible to Prometheus scrapers while mutating actions remain guarded.

### 7.3 One-Click Secure Remote Launch
* **Windows (PowerShell):**
  ```powershell
  .\scripts\deploy-remote.ps1
  ```
* **Linux / macOS (Bash):**
  ```bash
  ./scripts/deploy-remote.sh
  ```

The deployment script automatically:
1. Generates a cryptographically strong 32-byte session token (if not already set via `ADF_ACCESS_TOKEN`).
2. Boots the container cluster with the `adf-tunnel` profile active.
3. Discovers the live public Cloudflare HTTPS URL from the tunnel handshake.
4. Prints the pre-authenticated remote URL:
   ```
   🌐 Public HTTPS Domain:   https://xxxxxxxx-xxxx.trycloudflare.com
   🔑 Authenticated Web UI:  https://xxxxxxxx-xxxx.trycloudflare.com/?token=<token>
   🛡️ Security Access Token: <token>
   ```

### 7.4 Tearing Down Remote Accessibility
```powershell
.\scripts\deploy-remote.ps1 -Down
```

