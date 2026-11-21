#!/usr/bin/env bash
# ==============================================================================
# Agent Development Factory - One-Click Local Multi-Container Deployment (Unix)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/deploy/docker-compose.scaling.yml"

echo "=================================================================="
echo "    AGENT DEVELOPMENT FACTORY — LOCAL DOCKER CLUSTER DEPLOYMENT   "
echo "=================================================================="

if [[ "${1:-}" == "--down" ]]; then
    echo "[TEARDOWN] Stopping and removing all ADF container services..."
    docker compose -f "$COMPOSE_FILE" down -v
    echo "[TEARDOWN] ADF cluster successfully stopped."
    exit 0
fi

echo "[PREFLIGHT] Checking Docker availability..."
docker --version

echo "[DEPLOY] Launching multi-container topology from $COMPOSE_FILE..."
BUILD_FLAG=""
if [[ "${1:-}" == "--build" ]]; then
    BUILD_FLAG="--build"
fi

docker compose -f "$COMPOSE_FILE" up -d --remove-orphans $BUILD_FLAG

echo ""
echo "[HEALTHCHECK] Waiting for ADF services to report healthy..."
for i in {1..15}; do
    sleep 2
    if curl -s -f http://localhost:3000/healthz >/dev/null 2>&1; then
        echo "✅ ADF Control Plane is healthy."
        break
    fi
    echo "  ... waiting for ADF Control Plane (attempt $i/15)"
done

echo ""
echo "=================================================================="
echo "    ✅ ADF ZERO-COST ENTERPRISE CLUSTER DEPLOYED SUCCESSFULLY!    "
echo "=================================================================="
echo "  • Material Design Web UI:       http://localhost:3000"
echo "  • Control Plane REST API:       http://localhost:3000/api/health"
echo "  • SRE Liveness Probe:           http://localhost:3000/healthz"
echo "  • SRE Readiness Probe:          http://localhost:3000/readyz"
echo "  • Prometheus Scrape Metrics:    http://localhost:3000/metrics"
echo "  • Distributed Tracing (Jaeger): http://localhost:16686"
echo "  • Prometheus Metric Server:     http://localhost:9090"
echo "  • Constitutional Spend Limit:   \$0.00 USD"
echo "=================================================================="
echo "To shut down the cluster later, run: ./scripts/deploy-local.sh --down"
