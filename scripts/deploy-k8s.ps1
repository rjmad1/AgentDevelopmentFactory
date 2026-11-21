# ==============================================================================
# Agent Development Factory - One-Click Kubernetes HPA v2 Deployment
# Deploys ADF Runtime Namespace, Worker Deployments, and Autoscaler (HPA v2)
# ==============================================================================

param (
    [switch]$Delete
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$HpaManifest = Join-Path $ProjectRoot "deploy\k8s\hpa.yaml"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "    AGENT DEVELOPMENT FACTORY — KUBERNETES AUTOSCALER DEPLOYMENT  " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

Write-Host "[PREFLIGHT] Checking kubectl connectivity..." -ForegroundColor Cyan
try {
    $context = kubectl config current-context
    Write-Host "[PASS] Connected to Kubernetes context: $context" -ForegroundColor Green
} catch {
    Write-Error "[FAIL] Unable to connect to Kubernetes cluster via kubectl."
}

if ($Delete) {
    Write-Host "[TEARDOWN] Deleting ADF Kubernetes resources..." -ForegroundColor Yellow
    kubectl delete -f $HpaManifest --ignore-not-found=true
    kubectl delete namespace adf-runtime --ignore-not-found=true
    Write-Host "[TEARDOWN] ADF Kubernetes deployment removed." -ForegroundColor Green
    exit 0
}

Write-Host "[NAMESPACE] Ensuring 'adf-runtime' namespace exists..." -ForegroundColor Cyan
kubectl create namespace adf-runtime --dry-run=client -o yaml | kubectl apply -f -

Write-Host "[DEPLOY] Applying declarative manifests from $HpaManifest..." -ForegroundColor Cyan
kubectl apply -f $HpaManifest

Write-Host "`n[STATUS] Inspecting ADF Deployment & HPA status..." -ForegroundColor Cyan
kubectl get deployment -n adf-runtime
kubectl get hpa -n adf-runtime

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "    ✅ ADF KUBERNETES AUTOSCALING RUNTIME DEPLOYED!               " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "To monitor pods in real time: kubectl get pods -n adf-runtime -w"
Write-Host "To tear down deployment: .\scripts\deploy-k8s.ps1 -Delete`n"
