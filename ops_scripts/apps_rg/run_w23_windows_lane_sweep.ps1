# W2/W3 fresh canonical lane proof sweep (Windows; requires local vLLM + BGE snapshot).
# RCA-2: modular sections root + upstream-first lane order for companion chain.
$ErrorActionPreference = "Continue"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
Set-Location $Repo
$LogDir = Join-Path $Repo "artifacts/apps_rg/plans/w23_lane_sweep"
$ModularRoot = Join-Path $Repo "artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $ModularRoot | Out-Null

$env:APPS_RG_MODULAR_R4_SECTIONS_ROOT = "artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes"
$env:APPS_RG_WHOLE_RUN_ENVELOPE = "1"

python -c @"
from pathlib import Path
from apps_rg.runtime.sections_root_manifest import emit_sections_root_manifest
repo = Path(r'$Repo')
root = repo / 'artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes'
emit_sections_root_manifest(
    repo_root=repo,
    sections_root_abs=root,
    source_env_literal='APPS_RG_MODULAR_R4_SECTIONS_ROOT',
    correlation_id='w23_lane_sweep',
    notes='W23 Windows per-lane sweep modular companion chain',
)
"@

$Jd = "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
$Brief = "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
$BriefExec = "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md"
$Common = @(
    "--target-company", "Brown & Brown",
    "--target-role", "SVP IT Strategy & Innovation",
    "--jd", $Jd,
    "--provider", "qwen_vllm",
    "--allow-non-allow-exit-zero"
)
# Upstream bullets before narrative companions; IBM bullets before IBM narrative.
$Lanes = @(
    @{ section = "unify_bullets"; brief = $Brief },
    @{ section = "unify_narrative"; brief = $Brief },
    @{ section = "headline"; brief = $Brief },
    @{ section = "competencies"; brief = $Brief },
    @{ section = "executive_summary"; brief = $BriefExec },
    @{ section = "ibm_bullets"; brief = $Brief },
    @{ section = "ibm_narrative"; brief = $Brief }
)
$Manifest = @{
    modular_sections_root = $env:APPS_RG_MODULAR_R4_SECTIONS_ROOT
    whole_run_envelope = $env:APPS_RG_WHOLE_RUN_ENVELOPE
    lanes = @()
}
foreach ($lane in $Lanes) {
    $sec = $lane.section
    $log = Join-Path $LogDir "$sec.log"
    Write-Host "=== $sec ==="
    & python -m apps_rg --section $sec @Common --manual-brief $lane.brief 2>&1 | Tee-Object -FilePath $log
    $rc = $LASTEXITCODE
    $Manifest.lanes += @{ section = $sec; exit_code = $rc; log = $log }
}
$Manifest | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $LogDir "w23_lane_sweep_manifest.json") -Encoding UTF8
python ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py | Tee-Object (Join-Path $LogDir "audit.log")
