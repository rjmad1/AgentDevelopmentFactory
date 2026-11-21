# ==============================================================================
# Agent Development Factory (ADF) - Production Container Image
# Multi-runtime: Node.js 20 + Python 3.11
# Security: Non-root user (10001), Read-only Root FS Compatible, Zero Spend Ceiling
# ==============================================================================

FROM python:3.11-slim AS base

# Install Node.js 20 & curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Set up non-root user (matching deploy/k8s/hpa.yaml: runAsUser 10001)
RUN groupadd -g 10001 adf && \
    useradd -u 10001 -g adf -m -s /bin/bash adf

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and grant appropriate ownership
COPY . .
RUN chown -R adf:adf /app

# Switch to non-root user
USER 10001

# Default environment configuration
ENV NODE_ENV=production \
    ADF_ENV=production \
    ADF_PORT=3000 \
    ADF_WORKER_PORT=8000 \
    ADF_SPEND_CEILING_USD=0.00 \
    PYTHONPATH=/app

# Expose HTTP control plane (3000) and worker probe (8000)
EXPOSE 3000 8000

# Container liveness probe
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/healthz', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Default to running the control plane HTTP API & UI server
CMD ["node", "src/server.js"]
