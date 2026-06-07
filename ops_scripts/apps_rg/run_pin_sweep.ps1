cd C:\Git\Agentic-Workflow-FRESH
$jd = "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt"
$brief = "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md"
$company = "AIG"
$role = "VP, Global Head of Agentic AI Solutions"
$sections = @('executive_summary','unify_bullets','unify_narrative','ibm_bullets','ibm_narrative','headline')
$summary = @()
foreach ($s in $sections) {
  Write-Host "==== SECTION $s ===="
  $started = Get-Date
  $logPath = "artifacts/apps_rg/_pinned/_assembled/sweep_${s}.log"
  $null = New-Item -ItemType Directory -Path (Split-Path $logPath -Parent) -Force
  python -m apps_rg --section $s --jd $jd --manual-brief $brief --provider qwen_vllm --target-company $company --target-role $role --attempts 4 --accept review --pin 2>&1 | Tee-Object -FilePath $logPath | Select-String -Pattern "PINNED|PIN_SKIPPED|attempt \d+/\d+|PRODUCT_X3_STATUS" | ForEach-Object { Write-Host $_.Line }
  $rc = $LASTEXITCODE
  $elapsed = [int]((Get-Date) - $started).TotalSeconds
  $pinned = Test-Path "artifacts/apps_rg/_pinned/$s"
  $summary += [PSCustomObject]@{Section=$s; rc=$rc; elapsed_s=$elapsed; pinned=$pinned}
  Write-Host "---- $s done rc=$rc elapsed=${elapsed}s pinned=$pinned ----"
}
$summary | Format-Table -AutoSize
$summary | ConvertTo-Json | Out-File "artifacts/apps_rg/_pinned/_assembled/sweep_summary.json"
Write-Host "==== ASSEMBLING ===="
python -m apps_rg --assemble-from-pinned 2>&1 | Select-String -Pattern "ASSEMBLED|ASSEMBLE_STATUS|assemble_status"
Write-Host "ASSEMBLE_RC=$LASTEXITCODE"
