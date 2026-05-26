# Fix apps_rg runtime on Windows: boot Qwen vLLM (WSL compose) + validate WSL venv.
# Usage: .\ops_scripts\apps_rg\Fix-AppsRgWslRuntime.ps1
#
# Boot SSOT: docs/cursor/local_qwen_docker_boot.md

$ErrorActionPreference = "Stop"
$Bge = "C:\Users\amita\.cache\huggingface\hub\models--BAAI--bge-m3\snapshots\5617a9f61b028005a4858fdac845db406aefb181"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$BootScript = "/mnt/c/Git/Agentic-Workflow-FRESH/ops_scripts/apps_rg/boot_local_qwen_vllm.sh"
# Normalize repo path for WSL when not default clone location
$RepoWsl = ($RepoRoot -replace '\\', '/') -replace '^C:', '/mnt/c' -replace '^c:', '/mnt/c'
$BootScript = "$RepoWsl/ops_scripts/apps_rg/boot_local_qwen_vllm.sh"

Write-Host "== apps_rg runtime fix ==" -ForegroundColor Cyan

Write-Host "[1/3] Booting local-qwen-vllm (WSL compose + mount check)..."
wsl -e bash -lc "export REPO_ROOT='$RepoWsl'; bash '$BootScript'"
if ($LASTEXITCODE -ne 0) { throw "boot_local_qwen_vllm.sh failed — see docs/cursor/local_qwen_docker_boot.md" }

if (-not (Test-Path $Bge)) { throw "BGE path missing: $Bge" }
Write-Host "OK: BGE model"

Write-Host "[2/3] WSL venv..."
wsl -e test -x /home/amita/.cache/awf-venv-wsl/bin/python
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating venv via uv sync (first run may take several minutes)..." -ForegroundColor Yellow
    wsl -e bash -lc "cd '$RepoWsl'; export UV_CACHE_DIR=/tmp/uv-cache-wsl-isolated; export UV_PROJECT_ENVIRONMENT=`$HOME/.cache/awf-venv-wsl; uv sync --python 3.12"
    if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }
}
Write-Host "OK: WSL venv"

Write-Host "[3/3] WSL import smoke test..."
wsl -e /home/amita/.cache/awf-venv-wsl/bin/python -c "import torch; print('OK', torch.__version__)"
if ($LASTEXITCODE -ne 0) { throw "WSL torch import failed" }

Write-Host ""
Write-Host "FIX COMPLETE." -ForegroundColor Green
Write-Host "Headline:  wsl bash $RepoWsl/ops_scripts/apps_rg/run_headline_wsl.sh"
Write-Host "Exec sum:  wsl bash $RepoWsl/ops_scripts/apps_rg/run_exec_summary_wsl.sh"
