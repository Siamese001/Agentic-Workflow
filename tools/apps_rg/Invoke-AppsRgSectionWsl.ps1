# Run python -m apps_rg via WSL (bypasses Windows Smart App Control blocking torch .pyd).
# Usage:
#   .\tools\apps_rg\Invoke-AppsRgSectionWsl.ps1 --section executive_summary --target-company "Acme" ...
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$AppArgs
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$RepoNorm = $RepoRoot -replace '\\', '/'
if ($RepoNorm -match '^([A-Za-z]):(.*)$') {
    $RepoWsl = "/mnt/$($Matches[1].ToLower())$($Matches[2])"
} else {
    $RepoWsl = $RepoNorm
}
$Bootstrap = "$RepoWsl/tools/apps_rg/wsl_bootstrap.sh"
$Runner = "$RepoWsl/tools/apps_rg/run_section_wsl.sh"

$venvOk = wsl -e bash -lc "test -x ~/.cache/awf-venv-wsl/bin/python"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Bootstrapping WSL venv (first run; may take several minutes)..." -ForegroundColor Yellow
    wsl -e bash -lc "sed -i 's/\r$//' '$Bootstrap' '$Runner' && bash '$Bootstrap'"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$argLine = ($AppArgs | ForEach-Object {
    if ($_ -match '[\s"'']') { "'$($_ -replace "'", "''")'" } else { $_ }
}) -join ' '

wsl -e bash -lc "sed -i 's/\r$//' '$Runner' && bash '$Runner' $argLine"
exit $LASTEXITCODE
