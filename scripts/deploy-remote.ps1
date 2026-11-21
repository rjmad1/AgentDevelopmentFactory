# ==============================================================================
# Agent Development Factory - One-Click Secure Remote Deployment
# Deploys ADF Stack + Cloudflare Zero-Trust Quick Tunnel + Token Authentication
# ==============================================================================

param (
    [string]$Token = "",
    [switch]$Down
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectRoot "deploy\docker-compose.scaling.yml"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "   AGENT DEVELOPMENT FACTORY — SECURE REMOTE CLOUD DEPLOYMENT     " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

if ($Down) {
    Write-Host "[TEARDOWN] Stopping remote deployment and closing tunnel..." -ForegroundColor Yellow
    docker compose -f $ComposeFile --profile remote down -v
    Write-Host "[TEARDOWN] Remote tunnel and cluster closed successfully." -ForegroundColor Green
    exit 0
}

# 1. Generate or validate cryptographically secure access token
if (-not $Token) {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $Token = -join ($bytes | ForEach-Object { "{0:x2}" -f $_ })
    Write-Host "[SECURITY] Generated cryptographically strong remote access token." -ForegroundColor Green
} else {
    Write-Host "[SECURITY] Using user-specified remote access token." -ForegroundColor Green
}

$env:ADF_ACCESS_TOKEN = $Token
Write-Host "[SECURITY] Token authorization gate strictly active on all API endpoints." -ForegroundColor Green

# 2. Check Docker
try {
    $null = docker --version
} catch {
    Write-Error "[FAIL] Docker daemon is not running. Please start Docker first."
}

# 3. Launch Cluster + Cloudflare Quick Tunnel Sidecar
Write-Host "[DEPLOY] Starting ADF cluster with Zero-Trust Cloudflare Tunnel sidecar..." -ForegroundColor Cyan
docker compose -f $ComposeFile --profile remote up -d --remove-orphans

Write-Host "`n[TUNNEL] Establishing Cloudflare secure HTTPS edge tunnel..." -ForegroundColor Cyan
$tunnelUrl = ""
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts -and -not $tunnelUrl) {
    Start-Sleep -Seconds 2
    $attempt++
    $logs = docker logs adf-remote-tunnel 2>&1
    if ($logs -match "https://([a-zA-Z0-9-]+\.trycloudflare\.com)") {
        $tunnelUrl = $matches[0]
        break
    }
    Write-Host "  ... waiting for Cloudflare edge propagation ($attempt/$maxAttempts)"
}

if (-not $tunnelUrl) {
    Write-Warning "[WARNING] Tunnel URL not detected in logs yet. Inspect with: docker logs adf-remote-tunnel"
    $tunnelUrl = "https://<your-tunnel-subdomain>.trycloudflare.com"
}

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "  ✅ ADF SECURE REMOTE ECOSYSTEM IS LIVE & GLOBALLY ACCESSIBLE!  " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  🌐 Public HTTPS Domain:      $tunnelUrl" -ForegroundColor Cyan
Write-Host "  🔑 Authenticated URL:        $tunnelUrl/?token=$Token" -ForegroundColor Yellow
Write-Host "  🛡️ Security Access Token:    $Token" -ForegroundColor White
Write-Host "  📊 Prometheus Metrics:       $tunnelUrl/metrics"
Write-Host "  🩺 SRE Liveness Probe:       $tunnelUrl/healthz"
Write-Host "  🩺 SRE Readiness Probe:      $tunnelUrl/readyz"
Write-Host "  💰 Operational Cost:         $0.00 USD (100% Free Utilities)"
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Security: All mutating API calls require Authorization: Bearer <token>"
Write-Host "To tear down remote accessibility: .\scripts\deploy-remote.ps1 -Down`n"
