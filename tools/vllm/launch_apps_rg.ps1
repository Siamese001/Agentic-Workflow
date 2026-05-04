#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Launch apps_rg with automatic vLLM health check and startup.

.DESCRIPTION
    Ensures WSL is running, vLLM is healthy, starts vLLM if needed,
    waits for ready state, then runs apps_rg with provided arguments.

.EXAMPLE
    .\tools\vllm\launch_apps_rg.ps1 --target-role "Senior ML Engineer" --target-company "Google"

.EXAMPLE
    # Interactive mode (prompts for inputs)
    .\tools\vllm\launch_apps_rg.ps1
#>

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$AppArgs
)

$ErrorActionPreference = "Stop"
$VLLM_URL = "http://localhost:8000/v1/models"
$VLLM_HEALTH_TIMEOUT_SEC = 300  # 5 minutes max wait for vLLM cold start
$HEALTH_CHECK_INTERVAL_SEC = 5

function Write-Status { param([string]$msg) Write-Host "[launch_apps_rg] $msg" -ForegroundColor Cyan }
function Write-Error { param([string]$msg) Write-Host "[launch_apps_rg] $msg" -ForegroundColor Red }
function Write-Success { param([string]$msg) Write-Host "[launch_apps_rg] $msg" -ForegroundColor Green }

# -----------------------------------------------------------------------------
# 1. Ensure WSL is running
# -----------------------------------------------------------------------------
Write-Status "Checking WSL status..."
try {
    $wslStatus = wsl.exe --status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "WSL not available"
    }
} catch {
    Write-Status "Starting WSL..."
    wsl.exe --exec true
    Start-Sleep -Seconds 3
}

# -----------------------------------------------------------------------------
# 2. Check if vLLM is healthy
# -----------------------------------------------------------------------------
function Test-VllmHealth {
    try {
        $response = Invoke-RestMethod -Uri $VLLM_URL -Method GET -TimeoutSec 3 -ErrorAction Stop
        return $response.data.Count -gt 0
    } catch {
        return $false
    }
}

Write-Status "Checking vLLM health at $VLLM_URL..."
$isHealthy = Test-VllmHealth

if (-not $isHealthy) {
    Write-Status "vLLM not responding. Checking if service is running in WSL..."

    # Check if vllm service is active
    $serviceStatus = wsl.exe bash -c "systemctl --user is-active vllm.service 2>/dev/null || echo 'inactive'"

    if ($serviceStatus -eq "inactive" -or $serviceStatus -eq "failed" -or $serviceStatus -eq "unknown") {
        Write-Status "Starting vLLM systemd service..."
        wsl.exe bash -c "systemctl --user daemon-reload && systemctl --user start vllm.service"
    } else {
        Write-Status "Service reports: $serviceStatus"
    }

    # Wait for vLLM to be ready
    Write-Status "Waiting for vLLM to be healthy (timeout: ${VLLM_HEALTH_TIMEOUT_SEC}s)..."
    $elapsed = 0
    $ready = $false

    while ($elapsed -lt $VLLM_HEALTH_TIMEOUT_SEC) {
        Start-Sleep -Seconds $HEALTH_CHECK_INTERVAL_SEC
        $elapsed += $HEALTH_CHECK_INTERVAL_SEC

        $ready = Test-VllmHealth
        if ($ready) {
            break
        }

        # Show progress every 10 seconds
        if ($elapsed % 10 -eq 0) {
            Write-Status "Still waiting... ($elapsed s elapsed)"
            # Check service logs for debugging
            $logs = wsl.exe bash -c "journalctl --user -u vllm.service --since '10 seconds ago' --no-pager 2>/dev/null | tail -3"
            if ($logs) {
                Write-Status "Recent logs: $logs"
            }
        }
    }

    if (-not $ready) {
        Write-Error "vLLM failed to become healthy within ${VLLM_HEALTH_TIMEOUT_SEC} seconds"
        Write-Error "Check logs: wsl.exe journalctl --user -u vllm.service -f"
        exit 1
    }

    Write-Success "vLLM is healthy and ready!"
} else {
    Write-Success "vLLM already healthy"
}

# -----------------------------------------------------------------------------
# 3. Run apps_rg
# -----------------------------------------------------------------------------
Write-Status "Launching apps_rg with args: $AppArgs"

# Change to repo root and run
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location $repoRoot

try {
    $pythonCmd = "python"
    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
        $pythonCmd = "uv run python"
    }

    # Build the command
    $cmd = "$pythonCmd -m apps_rg"
    if ($AppArgs.Count -gt 0) {
        $cmd += " " + ($AppArgs -join " ")
    }

    Write-Status "Executing: $cmd"
    Invoke-Expression $cmd

    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Error "apps_rg exited with code $exitCode"
        exit $exitCode
    }

    Write-Success "apps_rg completed successfully"
} finally {
    Pop-Location
}
