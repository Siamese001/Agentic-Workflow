#requires -RunAsAdministrator
# VHDX compaction using diskpart (works without Hyper-V module).
# Steps: fstrim inside WSL -> stop Docker Desktop -> wsl --shutdown -> diskpart compact -> restart Docker
# Writes artifacts\vhdx_optimize.done with results.

param(
    [string]$VhdxPath = $env:WSL_VHDX_PATH
)

$ErrorActionPreference = 'Stop'
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$logPath    = Join-Path $repoRoot "artifacts\vhdx_optimize.log"
$markerDone = Join-Path $repoRoot "artifacts\vhdx_optimize.done"
New-Item -ItemType Directory -Path (Split-Path $logPath) -Force | Out-Null
Remove-Item $markerDone -ErrorAction SilentlyContinue

Start-Transcript -Path $logPath -Force -Append | Out-Null

try {
    Write-Host ""
    Write-Host "=== VHDX Diskpart-Compact Run $(Get-Date) ===" -ForegroundColor Cyan

    $IsElevated = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $IsElevated) { throw "Must run as Administrator." }

    $Vhdx = $VhdxPath
    if ([string]::IsNullOrWhiteSpace($Vhdx)) {
        throw "Pass -VhdxPath or set WSL_VHDX_PATH to the ext4.vhdx path for the distro being compacted."
    }
    if (-not (Test-Path $Vhdx)) { throw "VHDX not found at $Vhdx" }

    $BeforeBytes = (Get-Item $Vhdx).Length
    $BeforeGB = [math]::Round($BeforeBytes / 1GB, 2)
    Write-Host "[1/5] VHDX before: $BeforeGB GB" -ForegroundColor Green
    Write-Host "    Path: $Vhdx"

    Write-Host "[2/5] Running fstrim inside WSL as root to zero free blocks..." -ForegroundColor Cyan
    wsl -d Ubuntu-24.04 -u root -- fstrim -v /
    Start-Sleep -Seconds 3

    Write-Host "[3/5] Stopping Docker Desktop (it holds a WSL VHDX lock)..." -ForegroundColor Cyan
    $dockerProcs = @('Docker Desktop', 'com.docker.backend', 'com.docker.proxy', 'dockerd', 'docker')
    foreach ($p in $dockerProcs) {
        Stop-Process -Name $p -Force -ErrorAction SilentlyContinue
    }
    wsl -t docker-desktop 2>$null
    Start-Sleep -Seconds 10

    Write-Host "[4/5] Shutting down all WSL distros..." -ForegroundColor Cyan
    wsl --shutdown
    Start-Sleep -Seconds 15

    Write-Host "[5/5] Running diskpart compact vdisk (1-4 min)..." -ForegroundColor Cyan
    $dpScript = "select vdisk file=`"$Vhdx`"`r`nattach vdisk readonly`r`ncompact vdisk`r`ndetach vdisk`r`nexit`r`n"
    $dpFile = [System.IO.Path]::GetTempFileName() + ".txt"
    [System.IO.File]::WriteAllText($dpFile, $dpScript, [System.Text.Encoding]::ASCII)

    $t0 = Get-Date
    $dpOutput = diskpart /s $dpFile 2>&1
    $t1 = Get-Date
    $duration = [math]::Round(($t1 - $t0).TotalSeconds, 1)

    Write-Host "--- diskpart output ---" -ForegroundColor Gray
    $dpOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    Write-Host "--- end diskpart output ---" -ForegroundColor Gray

    Remove-Item $dpFile -ErrorAction SilentlyContinue
    Write-Host "    diskpart finished in ${duration}s" -ForegroundColor Green

    $AfterBytes = (Get-Item $Vhdx).Length
    $AfterGB = [math]::Round($AfterBytes / 1GB, 2)
    $ReclaimedGB = [math]::Round(($BeforeBytes - $AfterBytes) / 1GB, 2)

    Write-Host ""
    Write-Host "=== RESULT ===" -ForegroundColor Cyan
    Write-Host "    Before:    $BeforeGB GB" -ForegroundColor White
    Write-Host "    After:     $AfterGB GB" -ForegroundColor White
    Write-Host "    Reclaimed: $ReclaimedGB GB" -ForegroundColor Green

    "DONE BeforeGB=$BeforeGB AfterGB=$AfterGB ReclaimedGB=$ReclaimedGB DurationSec=$duration" |
        Out-File $markerDone -Encoding ascii

    Write-Host ""
    Write-Host "Restarting Docker Desktop..." -ForegroundColor Cyan
    $dockerExe = @(
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($dockerExe) {
        Start-Process $dockerExe
        Write-Host "    Docker Desktop relaunched." -ForegroundColor Green
    } else {
        Write-Host "    Docker Desktop exe not found - start manually if needed." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "After Docker settles (~30s), restart canonical Docker vLLM:" -ForegroundColor Yellow
    Write-Host "    wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH && bash ops_scripts/apps_rg/boot_local_qwen_vllm.sh'" -ForegroundColor Yellow

} catch {
    Write-Error $_
    "FAILED: $_" | Out-File $markerDone -Encoding ascii
} finally {
    Stop-Transcript | Out-Null
}
