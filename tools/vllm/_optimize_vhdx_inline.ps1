#requires -RunAsAdministrator
# Inline single-shot VHDX optimize: wsl --shutdown -> wait -> Optimize-VHD.
# Self-contained, no separate verify-unlock loop, no script waits.
# All output to artifacts/vhdx_optimize.log AND a marker file.

$ErrorActionPreference = 'Stop'
$logPath = "C:\Git\Agentic-Workflow\artifacts\vhdx_optimize.log"
$markerDone = "C:\Git\Agentic-Workflow\artifacts\vhdx_optimize.done"
New-Item -ItemType Directory -Path (Split-Path $logPath) -Force | Out-Null
Remove-Item $markerDone -ErrorAction SilentlyContinue

Start-Transcript -Path $logPath -Force | Out-Null

try {
    Write-Host "=== VHDX Optimize Run $(Get-Date) ===" -ForegroundColor Cyan

    # Verify elevation
    $IsElevated = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $IsElevated) { throw "Must run as Administrator." }

    $Vhdx = "C:\Users\amita\AppData\Local\wsl\{358ed4de-0575-4f25-973c-dacd8fec83c2}\ext4.vhdx"
    if (-not (Test-Path $Vhdx)) { throw "VHDX not found at $Vhdx" }

    $BeforeBytes = (Get-Item $Vhdx).Length
    $BeforeGB = [math]::Round($BeforeBytes / 1GB, 2)
    Write-Host "[1/4] VHDX before: $BeforeGB GB ($Vhdx)" -ForegroundColor Green

    Write-Host "[2/4] Shutting down WSL..." -ForegroundColor Cyan
    wsl --shutdown
    Start-Sleep -Seconds 12

    Write-Host "[3/4] Running Optimize-VHD -Mode Full (1-3 min, no progress bar)..." -ForegroundColor Cyan
    $t0 = Get-Date
    Optimize-VHD -Path $Vhdx -Mode Full
    $t1 = Get-Date
    $duration = ($t1 - $t0).TotalSeconds
    Write-Host "    Optimize-VHD finished in $([math]::Round($duration, 1))s" -ForegroundColor Green

    $AfterBytes = (Get-Item $Vhdx).Length
    $AfterGB = [math]::Round($AfterBytes / 1GB, 2)
    $ReclaimedGB = [math]::Round(($BeforeBytes - $AfterBytes) / 1GB, 2)

    Write-Host ""
    Write-Host "[4/4] RESULT" -ForegroundColor Cyan
    Write-Host "    Before:    $BeforeGB GB" -ForegroundColor White
    Write-Host "    After:     $AfterGB GB" -ForegroundColor White
    Write-Host "    Reclaimed: $ReclaimedGB GB" -ForegroundColor Green

    "DONE BeforeGB=$BeforeGB AfterGB=$AfterGB ReclaimedGB=$ReclaimedGB DurationSec=$duration" |
        Out-File $markerDone -Encoding ascii
} catch {
    Write-Error $_
    "FAILED: $_" | Out-File $markerDone -Encoding ascii
} finally {
    Stop-Transcript | Out-Null
}
