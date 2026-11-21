# ==============================================================================
# Agent Development Factory - One-Click Local Multi-Container Deployment
# Deploys ADF Server, Autoscaling Worker Pool, Jaeger, and Prometheus on Docker
# ==============================================================================

param (
    [switch]$Down,
    [switch]$Build
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectRoot "deploy\docker-compose.scaling.yml"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "    AGENT DEVELOPMENT FACTORY — LOCAL DOCKER CLUSTER DEPLOYMENT   " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

if ($Down) {
    Write-Host "[TEARDOWN] Stopping and removing all ADF container services..." -ForegroundColor Yellow
    docker compose -f $ComposeFile down -v
    Write-Host "[TEARDOWN] ADF cluster successfully stopped." -ForegroundColor Green
    exit 0
}

Write-Host "[PREFLIGHT] Checking Docker availability..." -ForegroundColor Cyan
try {
    $dockerVer = docker --version
    Write-Host "[PASS] Docker detected: $dockerVer" -ForegroundColor Green
} catch {
    Write-Error "[FAIL] Docker daemon is not running or not installed."
}

$buildArgs = if ($Build) { "--build" } else { "" }
Write-Host "[DEPLOY] Launching multi-container topology from $ComposeFile..." -ForegroundColor Cyan

docker compose -f $ComposeFile up -d --remove-orphans $buildArgs

Write-Host "`n[HEALTHCHECK] Waiting for ADF services to become healthy..." -ForegroundColor Cyan
$maxAttempts = 15
$attempt = 0
$serverHealthy = $false

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    $attempt++
    try {
        $resp = Invoke-RestMethod -Uri "http://localhost:3000/healthz" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($resp.status -eq "healthy") {
            $serverHealthy = $true
            break
        }
    } catch {
        Write-Host "  ... waiting for ADF Control Plane (attempt $attempt/$maxAttempts)"
    }
}

if (-not $serverHealthy) {
    Write-Error "[FAIL] ADF Control Plane failed to report healthy within 30 seconds."
}

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "    ✅ ADF ZERO-COST ENTERPRISE CLUSTER DEPLOYED SUCCESSFULLY!    " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  • Material Design Web UI:     http://localhost:3000"
Write-Host "  • Control Plane REST API:     http://localhost:3000/api/health"
Write-Host "  • SRE Liveness Probe:         http://localhost:3000/healthz"
Write-Host "  • SRE Readiness Probe:        http://localhost:3000/readyz"
Write-Host "  • Prometheus Scrape Metrics:  http://localhost:3000/metrics"
Write-Host "  • Distributed Tracing (Jaeger): http://localhost:16686"
Write-Host "  • Prometheus Metric Server:   http://localhost:9090"
Write-Host "  • Constitutional Spend Limit: $0.00 USD"
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "To shut down the cluster later, run: .\scripts\deploy-local.ps1 -Down`n"
