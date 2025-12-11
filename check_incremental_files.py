import sys

# --- USER-PROVIDED INPUTS ---

# List 1: Basenames of all Python files in the current Sovereign Codebase (the files we MUST NOT overwrite).
# Format: ['fileA.py', 'helper_util.py', ...]
SOVEREIGN_EXCLUSION_LIST = [
    'fix_canon_violations.py',
    'docstring_debt.py',
    '__init__.py',
    'verify_installation.py',
    'shared_utilities.py',
    'test_utils.py',
    'test_security_controls.py',
    'test_runtime_ops.py',
    'test_pipeline_ops.py',
    'test_logic_ops.py',
    'test_cache_ops.py',
    'test_scripts.py',
    'test_planning_schema_validation.py',
    'test_models.py',
    'test_memory_schema_validation.py',
    'test_multi_provider_clients.py',
    'test_cache_regression.py',
    'test_cache.py',
    'test_prompt_governance.py',
    'test_observability.py',
    'validate_safety_ethics.py',
    'update_update_safety_usage.py',
    'update_track_safety_cost.py',
    'update_enforce_safety_budget.py',
    'state_update_safety_usage.py',
    'safety_validate_safety_ethics.py',
    'safety_enforce_safety_filters.py',
    'enforce_safety_filters.py',
    'che_update_track_safety_cost.py',
    'che_update_enforce_safety_budget.py',
    'validate-phase-group_retrieval-ops.py',
    'validate-phase-group.py',
    'expand-phase-group_vectorization-ops.py',
    'expand-phase-group.py',
    'route-phase-group.py',
]

# List 2: Basenames of all Python files in the archive folder: 
# C:\Git\Agentic-Workflow\archives\engines\legacy_engines (the files we want to check and potentially copy).
# Format: ['Legacy_Engine.py', 'old_util.py', ...]
ARCHIVE_SOURCE_LIST = [
    'constitutional_ai_system.py',
    'content_quality_enhancements.py',
    'enhanced_semantic_cache.py',
    'enhancement_demo.py',
    'goal_alignment_engine.py',
    'hybrid_scoring.py',
    'intelligence_bundles.py',
    'lic_demo.py',
    'lic_retrieval_demo.py',
    'hardening_demo.py',
    'enhanced_orchestrator.py',
    'fusion_planner.py',
    'grounding_planner.py',
    'insights_engine.py',
    'rag_pipeline.py',
    'research_planner.py',
    'retrieval_hardening.py',
    'lic_profile_planner.py',
    'lic_rag.py',
    'lic_research_planner.py',
    'meta_learning_system.py',
    'retrieval_enhancements.py',
    'rg_orchestrator.py',
    'rg_planner.py',
    'rg_state.py',
    'safety_enhancements.py',
]

# ----------------------------

# --- Hardened Logic for Incremental Check ---

# 1. Create a hardened, case-insensitive exclusion set
hardened_exclusion_set = {f.lower() for f in SOVEREIGN_EXCLUSION_LIST}

# 2. Perform the case-insensitive comparison
net_incremental_files = []
duplicates_found = []

for archive_file in ARCHIVE_SOURCE_LIST:
    # Hardening: Check the lowercase version of the archive file against the exclusion set
    if archive_file.lower() not in hardened_exclusion_set:
        # File is NET INCREMENTAL NEW CODE
        net_incremental_files.append(archive_file)
    else:
        # File is a DUPLICATE and MUST be skipped (Hardened logic prevents copy)
        duplicates_found.append(archive_file)

# --- Reporting ---

if net_incremental_files:
    print("\n✅ SUCCESS: NET INCREMENTAL FILES IDENTIFIED (Ready for Staging)")
    print(f"Total files to be moved to /archive_code/: {len(net_incremental_files)}")
    print("--- Incremental Files List ---")
    for filename in net_incremental_files:
        print(f"- {filename}")
    print("\nNext Action: Manually copy these files into the /archive_code/ staging folder.")
else:
    print("\n✅ SUCCESS: NO NET INCREMENTAL FILES FOUND.")
    print("All files in the legacy archive are already present in the current sovereign codebase (duplicates).")

if duplicates_found:
    print("\n--- Duplicates Skipped (Hardened Check Confirmed) ---")
    for filename in duplicates_found:
        print(f"- {filename}")

# Exit cleanly
sys.exit(0)
