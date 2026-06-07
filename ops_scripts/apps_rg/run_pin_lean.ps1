cd C:\Git\Agentic-Workflow-FRESH
$jd = "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt"
$brief = "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md"
$company = "AIG"
$role = "VP, Global Head of Agentic AI Solutions"
# Variance-class triage:
#   * Bullets sections (ibm/unify/competencies): MECHANICAL dominance after deterministic
#     guards — SC capped at 4 in section_reasoning_intensity.py. attempts=2 sufficient.
#   * Narratives: depend on upstream bullets canonical artifact — must run AFTER bullets.
#     Loop exits early on BLOCKED_UPSTREAM_NOT_FINALIZED so upstream-blocked sections
#     don't pay 4× preflight.
#   * executive_summary: 5 mechanical blockers all addressed by deterministic guards in
#     tree (orphan-row repair, sentence coercer, gate emission fix). attempts=2.
#   * headline: dominant blocker is UPSTREAM EVIDENCE MISSING (fact_engineering_platform_001
#     not in headline FEC). No number of retries fixes this — that's a data wave. Skipped.
# Order: bullets first (produce canonical artifact upstream lookup), then narratives.
$sections = @(
  @{name='ibm_bullets'; accept='review'},
  @{name='ibm_narrative'; accept='review'},
  @{name='unify_narrative'; accept='review'},
  @{name='executive_summary'; accept='review'}
)
$summary = @()
$ts = Get-Date -Format "HHmmss"
foreach ($entry in $sections) {
  $s = $entry.name
  $accept = $entry.accept
  Write-Host "==== SECTION $s (accept=$accept) ===="
  $started = Get-Date
  $logPath = "artifacts/apps_rg/_pinned/_assembled/lean_${ts}_${s}.log"
  python -m apps_rg --section $s --jd $jd --manual-brief $brief --provider qwen_vllm --target-company $company --target-role $role --attempts 2 --accept $accept --pin 2>&1 | Tee-Object -FilePath $logPath | Select-String -Pattern "PINNED|PIN_SKIPPED|attempt \d+/\d+|upstream_blocked" | ForEach-Object { Write-Host $_.Line }
  $rc = $LASTEXITCODE
  $elapsed = [int]((Get-Date) - $started).TotalSeconds
  $pinned = Test-Path "artifacts/apps_rg/_pinned/$s/x3_disposition.json"
  $summary += [PSCustomObject]@{Section=$s; rc=$rc; elapsed_s=$elapsed; pinned=$pinned}
  Write-Host "---- $s done rc=$rc elapsed=${elapsed}s pinned=$pinned ----"
}
$summary | Format-Table -AutoSize
$summary | ConvertTo-Json | Out-File "artifacts/apps_rg/_pinned/_assembled/lean_${ts}_summary.json"
Write-Host "==== ASSEMBLING ===="
python -m apps_rg --assemble-from-pinned 2>&1 | Select-String -Pattern "ASSEMBLED|ASSEMBLE_STATUS|assemble_status"
Write-Host "ASSEMBLE_RC=$LASTEXITCODE"
