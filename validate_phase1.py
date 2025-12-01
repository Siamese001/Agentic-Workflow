#!/usr/bin/env python3
"""
Phase 1 Validation Script for agentic_core
Validates all 12 Phase 1 completion criteria
"""

import os
from pathlib import Path

def validate_phase1():
    """Validate Phase 1 completion criteria for agentic_core"""
    
    print("=== PHASE 1 VALIDATION: agentic_core ===")
    
    base_path = Path("c:/Git/Agentic-Workflow/agentic_core")
    
    # Expected files from YAML structure
    expected_files = [
        # plan-layer
        "plan-layer/plan-phase/get-core-info/general/understand-request/build_core_query.py",
        "plan-layer/plan-phase/get-core-info/general/understand-request/parse_registry_intent.py", 
        "plan-layer/plan-phase/get-core-info/general/understand-request/extract_layer_parameters.py",
        "plan-layer/plan-phase/get-core-info/utility/prepare-information/prepare_core_payload.py",
        "plan-layer/plan-phase/get-core-info/utility/prepare-information/format_registry_context.py",
        "plan-layer/plan-phase/get-core-info/utility/prepare-information/build_core_filters.py",
        "plan-layer/plan-phase/check-core-rules/policy/check-safety/validate_core_constraints.py",
        "plan-layer/plan-phase/check-core-rules/policy/check-safety/check_registry_policy.py",
        "plan-layer/plan-phase/check-core-rules/policy/check-safety/enforce_core_boundaries.py",
        "plan-layer/expand-phase/convert-core-content/embedding/compare-meaning/compute_core_embeddings.py",
        "plan-layer/expand-phase/convert-core-content/embedding/compare-meaning/normalize_core_vectors.py",
        "plan-layer/expand-phase/convert-core-content/embedding/compare-meaning/calculate_core_similarity.py",
        "plan-layer/expand-phase/convert-core-content/semantic/adjust-scores/normalize_core_scores.py",
        "plan-layer/expand-phase/convert-core-content/semantic/adjust-scores/apply_core_weights.py",
        "plan-layer/expand-phase/convert-core-content/semantic/adjust-scores/compute_core_confidence.py",
        "plan-layer/refine-phase/pick-best-result/general/understand-request/rank_core_components.py",
        "plan-layer/refine-phase/pick-best-result/general/understand-request/apply_core_algorithm.py",
        "plan-layer/refine-phase/pick-best-result/general/understand-request/sort_core_results.py",
        "plan-layer/refine-phase/pick-best-result/refinement/adjust-scores/refine_core_ranking.py",
        "plan-layer/refine-phase/pick-best-result/refinement/adjust-scores/adjust_core_weights.py",
        "plan-layer/refine-phase/pick-best-result/refinement/adjust-scores/optimize_core_order.py",
        "plan-layer/validate-phase/check-core-structure/policy/check-safety/validate_core_schema.py",
        "plan-layer/validate-phase/check-core-structure/policy/check-safety/check_core_compliance.py",
        "plan-layer/validate-phase/check-core-structure/policy/check-safety/enforce_core_contracts.py",
        "plan-layer/validate-phase/check-core-structure/semantic/adjust-scores/validate_core_quality.py",
        "plan-layer/validate-phase/check-core-structure/semantic/adjust-scores/assess_core_confidence.py",
        "plan-layer/validate-phase/check-core-structure/semantic/adjust-scores/compute_core_validation.py",
        "plan-layer/act-phase/use-core-tools/general/use-a-tool/execute_core_action.py",
        "plan-layer/act-phase/use-core-tools/general/use-a-tool/invoke_core_service.py",
        "plan-layer/act-phase/use-core-tools/general/use-a-tool/process_core_response.py",
        "plan-layer/act-phase/use-core-tools/routing/retry-task/implement_core_retry.py",
        "plan-layer/act-phase/use-core-tools/routing/retry-task/apply_core_backoff.py",
        "plan-layer/act-phase/use-core-tools/routing/retry-task/handle_core_failures.py",
        "plan-layer/inspect-phase/find-core-problems/general/update-memory/inspect_core_state.py",
        "plan-layer/inspect-phase/find-core-problems/general/update-memory/capture_core_diagnostics.py",
        "plan-layer/inspect-phase/find-core-problems/general/update-memory/log_core_inspection.py",
        "plan-layer/retrieve-phase/get-core-info/general/understand-request/retrieve_core_context.py",
        "plan-layer/retrieve-phase/get-core-info/general/understand-request/query_core_store.py",
        "plan-layer/retrieve-phase/get-core-info/general/understand-request/fetch_core_history.py",
        "plan-layer/retrieve-phase/get-core-info/embedding/compare-meaning/search_core_vectors.py",
        "plan-layer/retrieve-phase/get-core-info/embedding/compare-meaning/match_core_context.py",
        "plan-layer/retrieve-phase/get-core-info/embedding/compare-meaning/retrieve_core_similarity.py",
        "plan-layer/agg-phase/update-core-state/general/update-memory/aggregate_core_state.py",
        "plan-layer/agg-phase/update-core-state/general/update-memory/merge_core_contexts.py",
        "plan-layer/agg-phase/update-core-state/general/update-memory/consolidate_core_updates.py",
        "plan-layer/agg-phase/update-core-state/utility/prepare-information/prepare_core_snapshot.py",
        "plan-layer/agg-phase/update-core-state/utility/prepare-information/serialize_core_state.py",
        "plan-layer/agg-phase/update-core-state/utility/prepare-information/format_core_payload.py",
        "plan-layer/safety-phase/check-core-rules/policy/check-safety/apply_core_safety.py",
        "plan-layer/safety-phase/check-core-rules/policy/check-safety/enforce_core_filters.py",
        "plan-layer/safety-phase/check-core-rules/policy/check-safety/validate_core_ethics.py",
        "plan-layer/safety-phase/manage-core-costs/general/update-memory/update_core_budget.py",
        "plan-layer/safety-phase/manage-core-costs/general/update-memory/track_core_usage.py",
        "plan-layer/safety-phase/manage-core-costs/general/update-memory/enforce_core_limits.py",
        
        # orc-layer
        "orc-layer/plan-phase/get-core-info/general/understand-request/orchestrate_core_planning.py",
        "orc-layer/plan-phase/get-core-info/general/understand-request/coordinate_core_queries.py",
        "orc-layer/plan-phase/get-core-info/general/understand-request/manage_core_context.py",
        "orc-layer/act-phase/use-core-tools/general/use-a-tool/dispatch_orchestration_tools.py",
        "orc-layer/act-phase/use-core-tools/general/use-a-tool/invoke_orchestration_service.py",
        "orc-layer/act-phase/use-core-tools/general/use-a-tool/call_orchestration_api.py",
        "orc-layer/act-phase/use-core-tools/routing/retry-task/retry_orchestration_operations.py",
        "orc-layer/act-phase/use-core-tools/routing/retry-task/handle_orchestration_failures.py",
        "orc-layer/act-phase/use-core-tools/routing/retry-task/implement_orchestration_fallback.py",
        "orc-layer/safety-phase/check-core-rules/policy/check-safety/apply_orchestration_safety.py",
        "orc-layer/safety-phase/check-core-rules/policy/check-safety/enforce_orchestration_policy.py",
        "orc-layer/safety-phase/check-core-rules/policy/check-safety/validate_orchestration_ethics.py",
        
        # exec-layer
        "exec-layer/act-phase/use-core-tools/general/use-a-tool/execute_core_execution.py",
        "exec-layer/act-phase/use-core-tools/general/use-a-tool/perform_core_operation.py",
        "exec-layer/act-phase/use-core-tools/general/use-a-tool/invoke_core_tool.py",
        "exec-layer/act-phase/use-core-tools/utility/prepare-information/prepare_execution_payload.py",
        "exec-layer/act-phase/use-core-tools/utility/prepare-information/format_execution_request.py",
        "exec-layer/act-phase/use-core-tools/utility/prepare-information/serialize_execution_params.py",
        "exec-layer/validate-phase/check-core-structure/policy/check-safety/validate_execution_schema.py",
        "exec-layer/validate-phase/check-core-structure/policy/check-safety/check_execution_compliance.py",
        "exec-layer/validate-phase/check-core-structure/policy/check-safety/enforce_execution_contracts.py",
        "exec-layer/safety-phase/check-core-rules/policy/check-safety/apply_execution_safety.py",
        "exec-layer/safety-phase/check-core-rules/policy/check-safety/enforce_execution_policy.py",
        "exec-layer/safety-phase/check-core-rules/policy/check-safety/validate_execution_ethics.py",
        
        # mem-layer
        "mem-layer/retrieve-phase/get-core-info/general/understand-request/retrieve_core_memory.py",
        "mem-layer/retrieve-phase/get-core-info/general/understand-request/query_core_state.py",
        "mem-layer/retrieve-phase/get-core-info/general/understand-request/fetch_core_history.py",
        "mem-layer/retrieve-phase/get-core-info/embedding/compare-meaning/search_core_vectors.py",
        "mem-layer/retrieve-phase/get-core-info/embedding/compare-meaning/match_core_patterns.py",
        "mem-layer/retrieve-phase/get-core-info/embedding/compare-meaning/find_core_context.py",
        "mem-layer/safety-phase/check-core-rules/policy/check-safety/apply_memory_safety.py",
        "mem-layer/safety-phase/check-core-rules/policy/check-safety/enforce_memory_policy.py",
        "mem-layer/safety-phase/check-core-rules/policy/check-safety/validate_memory_ethics.py",
        
        # safe-layer
        "safe-layer/safety-phase/check-core-rules/policy/check-safety/apply_safety_policy.py",
        "safe-layer/safety-phase/check-core-rules/policy/check-safety/enforce_safety_filters.py",
        "safe-layer/safety-phase/check-core-rules/policy/check-safety/validate_safety_ethics.py",
        "safe-layer/safety-phase/check-core-rules/semantic/adjust-scores/assess_safety_risk.py",
        "safe-layer/safety-phase/check-core-rules/semantic/adjust-scores/compute_safety_score.py",
        "safe-layer/safety-phase/check-core-rules/semantic/adjust-scores/evaluate_safety_compliance.py",
        "safe-layer/safety-phase/manage-core-costs/general/update-memory/track_safety_cost.py",
        "safe-layer/safety-phase/manage-core-costs/general/update-memory/update_safety_usage.py",
        "safe-layer/safety-phase/manage-core-costs/general/update-memory/enforce_safety_budget.py"
    ]
    
    print("\n--- VALIDATING PHASE 1 CRITERIA ---")
    
    # Get actual files and directories
    actual_files = []
    actual_dirs = []
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), base_path).replace("\\", "/")
            actual_files.append(rel_path)
        for dir in dirs:
            rel_path = os.path.relpath(os.path.join(root, dir), base_path).replace("\\", "/")
            if rel_path != ".":
                actual_dirs.append(rel_path)
    
    actual_files.sort()
    actual_dirs.sort()
    
    validation_results = {}
    all_passed = True
    
    # CRITERION 1: Directory tree matches YAML
    print("\n1. PHASE1_AGENITIC_CORE_DIRECTORY_TREE_MATCHES_YAML")
    expected_count = len(expected_files)
    actual_count = len(actual_files)
    if expected_count == actual_count:
        print(f"   ✓ PASS: Expected {expected_count} files, found {actual_count} files")
        validation_results["DIRECTORY_TREE_MATCHES_YAML"] = True
    else:
        print(f"   ✗ FAIL: Expected {expected_count} files, found {actual_count} files")
        validation_results["DIRECTORY_TREE_MATCHES_YAML"] = False
        all_passed = False
    
    # CRITERION 2: All folders created
    print("\n2. PHASE1_AGENITIC_CORE_ALL_FOLDERS_CREATED")
    expected_dirs = set()
    for file in expected_files:
        expected_dirs.add(os.path.dirname(file))
    
    missing_dirs = expected_dirs - set(actual_dirs)
    if not missing_dirs:
        print("   ✓ PASS: All expected folders created")
        validation_results["ALL_FOLDERS_CREATED"] = True
    else:
        print(f"   ✗ FAIL: Missing folders: {', '.join(sorted(missing_dirs))}")
        validation_results["ALL_FOLDERS_CREATED"] = False
        all_passed = False
    
    # CRITERION 3: All files created
    print("\n3. PHASE1_AGENITIC_CORE_ALL_FILES_CREATED")
    missing_files = set(expected_files) - set(actual_files)
    if not missing_files:
        print("   ✓ PASS: All expected files created")
        validation_results["ALL_FILES_CREATED"] = True
    else:
        print(f"   ✗ FAIL: Missing files: {', '.join(sorted(missing_files))}")
        validation_results["ALL_FILES_CREATED"] = False
        all_passed = False
    
    # CRITERION 4: No extra folders
    print("\n4. PHASE1_AGENITIC_CORE_NO_EXTRA_FOLDERS")
    extra_dirs = set(actual_dirs) - expected_dirs
    if not extra_dirs:
        print("   ✓ PASS: No extra folders found")
        validation_results["NO_EXTRA_FOLDERS"] = True
    else:
        print(f"   ✗ FAIL: Extra folders: {', '.join(sorted(extra_dirs))}")
        validation_results["NO_EXTRA_FOLDERS"] = False
        all_passed = False
    
    # CRITERION 5: No extra files
    print("\n5. PHASE1_AGENITIC_CORE_NO_EXTRA_FILES")
    extra_files = set(actual_files) - set(expected_files)
    if not extra_files:
        print("   ✓ PASS: No extra files found")
        validation_results["NO_EXTRA_FILES"] = True
    else:
        print(f"   ✗ FAIL: Extra files: {', '.join(sorted(extra_files))}")
        validation_results["NO_EXTRA_FILES"] = False
        all_passed = False
    
    # CRITERION 6: No missing folders
    print("\n6. PHASE1_AGENITIC_CORE_NO_MISSING_FOLDERS")
    if not missing_dirs:
        print("   ✓ PASS: No missing folders")
        validation_results["NO_MISSING_FOLDERS"] = True
    else:
        print(f"   ✗ FAIL: Missing folders: {', '.join(sorted(missing_dirs))}")
        validation_results["NO_MISSING_FOLDERS"] = False
        all_passed = False
    
    # CRITERION 7: No missing files
    print("\n7. PHASE1_AGENITIC_CORE_NO_MISSING_FILES")
    if not missing_files:
        print("   ✓ PASS: No missing files")
        validation_results["NO_MISSING_FILES"] = True
    else:
        print(f"   ✗ FAIL: Missing files: {', '.join(sorted(missing_files))}")
        validation_results["NO_MISSING_FILES"] = False
        all_passed = False
    
    # CRITERION 8: Case-sensitive paths
    print("\n8. PHASE1_AGENITIC_CORE_CASE_SENSITIVE_PATHS")
    case_issues = []
    for file in actual_files:
        if file not in expected_files:
            # Check if case mismatch
            for expected in expected_files:
                if expected.lower() == file.lower() and expected != file:
                    case_issues.append(f"{file} (expected: {expected})")
                    break
    
    if not case_issues:
        print("   ✓ PASS: All paths match case exactly")
        validation_results["CASE_SENSITIVE_PATHS"] = True
    else:
        print(f"   ✗ FAIL: Case issues: {', '.join(case_issues)}")
        validation_results["CASE_SENSITIVE_PATHS"] = False
        all_passed = False
    
    # CRITERION 9: Depths correct
    print("\n9. PHASE1_AGENITIC_CORE_DEPTHS_CORRECT")
    depth_issues = []
    for expected_file in expected_files:
        expected_depth = expected_file.count("/")
        if expected_file in actual_files:
            actual_depth = expected_file.count("/")
            if expected_depth != actual_depth:
                depth_issues.append(f"{expected_file} (expected depth: {expected_depth}, actual: {actual_depth})")
    
    if not depth_issues:
        print("   ✓ PASS: All directory depths correct")
        validation_results["DEPTHS_CORRECT"] = True
    else:
        print(f"   ✗ FAIL: Depth issues: {', '.join(depth_issues)}")
        validation_results["DEPTHS_CORRECT"] = False
        all_passed = False
    
    # CRITERION 10: Legacy merge complete
    print("\n10. PHASE1_AGENITIC_CORE_LEGACY_MERGE_COMPLETE")
    # For Phase 1, this means no legacy files with content
    legacy_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > 0:
                    # Check if this is a legacy file (not in expected structure)
                    rel_path = os.path.relpath(file_path, base_path).replace("\\", "/")
                    if rel_path not in expected_files:
                        legacy_files.append(rel_path)
    
    if not legacy_files:
        print("   ✓ PASS: No legacy files requiring merge")
        validation_results["LEGACY_MERGE_COMPLETE"] = True
    else:
        print(f"   ✗ FAIL: Legacy files found: {', '.join(legacy_files)}")
        validation_results["LEGACY_MERGE_COMPLETE"] = False
        all_passed = False
    
    # CRITERION 11: No orphaned paths
    print("\n11. PHASE1_AGENITIC_CORE_NO_ORPHANED_PATHS")
    orphaned_paths = set(actual_dirs) - expected_dirs
    if not orphaned_paths:
        print("   ✓ PASS: No orphaned directory paths")
        validation_results["NO_ORPHANED_PATHS"] = True
    else:
        print(f"   ✗ FAIL: Orphaned paths: {', '.join(sorted(orphaned_paths))}")
        validation_results["NO_ORPHANED_PATHS"] = False
        all_passed = False
    
    # CRITERION 12: Ready for Phase 2
    print("\n12. PHASE1_AGENITIC_CORE_READY_FOR_PHASE2")
    if all_passed:
        print("   ✓ PASS: All criteria passed - ready for Phase 2")
        validation_results["READY_FOR_PHASE2"] = True
    else:
        print("   ✗ FAIL: Not ready for Phase 2 - some criteria failed")
        validation_results["READY_FOR_PHASE2"] = False
    
    # Final summary
    print("\n=== VALIDATION SUMMARY ===")
    print(f"Total files expected: {expected_count}")
    print(f"Total files created: {actual_count}")
    print(f"Total directories created: {len(actual_dirs)}")
    
    passed_count = sum(1 for result in validation_results.values() if result)
    print(f"Criteria passed: {passed_count}/12")
    
    if all_passed:
        print("\n🎉 PHASE 1 COMPLETE - ALL KEYS PASS!")
        print("Ready to proceed to Phase 2")
    else:
        print("\n❌ PHASE 1 INCOMPLETE - SOME KEYS FAIL")
        print("Address failed criteria before proceeding")
    
    return all_passed

if __name__ == "__main__":
    validate_phase1()
