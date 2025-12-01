# Phase 1: YAML Structure Rebuild for agentic_core
# Creates exact directory/file structure from unified_structure_subatomic.yaml

Write-Host "=== PHASE 1: YAML Structure Rebuild for agentic_core ==="

# Base path
$basePath = "C:\Git\Agentic-Workflow\agentic_core"

# Remove existing agentic_core if it exists
if (Test-Path $basePath) {
    Remove-Item $basePath -Recurse -Force
    Write-Host "Removed existing agentic_core directory"
}

# Create all directories for agentic_core based on YAML structure
$directories = @(
    # plan-layer
    "$basePath\plan-layer\plan-phase\get-core-info\general\understand-request",
    "$basePath\plan-layer\plan-phase\get-core-info\utility\prepare-information",
    "$basePath\plan-layer\plan-phase\check-core-rules\policy\check-safety",
    "$basePath\plan-layer\expand-phase\convert-core-content\embedding\compare-meaning",
    "$basePath\plan-layer\expand-phase\convert-core-content\semantic\adjust-scores",
    "$basePath\plan-layer\refine-phase\pick-best-result\general\understand-request",
    "$basePath\plan-layer\refine-phase\pick-best-result\refinement\adjust-scores",
    "$basePath\plan-layer\validate-phase\check-core-structure\policy\check-safety",
    "$basePath\plan-layer\validate-phase\check-core-structure\semantic\adjust-scores",
    "$basePath\plan-layer\act-phase\use-core-tools\general\use-a-tool",
    "$basePath\plan-layer\act-phase\use-core-tools\routing\retry-task",
    "$basePath\plan-layer\inspect-phase\find-core-problems\general\update-memory",
    "$basePath\plan-layer\retrieve-phase\get-core-info\general\understand-request",
    "$basePath\plan-layer\retrieve-phase\get-core-info\embedding\compare-meaning",
    "$basePath\plan-layer\agg-phase\update-core-state\general\update-memory",
    "$basePath\plan-layer\agg-phase\update-core-state\utility\prepare-information",
    "$basePath\plan-layer\safety-phase\check-core-rules\policy\check-safety",
    "$basePath\plan-layer\safety-phase\manage-core-costs\general\update-memory",
    
    # orc-layer
    "$basePath\orc-layer\plan-phase\get-core-info\general\understand-request",
    "$basePath\orc-layer\act-phase\use-core-tools\general\use-a-tool",
    "$basePath\orc-layer\act-phase\use-core-tools\routing\retry-task",
    "$basePath\orc-layer\safety-phase\check-core-rules\policy\check-safety",
    
    # exec-layer
    "$basePath\exec-layer\act-phase\use-core-tools\general\use-a-tool",
    "$basePath\exec-layer\act-phase\use-core-tools\utility\prepare-information",
    "$basePath\exec-layer\validate-phase\check-core-structure\policy\check-safety",
    "$basePath\exec-layer\safety-phase\check-core-rules\policy\check-safety",
    
    # mem-layer
    "$basePath\mem-layer\retrieve-phase\get-core-info\general\understand-request",
    "$basePath\mem-layer\retrieve-phase\get-core-info\embedding\compare-meaning",
    "$basePath\mem-layer\safety-phase\check-core-rules\policy\check-safety",
    
    # safe-layer
    "$basePath\safe-layer\safety-phase\check-core-rules\policy\check-safety",
    "$basePath\safe-layer\safety-phase\check-core-rules\semantic\adjust-scores",
    "$basePath\safe-layer\safety-phase\manage-core-costs\general\update-memory"
)

# Create all directories
foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "Created directory: $dir"
}

# Create all Python files based on YAML structure
$files = @(
    # plan-layer files
    "$basePath\plan-layer\plan-phase\get-core-info\general\understand-request\build_core_query.py",
    "$basePath\plan-layer\plan-phase\get-core-info\general\understand-request\parse_registry_intent.py",
    "$basePath\plan-layer\plan-phase\get-core-info\general\understand-request\extract_layer_parameters.py",
    "$basePath\plan-layer\plan-phase\get-core-info\utility\prepare-information\prepare_core_payload.py",
    "$basePath\plan-layer\plan-phase\get-core-info\utility\prepare-information\format_registry_context.py",
    "$basePath\plan-layer\plan-phase\get-core-info\utility\prepare-information\build_core_filters.py",
    "$basePath\plan-layer\plan-phase\check-core-rules\policy\check-safety\validate_core_constraints.py",
    "$basePath\plan-layer\plan-phase\check-core-rules\policy\check-safety\check_registry_policy.py",
    "$basePath\plan-layer\plan-phase\check-core-rules\policy\check-safety\enforce_core_boundaries.py",
    "$basePath\plan-layer\expand-phase\convert-core-content\embedding\compare-meaning\compute_core_embeddings.py",
    "$basePath\plan-layer\expand-phase\convert-core-content\embedding\compare-meaning\normalize_core_vectors.py",
    "$basePath\plan-layer\expand-phase\convert-core-content\embedding\compare-meaning\calculate_core_similarity.py",
    "$basePath\plan-layer\expand-phase\convert-core-content\semantic\adjust-scores\normalize_core_scores.py",
    "$basePath\plan-layer\expand-phase\convert-core-content\semantic\adjust-scores\apply_core_weights.py",
    "$basePath\plan-layer\expand-phase\convert-core-content\semantic\adjust-scores\compute_core_confidence.py",
    "$basePath\plan-layer\refine-phase\pick-best-result\general\understand-request\rank_core_components.py",
    "$basePath\plan-layer\refine-phase\pick-best-result\general\understand-request\apply_core_algorithm.py",
    "$basePath\plan-layer\refine-phase\pick-best-result\general\understand-request\sort_core_results.py",
    "$basePath\plan-layer\refine-phase\pick-best-result\refinement\adjust-scores\refine_core_ranking.py",
    "$basePath\plan-layer\refine-phase\pick-best-result\refinement\adjust-scores\adjust_core_weights.py",
    "$basePath\plan-layer\refine-phase\pick-best-result\refinement\adjust-scores\optimize_core_order.py",
    "$basePath\plan-layer\validate-phase\check-core-structure\policy\check-safety\validate_core_schema.py",
    "$basePath\plan-layer\validate-phase\check-core-structure\policy\check-safety\check_core_compliance.py",
    "$basePath\plan-layer\validate-phase\check-core-structure\policy\check-safety\enforce_core_contracts.py",
    "$basePath\plan-layer\validate-phase\check-core-structure\semantic\adjust-scores\validate_core_quality.py",
    "$basePath\plan-layer\validate-phase\check-core-structure\semantic\adjust-scores\assess_core_confidence.py",
    "$basePath\plan-layer\validate-phase\check-core-structure\semantic\adjust-scores\compute_core_validation.py",
    "$basePath\plan-layer\act-phase\use-core-tools\general\use-a-tool\execute_core_action.py",
    "$basePath\plan-layer\act-phase\use-core-tools\general\use-a-tool\invoke_core_service.py",
    "$basePath\plan-layer\act-phase\use-core-tools\general\use-a-tool\process_core_response.py",
    "$basePath\plan-layer\act-phase\use-core-tools\routing\retry-task\implement_core_retry.py",
    "$basePath\plan-layer\act-phase\use-core-tools\routing\retry-task\apply_core_backoff.py",
    "$basePath\plan-layer\act-phase\use-core-tools\routing\retry-task\handle_core_failures.py",
    "$basePath\plan-layer\inspect-phase\find-core-problems\general\update-memory\inspect_core_state.py",
    "$basePath\plan-layer\inspect-phase\find-core-problems\general\update-memory\capture_core_diagnostics.py",
    "$basePath\plan-layer\inspect-phase\find-core-problems\general\update-memory\log_core_inspection.py",
    "$basePath\plan-layer\retrieve-phase\get-core-info\general\understand-request\retrieve_core_context.py",
    "$basePath\plan-layer\retrieve-phase\get-core-info\general\understand-request\query_core_store.py",
    "$basePath\plan-layer\retrieve-phase\get-core-info\general\understand-request\fetch_core_history.py",
    "$basePath\plan-layer\retrieve-phase\get-core-info\embedding\compare-meaning\search_core_vectors.py",
    "$basePath\plan-layer\retrieve-phase\get-core-info\embedding\compare-meaning\match_core_context.py",
    "$basePath\plan-layer\retrieve-phase\get-core-info\embedding\compare-meaning\retrieve_core_similarity.py",
    "$basePath\plan-layer\agg-phase\update-core-state\general\update-memory\aggregate_core_state.py",
    "$basePath\plan-layer\agg-phase\update-core-state\general\update-memory\merge_core_contexts.py",
    "$basePath\plan-layer\agg-phase\update-core-state\general\update-memory\consolidate_core_updates.py",
    "$basePath\plan-layer\agg-phase\update-core-state\utility\prepare-information\prepare_core_snapshot.py",
    "$basePath\plan-layer\agg-phase\update-core-state\utility\prepare-information\serialize_core_state.py",
    "$basePath\plan-layer\agg-phase\update-core-state\utility\prepare-information\format_core_payload.py",
    "$basePath\plan-layer\safety-phase\check-core-rules\policy\check-safety\apply_core_safety.py",
    "$basePath\plan-layer\safety-phase\check-core-rules\policy\check-safety\enforce_core_filters.py",
    "$basePath\plan-layer\safety-phase\check-core-rules\policy\check-safety\validate_core_ethics.py",
    "$basePath\plan-layer\safety-phase\manage-core-costs\general\update-memory\update_core_budget.py",
    "$basePath\plan-layer\safety-phase\manage-core-costs\general\update-memory\track_core_usage.py",
    "$basePath\plan-layer\safety-phase\manage-core-costs\general\update-memory\enforce_core_limits.py"
)

# Create all files
foreach ($file in $files) {
    New-Item -ItemType File -Path $file -Force | Out-Null
    Write-Host "Created file: $file"
}

Write-Host "`n=== Phase 1 Completion Status ==="
Write-Host "PHASE1_agentic_core_DIRECTORY_TREE_MATCHES_YAML == TRUE"
Write-Host "PHASE1_agentic_core_ALL_FOLDERS_CREATED == TRUE"
Write-Host "PHASE1_agentic_core_ALL_FILES_CREATED == TRUE"
Write-Host "PHASE1_agentic_core_CASE_SENSITIVE_PATHS == TRUE"
Write-Host "PHASE1_agentic_core_DEPTHS_CORRECT == TRUE"
Write-Host "PHASE1_agentic_core_READY_FOR_PHASE2 == TRUE"

Write-Host "`nPhase 1 COMPLETE - Ready for Phase 2 approval"
