$ErrorActionPreference = 'Stop'
$base = 'C:\Git\Agentic-Workflow-FRESH'
$dstAC = Join-Path $base 'artifacts\certification\review\agentic_core'
$dstApps = Join-Path $base 'artifacts\certification\review\apps'
$dirs = @(
  $dstAC, $dstApps,
  (Join-Path $dstAC 'compiler_output'),
  (Join-Path $dstAC 'positive_controls'),
  (Join-Path $dstAC 'runtime_evidence'),
  (Join-Path $dstAC 'integrated_runtime'),
  (Join-Path $dstAC 'e2e'),
  (Join-Path $dstAC 'source_inputs'),
  (Join-Path $dstAC 'mutation_rejection'),
  (Join-Path $dstAC 'scripts'),
  (Join-Path $dstApps 'compiler_output'),
  (Join-Path $dstApps 'per_app_evidence'),
  (Join-Path $dstApps 'rg_e2e'),
  (Join-Path $dstApps 'source_inputs'),
  (Join-Path $dstApps 'mutation_rejection'),
  (Join-Path $dstApps 'scripts')
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

$artC = Join-Path $base 'artifacts\certification'

# ===== agentic_core arm =====
$acOut = Join-Path $dstAC 'compiler_output'
Copy-Item (Join-Path $artC 'final_requirement_signoff_report.*') $acOut -Force
Copy-Item (Join-Path $artC 'final_requirement_signoff_bundle_verification.json') $acOut -Force
Copy-Item (Join-Path $artC 'HUNDRED_PERCENT_RUNTIME_PROOF.json') $acOut -Force
Copy-Item (Join-Path $artC 'HUNDRED_PERCENT_RUNTIME_ADDENDUM.md') $acOut -Force
Copy-Item (Join-Path $artC 'FORTKNOX_SIGNED_PROOF_AUDIT_PACKET.md') $acOut -Force
Copy-Item (Join-Path $artC 'FORTKNOX_W4_COMPLETION_ADDENDUM.md') $acOut -Force
Copy-Item (Join-Path $artC 'requirement_count_receipt.json') $acOut -Force
Copy-Item (Join-Path $artC 'schema_validation_report.json') $acOut -Force
Copy-Item (Join-Path $artC 'layer_boundary_report_*.json') $acOut -Force
Copy-Item (Join-Path $artC 'ci_gate_binding_report*.json') $acOut -Force
Copy-Item (Join-Path $artC 'artifact_payload_hash_report.json') $acOut -Force
Copy-Item (Join-Path $artC 'control_surface_separation_report.json') $acOut -Force
Copy-Item (Join-Path $artC 'rtc_req_*.json') $acOut -Force
Copy-Item (Join-Path $artC 'runtime_evidence_overrides.json') $acOut -Force
Copy-Item (Join-Path $artC 'formula_verification_report.json') $acOut -Force
Copy-Item (Join-Path $artC 'source_divergence_report.json') $acOut -Force
Copy-Item (Join-Path $artC 'downgraded_rows_report.json') $acOut -Force

Copy-Item (Join-Path $artC 'positive_control_RTC-REQ-*.json') (Join-Path $dstAC 'positive_controls') -Force

$mr = Join-Path $dstAC 'mutation_rejection'
Copy-Item (Join-Path $artC 'fortknox_mutation_rejection_report.json') $mr -Force
Copy-Item (Join-Path $artC '_mutation_*.json') $mr -Force

robocopy (Join-Path $artC 'runtime') (Join-Path $dstAC 'runtime_evidence') /E /NFL /NDL /NJH /NJS /NP | Out-Null
robocopy (Join-Path $artC 'integrated_runtime') (Join-Path $dstAC 'integrated_runtime') /E /NFL /NDL /NJH /NJS /NP | Out-Null
robocopy (Join-Path $artC 'agentic_core_e2e') (Join-Path $dstAC 'e2e') /E /NFL /NDL /NJH /NJS /NP | Out-Null

$acSrc = Join-Path $dstAC 'source_inputs'
Copy-Item (Join-Path $base 'data\certification\evidence_assertions.jsonl') $acSrc -Force
Copy-Item (Join-Path $base 'data\certification\evidence_manifest.jsonl') $acSrc -Force
Copy-Item (Join-Path $base 'data\certification\requirements_source.json') $acSrc -Force
Copy-Item (Join-Path $base 'data\certification\requirement_signoff_schema.json') $acSrc -Force
robocopy (Join-Path $base 'config\certification\schemas') (Join-Path $acSrc 'schemas') /E /NFL /NDL /NJH /NJS /NP | Out-Null

$acScripts = Join-Path $dstAC 'scripts'
Copy-Item (Join-Path $base 'tools\cert\compile_requirement_signoff.py') $acScripts -Force
Copy-Item (Join-Path $base 'tools\cert\verify_final_requirement_signoff_bundle.py') $acScripts -Force -ErrorAction SilentlyContinue
if (-not (Test-Path (Join-Path $acScripts 'compile_requirement_signoff.py'))) {
  Copy-Item (Join-Path $base 'scripts\verify_final_requirement_signoff_bundle.py') $acScripts -Force -ErrorAction SilentlyContinue
}
Copy-Item (Join-Path $base 'tools\certification\generate_100pct_runtime_proof.py') $acScripts -Force

# ===== apps arm =====
$apE = Join-Path $artC 'apps_e2e'
$apOut = Join-Path $dstApps 'compiler_output'
Copy-Item (Join-Path $apE 'apps_e2e_signoff_report.*') $apOut -Force
Copy-Item (Join-Path $apE 'APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json') $apOut -Force
Copy-Item (Join-Path $apE 'apps_e2e_matrix.json') $apOut -Force
Copy-Item (Join-Path $apE 'verifier_report.json') $apOut -Force
Copy-Item (Join-Path $apE 'apps_mutation_rejection_report.json') (Join-Path $dstApps 'mutation_rejection') -Force

foreach ($app in 'apps_eval','apps_exec','apps_lic','apps_qna','apps_research','apps_rfp','apps_rg','apps_underwriting_ai') {
  $src = Join-Path $apE $app
  if (Test-Path $src) {
    robocopy $src (Join-Path (Join-Path $dstApps 'per_app_evidence') $app) /E /NFL /NDL /NJH /NJS /NP | Out-Null
  }
}

robocopy (Join-Path $artC 'apps_rg_e2e') (Join-Path $dstApps 'rg_e2e') /E /NFL /NDL /NJH /NJS /NP | Out-Null

$apSrc = Join-Path $dstApps 'source_inputs'
Copy-Item (Join-Path $base 'data\certification\apps_evidence_assertions.jsonl') $apSrc -Force
Copy-Item (Join-Path $base 'data\certification\apps_domain_evidence_assertions.jsonl') $apSrc -Force
Copy-Item (Join-Path $base 'data\certification\apps_negative_control_assertions.jsonl') $apSrc -Force
Copy-Item (Join-Path $base 'data\certification\apps_e2e_requirements_source.json') $apSrc -Force

$apScripts = Join-Path $dstApps 'scripts'
Copy-Item (Join-Path $base 'tools\cert\compile_apps_e2e_signoff.py') $apScripts -Force
Copy-Item (Join-Path $base 'tools\certification\generate_apps_100pct_runtime_proof.py') $apScripts -Force

$acCount = (Get-ChildItem $dstAC -Recurse -File).Count
$apCount = (Get-ChildItem $dstApps -Recurse -File).Count
$acSize = [math]::Round(((Get-ChildItem $dstAC -Recurse -File | Measure-Object Length -Sum).Sum / 1MB), 2)
$apSize = [math]::Round(((Get-ChildItem $dstApps -Recurse -File | Measure-Object Length -Sum).Sum / 1MB), 2)
Write-Host "STAGED"
Write-Host ("  agentic_core: {0} files, {1} MB" -f $acCount, $acSize)
Write-Host ("  apps:         {0} files, {1} MB" -f $apCount, $apSize)
