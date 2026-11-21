#!/usr/bin/env bash
# ==============================================================================
# Agent Development Factory - One-Click Kubernetes HPA v2 Deployment (Unix)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HPA_MANIFEST="$PROJECT_ROOT/deploy/k8s/hpa.yaml"

echo "=================================================================="
echo "    AGENT DEVELOPMENT FACTORY — KUBERNETES AUTOSCALER DEPLOYMENT  "
echo "=================================================================="

echo "[PREFLIGHT] Checking kubectl connectivity..."
kubectl config current-context

if [[ "${1:-}" == "--delete" ]]; then
    echo "[TEARDOWN] Deleting ADF Kubernetes resources..."
    kubectl delete -f "$HPA_MANIFEST" --ignore-not-found=true
    kubectl delete namespace adf-runtime --ignore-not-found=true
    echo "[TEARDOWN] ADF Kubernetes deployment removed."
    exit 0
fi

echo "[NAMESPACE] Ensuring 'adf-runtime' namespace exists..."
kubectl create namespace adf-runtime --dry-run=client -o yaml | kubectl apply -f -

echo "[DEPLOY] Applying declarative manifests from $HPA_MANIFEST..."
kubectl apply -f "$HPA_MANIFEST"

echo ""
echo "[STATUS] Inspecting ADF Deployment & HPA status..."
kubectl get deployment -n adf-runtime
kubectl get hpa -n adf-runtime

echo ""
echo "=================================================================="
echo "    ✅ ADF KUBERNETES AUTOSCALING RUNTIME DEPLOYED!               "
echo "=================================================================="
echo "To monitor pods in real time: kubectl get pods -n adf-runtime -w"
echo "To tear down deployment: ./scripts/deploy-k8s.sh --delete"
