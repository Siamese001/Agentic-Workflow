# Fix apps_rg runtime on Windows: start vLLM + validate WSL venv (bypasses WDAC-blocked Windows Python).
# Usage: .\ops_scripts\apps_rg\Fix-AppsRgWslRuntime.ps1

$ErrorActionPreference = "Stop"
$Bge = "C:\Users\amita\.cache\huggingface\hub\models--BAAI--bge-m3\snapshots\5617a9f61b028005a4858fdac845db406aefb181"

Write-Host "== apps_rg runtime fix ==" -ForegroundColor Cyan

Write-Host "[1/3] Starting local-qwen-vllm..."
docker start local-qwen-vllm 2>$null | Out-Null
$deadline = (Get-Date).AddSeconds(90)
do {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/v1/models" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) { Write-Host "OK: vLLM /v1/models -> 200"; break }
    } catch { }
    if ((Get-Date) -gt $deadline) { throw "vLLM not ready on localhost:8000 after 90s" }
    Start-Sleep -Seconds 3
} while ($true)

if (-not (Test-Path $Bge)) { throw "BGE path missing: $Bge" }
Write-Host "OK: BGE model"

Write-Host "[2/3] WSL venv..."
wsl -e test -x /home/amita/.cache/awf-venv-wsl/bin/python
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating venv via uv sync (first run may take several minutes)..." -ForegroundColor Yellow
    wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH; export UV_CACHE_DIR=/tmp/uv-cache-wsl-isolated; export UV_PROJECT_ENVIRONMENT=$HOME/.cache/awf-venv-wsl; uv sync --python 3.12'
    if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }
}
Write-Host "OK: WSL venv"

Write-Host "[3/3] WSL import smoke test..."
wsl -e /home/amita/.cache/awf-venv-wsl/bin/python -c "import torch; print('OK', torch.__version__)"
if ($LASTEXITCODE -ne 0) { throw "WSL torch import failed" }

Write-Host ""
Write-Host "FIX COMPLETE." -ForegroundColor Green
Write-Host "Headline:  wsl bash /mnt/c/Git/Agentic-Workflow-FRESH/ops_scripts/apps_rg/run_headline_wsl.sh"
Write-Host "Exec sum:  wsl bash /mnt/c/Git/Agentic-Workflow-FRESH/ops_scripts/apps_rg/run_exec_summary_wsl.sh"
