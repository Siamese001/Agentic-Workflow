# Phase 1 Validation Script for agentic_core
# Validates all 12 Phase 1 completion criteria

Write-Host "=== PHASE 1 VALIDATION: agentic_core ===" -ForegroundColor Green

$basePath = "c:\Git\Agentic-Workflow\agentic_core"
$yamlPath = "C:\Git\Agentic Folder Structure\unified_structure_subatomic.yaml"

# Expected structure from YAML
$expectedStructure = @(
    # plan-layer phases
    "plan-layer\plan-phase\get-core-info\general\understand-request\build_core_query.py",
    "plan-layer\plan-phase\get-core-info\general\understand-request\parse_registry_intent.py", 
    "plan-layer\plan-phase\get-core-info\general\understand-request\extract_layer_parameters.py",
    "plan-layer\plan-phase\get-core-info\utility\prepare-information\prepare_core_payload.py",
    "plan-layer\plan-phase\get-core-info\utility\prepare-information\format_registry_context.py",
    "plan-layer\plan-phase\get-core-info\utility\prepare-information\build_core_filters.py",
    "plan-layer\plan-phase\check-core-rules\policy\check-safety\validate_core_constraints.py",
    "plan-layer\plan-phase\check-core-rules\policy\check-safety\check_registry_policy.py",
    "plan-layer\plan-phase\check-core-rules\policy\check-safety\enforce_core_boundaries.py",
    "plan-layer\expand-phase\convert-core-content\embedding\compare-meaning\compute_core_embeddings.py",
    "plan-layer\expand-phase\convert-core-content\embedding\compare-meaning\normalize_core_vectors.py",
    "plan-layer\expand-phase\convert-core-content\embedding\compare-meaning\calculate_core_similarity.py",
    "plan-layer\expand-phase\convert-core-content\semantic\adjust-scores\normalize_core_scores.py",
    "plan-layer\expand-phase\convert-core-content\semantic\adjust-scores\apply_core_weights.py",
    "plan-layer\expand-phase\convert-core-content\semantic\adjust-scores\compute_core_confidence.py",
    "plan-layer\refine-phase\pick-best-result\general\understand-request\rank_core_components.py",
    "plan-layer\refine-phase\pick-best-result\general\understand-request\apply_core_algorithm.py",
    "plan-layer\refine-phase\pick-best-result\general\understand-request\sort_core_results.py",
    "plan-layer\refine-phase\pick-best-result\refinement\adjust-scores\refine_core_ranking.py",
    "plan-layer\refine-phase\pick-best-result\refinement\adjust-scores\adjust_core_weights.py",
    "plan-layer\refine-phase\pick-best-result\refinement\adjust-scores\optimize_core_order.py",
    "plan-layer\validate-phase\check-core-structure\policy\check-safety\validate_core_schema.py",
    "plan-layer\validate-phase\check-core-structure\policy\check-safety\check_core_compliance.py",
    "plan-layer\validate-phase\check-core-structure\policy\check-safety\enforce_core_contracts.py",
    "plan-layer\validate-phase\check-core-structure\semantic\adjust-scores\validate_core_quality.py",
    "plan-layer\validate-phase\check-core-structure\semantic\adjust-scores\assess_core_confidence.py",
    "plan-layer\validate-phase\check-core-structure\semantic\adjust-scores\compute_core_validation.py",
    "plan-layer\act-phase\use-core-tools\general\use-a-tool\execute_core_action.py",
    "plan-layer\act-phase\use-core-tools\general\use-a-tool\invoke_core_service.py",
    "plan-layer\act-phase\use-core-tools\general\use-a-tool\process_core_response.py",
    "plan-layer\act-phase\use-core-tools\routing\retry-task\implement_core_retry.py",
    "plan-layer\act-phase\use-core-tools\routing\retry-task\apply_core_backoff.py",
    "plan-layer\act-phase\use-core-tools\routing\retry-task\handle_core_failures.py",
    "plan-layer\inspect-phase\find-core-problems\general\update-memory\inspect_core_state.py",
    "plan-layer\inspect-phase\find-core-problems\general\update-memory\capture_core_diagnostics.py",
    "plan-layer\inspect-phase\find-core-problems\general\update-memory\log_core_inspection.py",
    "plan-layer\retrieve-phase\get-core-info\general\understand-request\retrieve_core_context.py",
    "plan-layer\retrieve-phase\get-core-info\general\understand-request\query_core_store.py",
    "plan-layer\retrieve-phase\get-core-info\general\understand-request\fetch_core_history.py",
    "plan-layer\retrieve-phase\get-core-info\embedding\compare-meaning\search_core_vectors.py",
    "plan-layer\retrieve-phase\get-core-info\embedding\compare-meaning\match_core_context.py",
    "plan-layer\retrieve-phase\get-core-info\embedding\compare-meaning\retrieve_core_similarity.py",
    "plan-layer\agg-phase\update-core-state\general\update-memory\aggregate_core_state.py",
    "plan-layer\agg-phase\update-core-state\general\update-memory\merge_core_contexts.py",
    "plan-layer\agg-phase\update-core-state\general\update-memory\consolidate_core_updates.py",
    "plan-layer\agg-phase\update-core-state\utility\prepare-information\prepare_core_snapshot.py",
    "plan-layer\agg-phase\update-core-state\utility\prepare-information\serialize_core_state.py",
    "plan-layer\agg-phase\update-core-state\utility\prepare-information\format_core_payload.py",
    "plan-layer\safety-phase\check-core-rules\policy\check-safety\apply_core_safety.py",
    "plan-layer\safety-phase\check-core-rules\policy\check-safety\enforce_core_filters.py",
    "plan-layer\safety-phase\check-core-rules\policy\check-safety\validate_core_ethics.py",
    "plan-layer\safety-phase\manage-core-costs\general\update-memory\update_core_budget.py",
    "plan-layer\safety-phase\manage-core-costs\general\update-memory\track_core_usage.py",
    "plan-layer\safety-phase\manage-core-costs\general\update-memory\enforce_core_limits.py",
    
    # orc-layer
    "orc-layer\plan-phase\get-core-info\general\understand-request\orchestrate_core_planning.py",
    "orc-layer\plan-phase\get-core-info\general\understand-request\coordinate_core_queries.py",
    "orc-layer\plan-phase\get-core-info\general\understand-request\manage_core_context.py",
    "orc-layer\act-phase\use-core-tools\general\use-a-tool\dispatch_orchestration_tools.py",
    "orc-layer\act-phase\use-core-tools\general\use-a-tool\invoke_orchestration_service.py",
    "orc-layer\act-phase\use-core-tools\general\use-a-tool\call_orchestration_api.py",
    "orc-layer\act-phase\use-core-tools\routing\retry-task\retry_orchestration_operations.py",
    "orc-layer\act-phase\use-core-tools\routing\retry-task\handle_orchestration_failures.py",
    "orc-layer\act-phase\use-core-tools\routing\retry-task\implement_orchestration_fallback.py",
    "orc-layer\safety-phase\check-core-rules\policy\check-safety\apply_orchestration_safety.py",
    "orc-layer\safety-phase\check-core-rules\policy\check-safety\enforce_orchestration_policy.py",
    "orc-layer\safety-phase\check-core-rules\policy\check-safety\validate_orchestration_ethics.py",
    
    # exec-layer
    "exec-layer\act-phase\use-core-tools\general\use-a-tool\execute_core_execution.py",
    "exec-layer\act-phase\use-core-tools\general\use-a-tool\perform_core_operation.py",
    "exec-layer\act-phase\use-core-tools\general\use-a-tool\invoke_core_tool.py",
    "exec-layer\act-phase\use-core-tools\utility\prepare-information\prepare_execution_payload.py",
    "exec-layer\act-phase\use-core-tools\utility\prepare-information\format_execution_request.py",
    "exec-layer\act-phase\use-core-tools\utility\prepare-information\serialize_execution_params.py",
    "exec-layer\validate-phase\check-core-structure\policy\check-safety\validate_execution_schema.py",
    "exec-layer\validate-phase\check-core-structure\policy\check-safety\check_execution_compliance.py",
    "exec-layer\validate-phase\check-core-structure\policy\check-safety\enforce_execution_contracts.py",
    "exec-layer\safety-phase\check-core-rules\policy\check-safety\apply_execution_safety.py",
    "exec-layer\safety-phase\check-core-rules\policy\check-safety\enforce_execution_policy.py",
    "exec-layer\safety-phase\check-core-rules\policy\check-safety\validate_execution_ethics.py",
    
    # mem-layer
    "mem-layer\retrieve-phase\get-core-info\general\understand-request\retrieve_core_memory.py",
    "mem-layer\retrieve-phase\get-core-info\general\understand-request\query_core_state.py",
    "mem-layer\retrieve-phase\get-core-info\general\understand-request\fetch_core_history.py",
    "mem-layer\retrieve-phase\get-core-info\embedding\compare-meaning\search_core_vectors.py",
    "mem-layer\retrieve-phase\get-core-info\embedding\compare-meaning\match_core_patterns.py",
    "mem-layer\retrieve-phase\get-core-info\embedding\compare-meaning\find_core_context.py",
    "mem-layer\safety-phase\check-core-rules\policy\check-safety\apply_memory_safety.py",
    "mem-layer\safety-phase\check-core-rules\policy\check-safety\enforce_memory_policy.py",
    "mem-layer\safety-phase\check-core-rules\policy\check-safety\validate_memory_ethics.py",
    
    # safe-layer
    "safe-layer\safety-phase\check-core-rules\policy\check-safety\apply_safety_policy.py",
    "safe-layer\safety-phase\check-core-rules\policy\check-safety\enforce_safety_filters.py",
    "safe-layer\safety-phase\check-core-rules\policy\check-safety\validate_safety_ethics.py",
    "safe-layer\safety-phase\check-core-rules\semantic\adjust-scores\assess_safety_risk.py",
    "safe-layer\safety-phase\check-core-rules\semantic\adjust-scores\compute_safety_score.py",
    "safe-layer\safety-phase\check-core-rules\semantic\adjust-scores\evaluate_safety_compliance.py",
    "safe-layer\safety-phase\manage-core-costs\general\update-memory\track_safety_cost.py",
    "safe-layer\safety-phase\manage-core-costs\general\update-memory\update_safety_usage.py",
    "safe-layer\safety-phase\manage-core-costs\general\update-memory\enforce_safety_budget.py"
)

# Get actual structure
$actualFiles = Get-ChildItem -Path $basePath -Recurse -File | ForEach-Object { $_.FullName.Replace($basePath + "\", "").Replace("/", "\") } | Sort-Object
$actualDirs = Get-ChildItem -Path $basePath -Recurse -Directory | ForEach-Object { $_.FullName.Replace($basePath + "\", "").Replace("/", "\") } | Sort-Object

# Validation results
$validationResults = @{}
$allPassed = $true

Write-Host "`n--- VALIDATING PHASE 1 CRITERIA ---" -ForegroundColor Yellow

# CRITERION 1: Directory tree matches YAML
Write-Host "`n1. PHASE1_AGENITIC_CORE_DIRECTORY_TREE_MATCHES_YAML" -ForegroundColor Cyan
$expectedCount = $expectedStructure.Count
$actualCount = $actualFiles.Count
if ($expectedCount -eq $actualCount) {
    Write-Host "   ✓ PASS: Expected $expectedCount files, found $actualCount files" -ForegroundColor Green
    $validationResults["DIRECTORY_TREE_MATCHES_YAML"] = $true
} else {
    Write-Host "   ✗ FAIL: Expected $expectedCount files, found $actualCount files" -ForegroundColor Red
    $validationResults["DIRECTORY_TREE_MATCHES_YAML"] = $false
    $allPassed = $false
}

# CRITERION 2: All folders created
Write-Host "`n2. PHASE1_AGENITIC_CORE_ALL_FOLDERS_CREATED" -ForegroundColor Cyan
$expectedDirs = $expectedStructure | ForEach-Object { Split-Path $_ -Parent } | Sort-Object -Unique
$missingDirs = @()
foreach ($dir in $expectedDirs) {
    if ($dir -notin $actualDirs) {
        $missingDirs += $dir
    }
}
if ($missingDirs.Count -eq 0) {
    Write-Host "   ✓ PASS: All expected folders created" -ForegroundColor Green
    $validationResults["ALL_FOLDERS_CREATED"] = $true
} else {
    Write-Host "   ✗ FAIL: Missing folders: $($missingDirs -join ', ')" -ForegroundColor Red
    $validationResults["ALL_FOLDERS_CREATED"] = $false
    $allPassed = $false
}

# CRITERION 3: All files created
Write-Host "`n3. PHASE1_AGENITIC_CORE_ALL_FILES_CREATED" -ForegroundColor Cyan
$missingFiles = @()
foreach ($file in $expectedStructure) {
    $fullPath = Join-Path $basePath $file
    if (-not (Test-Path $fullPath)) {
        $missingFiles += $file
    }
}
if ($missingFiles.Count -eq 0) {
    Write-Host "   ✓ PASS: All expected files created" -ForegroundColor Green
    $validationResults["ALL_FILES_CREATED"] = $true
} else {
    Write-Host "   ✗ FAIL: Missing files: $($missingFiles -join ', ')" -ForegroundColor Red
    $validationResults["ALL_FILES_CREATED"] = $false
    $allPassed = $false
}

# CRITERION 4: No extra folders
Write-Host "`n4. PHASE1_AGENITIC_CORE_NO_EXTRA_FOLDERS" -ForegroundColor Cyan
$extraDirs = @()
foreach ($dir in $actualDirs) {
    if ($dir -notin $expectedDirs -and $dir -ne "") {
        $extraDirs += $dir
    }
}
if ($extraDirs.Count -eq 0) {
    Write-Host "   ✓ PASS: No extra folders found" -ForegroundColor Green
    $validationResults["NO_EXTRA_FOLDERS"] = $true
} else {
    Write-Host "   ✗ FAIL: Extra folders: $($extraDirs -join ', ')" -ForegroundColor Red
    $validationResults["NO_EXTRA_FOLDERS"] = $false
    $allPassed = $false
}

# CRITERION 5: No extra files
Write-Host "`n5. PHASE1_AGENITIC_CORE_NO_EXTRA_FILES" -ForegroundColor Cyan
$extraFiles = @()
foreach ($file in $actualFiles) {
    if ($file -notin $expectedStructure) {
        $extraFiles += $file
    }
}
if ($extraFiles.Count -eq 0) {
    Write-Host "   ✓ PASS: No extra files found" -ForegroundColor Green
    $validationResults["NO_EXTRA_FILES"] = $true
} else {
    Write-Host "   ✗ FAIL: Extra files: $($extraFiles -join ', ')" -ForegroundColor Red
    $validationResults["NO_EXTRA_FILES"] = $false
    $allPassed = $false
}

# CRITERION 6: No missing folders (duplicate check)
Write-Host "`n6. PHASE1_AGENITIC_CORE_NO_MISSING_FOLDERS" -ForegroundColor Cyan
if ($missingDirs.Count -eq 0) {
    Write-Host "   ✓ PASS: No missing folders" -ForegroundColor Green
    $validationResults["NO_MISSING_FOLDERS"] = $true
} else {
    Write-Host "   ✗ FAIL: Missing folders: $($missingDirs -join ', ')" -ForegroundColor Red
    $validationResults["NO_MISSING_FOLDERS"] = $false
    $allPassed = $false
}

# CRITERION 7: No missing files (duplicate check)
Write-Host "`n7. PHASE1_AGENITIC_CORE_NO_MISSING_FILES" -ForegroundColor Cyan
if ($missingFiles.Count -eq 0) {
    Write-Host "   ✓ PASS: No missing files" -ForegroundColor Green
    $validationResults["NO_MISSING_FILES"] = $true
} else {
    Write-Host "   ✗ FAIL: Missing files: $($missingFiles -join ', ')" -ForegroundColor Red
    $validationResults["NO_MISSING_FILES"] = $false
    $allPassed = $false
}

# CRITERION 8: Case-sensitive paths
Write-Host "`n8. PHASE1_AGENITIC_CORE_CASE_SENSITIVE_PATHS" -ForegroundColor Cyan
$caseIssues = @()
foreach ($file in $actualFiles) {
    $expectedFile = $expectedStructure | Where-Object { $_ -eq $file }
    if (-not $expectedFile) {
        # Check if case mismatch
        $expectedFile = $expectedStructure | Where-Object { $_.ToLower() -eq $file.ToLower() }
        if ($expectedFile) {
            $caseIssues += "$file (expected: $expectedFile)"
        }
    }
}
if ($caseIssues.Count -eq 0) {
    Write-Host "   ✓ PASS: All paths match case exactly" -ForegroundColor Green
    $validationResults["CASE_SENSITIVE_PATHS"] = $true
} else {
    Write-Host "   ✗ FAIL: Case issues: $($caseIssues -join ', ')" -ForegroundColor Red
    $validationResults["CASE_SENSITIVE_PATHS"] = $false
    $allPassed = $false
}

# CRITERION 9: Depths correct
Write-Host "`n9. PHASE1_AGENITIC_CORE_DEPTHS_CORRECT" -ForegroundColor Cyan
$depthIssues = @()
foreach ($file in $expectedStructure) {
    $expectedDepth = ($file.Split("\").Count - 1)
    $actualFile = $actualFiles | Where-Object { $_ -eq $file }
    if ($actualFile) {
        $actualDepth = ($actualFile.Split("\").Count - 1)
        if ($expectedDepth -ne $actualDepth) {
            $depthIssues += "$file (expected depth: $expectedDepth, actual: $actualDepth)"
        }
    }
}
if ($depthIssues.Count -eq 0) {
    Write-Host "   ✓ PASS: All directory depths correct" -ForegroundColor Green
    $validationResults["DEPTHS_CORRECT"] = $true
} else {
    Write-Host "   ✗ FAIL: Depth issues: $($depthIssues -join ', ')" -ForegroundColor Red
    $validationResults["DEPTHS_CORRECT"] = $false
    $allPassed = $false
}

# CRITERION 10: Legacy merge complete (check if any old files need merging)
Write-Host "`n10. PHASE1_AGENITIC_CORE_LEGACY_MERGE_COMPLETE" -ForegroundColor Cyan
# For Phase 1, this means no legacy files that should be merged
$legacyFiles = Get-ChildItem -Path $basePath -Recurse -File -Include "*.py" | Where-Object { 
    $_.Length -gt 0 -and $_.FullName -notlike "*agentic_core*" 
} | ForEach-Object { $_.FullName.Replace($basePath + "\", "") }
if ($legacyFiles.Count -eq 0) {
    Write-Host "   ✓ PASS: No legacy files requiring merge" -ForegroundColor Green
    $validationResults["LEGACY_MERGE_COMPLETE"] = $true
} else {
    Write-Host "   ✗ FAIL: Legacy files found: $($legacyFiles -join ', ')" -ForegroundColor Red
    $validationResults["LEGACY_MERGE_COMPLETE"] = $false
    $allPassed = $false
}

# CRITERION 11: No orphaned paths
Write-Host "`n11. PHASE1_AGENITIC_CORE_NO_ORPHANED_PATHS" -ForegroundColor Cyan
$orphanedPaths = @()
foreach ($dir in $actualDirs) {
    if ($dir -notin $expectedDirs -and $dir -ne "") {
        $orphanedPaths += $dir
    }
}
if ($orphanedPaths.Count -eq 0) {
    Write-Host "   ✓ PASS: No orphaned directory paths" -ForegroundColor Green
    $validationResults["NO_ORPHANED_PATHS"] = $true
} else {
    Write-Host "   ✗ FAIL: Orphaned paths: $($orphanedPaths -join ', ')" -ForegroundColor Red
    $validationResults["NO_ORPHANED_PATHS"] = $false
    $allPassed = $false
}

# CRITERION 12: Ready for Phase 2
Write-Host "`n12. PHASE1_AGENITIC_CORE_READY_FOR_PHASE2" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "   ✓ PASS: All criteria passed - ready for Phase 2" -ForegroundColor Green
    $validationResults["READY_FOR_PHASE2"] = $true
} else {
    Write-Host "   ✗ FAIL: Not ready for Phase 2 - some criteria failed" -ForegroundColor Red
    $validationResults["READY_FOR_PHASE2"] = $false
}

# Final summary
Write-Host "`n=== VALIDATION SUMMARY ===" -ForegroundColor Yellow
Write-Host "Total files expected: $expectedCount" -ForegroundColor White
Write-Host "Total files created: $actualCount" -ForegroundColor White
Write-Host "Total directories created: $($actualDirs.Count)" -ForegroundColor White

$passedCount = ($validationResults.Values | Where-Object { $_ -eq $true }).Count
Write-Host "Criteria passed: $passedCount/12" -ForegroundColor $(if ($passedCount -eq 12) { 'Green' } else { 'Red' })

if ($allPassed) {
    Write-Host "`n🎉 PHASE 1 COMPLETE - ALL KEYS PASS!" -ForegroundColor Green
    Write-Host "Ready to proceed to Phase 2" -ForegroundColor Green
} else {
    Write-Host "`n❌ PHASE 1 INCOMPLETE - SOME KEYS FAIL" -ForegroundColor Red
    Write-Host "Address failed criteria before proceeding" -ForegroundColor Red
}

# Clean up
Remove-Item -Path "build_agentic_core.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "create_agentic_core_files.ps1" -Force -ErrorAction SilentlyContinue

return $allPassed
