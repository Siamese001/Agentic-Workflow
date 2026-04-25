#requires -RunAsAdministrator
# optimize_vhdx.ps1
# -----------------------------------------------------------------------------
# Reclaims free blocks from the WSL2 Ubuntu-24.04 ext4 VHDX after deleting
# large files inside WSL (e.g., the ~140 GB Stack B + duplicate model purge
# done on 2026-04-24).
#
# Why needed: WSL2's VHDX is a sparse file but only shrinks via Optimize-VHD.
# Stops Stack A vLLM mid-flight (wsl --shutdown is destructive to running
# processes); restart manually after this script returns.
#
# Usage (in an elevated PowerShell):
#   cd C:\Git\Agentic-Workflow
#   powershell -ExecutionPolicy Bypass -File tools\vllm\optimize_vhdx.ps1
# -----------------------------------------------------------------------------

[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# Verify elevation
$IsElevated = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsElevated) {
    Write-Error "Must run as Administrator. Right-click PowerShell -> Run as Administrator."
    exit 1
}

Write-Host "[1/5] Locating Ubuntu 24.04 VHDX..." -ForegroundColor Cyan
# Search known root locations recursively for ext4.vhdx, prefer the largest non-Docker one.
$Roots = @(
    "$env:LOCALAPPDATA\Packages",
    "$env:LOCALAPPDATA\wsl",
    "$env:USERPROFILE\AppData\Local\wsl"
) | Where-Object { Test-Path $_ }

$AllVhdx = @()
foreach ($root in $Roots) {
    $found = Get-ChildItem -Path $root -Recurse -Filter "ext4.vhdx" -ErrorAction SilentlyContinue -Force -Depth 6
    $AllVhdx += $found | Where-Object { $_.FullName -notmatch '\\Docker\\' }
}

if (-not $AllVhdx -or $AllVhdx.Count -eq 0) {
    Write-Error "Could not locate ext4.vhdx in: $($Roots -join '; ')"
    exit 1
}

# The active distro's VHDX is the largest one
$Vhdx = ($AllVhdx | Sort-Object Length -Descending | Select-Object -First 1).FullName
Write-Host "    Candidates considered:" -ForegroundColor Gray
foreach ($v in $AllVhdx) {
    $sizeGB = [math]::Round($v.Length / 1GB, 2)
    Write-Host "      $sizeGB GB  $($v.FullName)" -ForegroundColor Gray
}
$BeforeBytes = (Get-Item $Vhdx).Length
$BeforeGB = [math]::Round($BeforeBytes / 1GB, 2)
Write-Host "    VHDX: $Vhdx" -ForegroundColor Green
Write-Host "    Size before: $BeforeGB GB" -ForegroundColor Green

if ($DryRun) {
    Write-Host "[DryRun] Would now: wsl --shutdown; Optimize-VHD -Path '$Vhdx' -Mode Full" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n[2/5] Stopping WSL (this kills Stack A vLLM if it's running)..." -ForegroundColor Cyan
wsl --shutdown
Start-Sleep -Seconds 5

Write-Host "`n[3/5] Verifying VHDX is unlocked..." -ForegroundColor Cyan
$WaitMax = 30
for ($i = 0; $i -lt $WaitMax; $i++) {
    try {
        $stream = [System.IO.File]::Open($Vhdx, 'Open', 'Read', 'None')
        $stream.Close()
        Write-Host "    VHDX unlocked after $i seconds" -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 1
    }
    if ($i -eq $WaitMax - 1) {
        Write-Error "VHDX still locked after $WaitMax seconds. Aborting."
        exit 1
    }
}

Write-Host "`n[4/5] Running Optimize-VHD -Mode Full (may take 1-3 minutes)..." -ForegroundColor Cyan
Optimize-VHD -Path $Vhdx -Mode Full
Write-Host "    Optimize-VHD complete" -ForegroundColor Green

$AfterBytes = (Get-Item $Vhdx).Length
$AfterGB = [math]::Round($AfterBytes / 1GB, 2)
$ReclaimedGB = [math]::Round(($BeforeBytes - $AfterBytes) / 1GB, 2)

Write-Host "`n[5/5] Result" -ForegroundColor Cyan
Write-Host "    Before:    $BeforeGB GB" -ForegroundColor White
Write-Host "    After:     $AfterGB GB" -ForegroundColor White
Write-Host "    Reclaimed: $ReclaimedGB GB" -ForegroundColor Green

Write-Host "`nNext steps (manual):" -ForegroundColor Yellow
Write-Host "  1. wsl                                    # boot the distro"
Write-Host "  2. systemctl --user start vllm            # restart Stack A"
Write-Host "  3. systemctl --user enable vllm           # (optional) auto-start at boot"
Write-Host "  4. curl http://localhost:8000/v1/models   # verify"
