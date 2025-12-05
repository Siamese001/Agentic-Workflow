# =====================================================================

# PHASE 3 — ATOMIC STRUCTURAL + CODE REWRITE EXECUTION (ZERO-LOSS)

# =====================================================================

# PURPOSE:

#   Execute the unified migration + rewrite plan created in Phase 2.
#

#   Phase 3 MUST:

#       • Apply ALL structural filesystem changes

#       • Apply ALL code rewrite operations using FULL semantic cache:
#

#           06_data/semantic_cache/

#               resume_engine/

#               outreach_engine/

#               agentic_core/

#               schemas/

#               runtime/

#               prompt_governance/

#               config/

#               data_source/

#               observability/

#               scripts/

#               apps/

#               tests/

#               ast/

#               diffs/

#               embeddings/

#               meta/

#               safety/

#               golden/

#               integrity/
#

#   Phase 3 is the ONLY destructive phase.

#   Phase 3 MUST be fully ATOMIC with rollback.
#

#   Phase 3 MUST be runnable STANDALONE with ONLY:

#       - SSoT YAML

#       - Normalized FS (Phase 1 result)

#       - Phase 2 plan

#       - Phase 0.5 semantic cache

# =====================================================================

# =====================================================================

# 0. GLOBAL PATHS & TARGETS (CANONICAL)

# =====================================================================

# Project root must contain EXACTLY:

#   01_agentic_core/

#   02_schemas/

#   03_runtime/

#   04_prompt_governance/

#   05_config/

#   06_data/

#   07_observability/

#   08_scripts/

#   09_apps/

#   10_tests/

#   unified_structure_subatomic.yaml
#

# SEMANTIC CACHE ROOT:

#   06_data/semantic_cache/

# SEMANTIC-LINEAGE BUCKETS:

#   06_data/semantic_cache/resume_engine/

#   06_data/semantic_cache/outreach_engine/

#   06_data/semantic_cache/agentic_core/

#   06_data/semantic_cache/schemas/

#   06_data/semantic_cache/runtime/

#   06_data/semantic_cache/prompt_governance/

#   06_data/semantic_cache/config/

#   06_data/semantic_cache/data_source/

#   06_data/semantic_cache/observability/

#   06_data/semantic_cache/scripts/

#   06_data/semantic_cache/apps/

#   06_data/semantic_cache/tests/
#

# GLOBAL SEMANTIC ARTIFACTS:

#   06_data/semantic_cache/ast/

#   06_data/semantic_cache/embeddings/

#   06_data/semantic_cache/diffs/

#   06_data/semantic_cache/meta/

#   06_data/semantic_cache/safety/

#   06_data/semantic_cache/golden/

#   06_data/semantic_cache/integrity/
#

# PLAN PATH:

#   02_schemas/<TARGET_ROOT>_migration_and_rewrite_plan.json

# =====================================================================

# =====================================================================

# 1. PRECONDITIONS & STATE VALIDATION

# =====================================================================

K1:  EXECUTION_ENVIRONMENT_IS_DOCKER == TRUE
K2:  ROOT_STRUCTURE_IS_CANONICAL_10_FOLDERS == TRUE
K3:  UNIFIED_STRUCTURE_SUBATOMIC_YAML_EXISTS == TRUE
K3b: UNIFIED_STRUCTURE_SUBATOMIC_META_YAML_EXISTS == TRUE
K3c: UNIFIED_STRUCTURE_SUBATOMIC_META_PARSED == TRUE
K3d: COMBINED_SSoT_CANONICAL == TRUE

K4:  PHASE_1_COMPLETED_SUCCESSFULLY == TRUE
K5:  PHASE_2_COMPLETED_SUCCESSFULLY == TRUE

K6:  FS_STRUCTURE_MATCHES_SSoT_EXACTLY_AT_ENTRY == TRUE

# Semantic-cache availability for the specific root:

K7:  SEMANTIC_CACHE_ROOT_EXISTS == TRUE
K8:  SEMANTIC_CACHE_BUCKET_FOR_TARGET_ROOT_EXISTS == TRUE

# Global semantic artifacts MUST exist:

K9:  SEMANTIC_CACHE_SUBDIR_EXISTS("ast") == TRUE
K10: SEMANTIC_CACHE_SUBDIR_EXISTS("golden") == TRUE
K11: SEMANTIC_CACHE_SUBDIR_EXISTS("diffs") == TRUE
K12: SEMANTIC_CACHE_SUBDIR_EXISTS("meta") == TRUE
K13: SEMANTIC_CACHE_SUBDIR_EXISTS("integrity") == TRUE
K14: SEMANTIC_CACHE_SUBDIR_EXISTS("embeddings") == TRUE
K15: SEMANTIC_CACHE_SUBDIR_EXISTS("safety") == TRUE

K16: TARGET_ROOT in {01...10} == TRUE
K17: PLAN_FILE_EXISTS == TRUE
K18: PLAN_FILE_IS_VALID_JSON == TRUE

# =====================================================================

# 2. PLAN VALIDATION (STRICT)

# =====================================================================

K19: PLAN_SCHEMA_VERSION == "v1"
K20: PLAN_TARGET_ROOT == "<TARGET_ROOT>/"
K21: PLAN_MODE == "semantic_structural_unified"
K22: PLAN_HAS_OPERATIONS == TRUE
K23: OPERATIONS_IS_ARRAY == TRUE
K24: PLAN_HAS_SUMMARY == TRUE

K25: EVERY_OPERATION_HAS_TYPE == TRUE
K26: EVERY_OP_TYPE_IN_ALLOWED_SET({
        "create_dir","create_file",
        "delete_dir","delete_file",
        "move_path","rename_path",
        "rewrite_file_from_cache",
        "merge_file_from_cache",
        "patch_region_from_cache",
        "insert_semantic_block",
        "delete_semantic_block",
        "canonical_rewrite",
        "noop"
     }) == TRUE

K27: EACH_OPERATION_RELATIVE_TO_TARGET_ROOT == TRUE
K28: OP_PATHS_USE_FORWARD_SLASH == TRUE
K29: NO_OP_PATH_IS_ABSOLUTE == TRUE
K30: NO_OP_PATH_HAS_RANDOMNESS == TRUE
K31: OPERATION_ORDER_IS_CANONICAL == TRUE

# =====================================================================

# 3. PROTECTED PATHS MODEL

# =====================================================================

# Protected paths CANNOT be deleted, moved, renamed.

# They CAN be rewritten (content only).

K32: PROTECTED_PATH_PATTERNS_DEFINED == TRUE
K32b: PROTECTED_PATHS_IN_META_APPLIED == TRUE
K33: PATTERN(**/__init__.py) INCLUDED == TRUE
K34: PROTECTED_PATHS_EXPANDED == TRUE
K35: PROTECTED_PATHS_NORMALIZED == TRUE

K36: NO_OP_DELETES_PROTECTED_PATH == TRUE
K37: NO_OP_MOVES_PROTECTED_PATH == TRUE
K38: NO_OP_RENAMES_PROTECTED_PATH == TRUE
K39: CONTENT_REWRITE_ALLOWED_FOR_PROTECTED == TRUE

# =====================================================================

# 4. SEMANTIC CACHE RESOLUTION — STRICT LINKAGE

# =====================================================================

K40: EACH_SEMANTIC_OP_REFERENCES_EXISTING_CACHE == TRUE

# Full-file rewrite must find:

K41: FOR_EACH_rewrite_file_from_cache:
        golden_exists_in(06_data/semantic_cache/golden/) == TRUE

# Merge rewrite must find diff or golden:

K42: FOR_EACH_merge_file_from_cache:
        diff_or_golden_exists == TRUE

# Patch operations must reference AST or diff:

K43: FOR_EACH_patch_region_from_cache:
        ast_or_diff_exists == TRUE

# Block operations rely on AST canonical boundaries:

K44: semantic_boundary_metadata_exists == TRUE

K45: NO_SEMANTIC_OP_REFERENCES_OUTSIDE_CACHE == TRUE
K46: NO_SEMANTIC_OP_TRIGGERS_LLM_OR_NETWORK == TRUE

# =====================================================================

# 5. ATOMIC EXECUTION ENGINE (SNAPSHOT + ROLLBACK)

# =====================================================================

K47: ATOMIC_ENGINE_INITIALIZED == TRUE
K48: SNAPSHOT_CREATED == TRUE
K49: SNAPSHOT_STORED_OUTSIDE_TARGET_ROOT == TRUE
K50: SNAPSHOT_CONTAINS_FULL_DIRECTORY_TREE == TRUE
K51: SNAPSHOT_INCLUDES_PERMISSIONS == TRUE
K52: SNAPSHOT_INCLUDES_TIMESTAMPS == TRUE

K53: TRANSACTION_LOG_INITIALIZED == TRUE
K54: EVERY_MUTATION_LOGGED == TRUE

K55: ROLLBACK_ENGINE_READY == TRUE
K56: ANY_FAILURE_TRIGGERS_FULL_ROLLBACK == TRUE
K57: ROLLBACK_RESTORES_ALL_FILES == TRUE
K58: ROLLBACK_RESTORES_ALL_DIRS == TRUE
K59: ROLLBACK_RESTORES_PERMISSIONS == TRUE
K60: ROLLBACK_RESTORES_TIMESTAMPS == TRUE

# =====================================================================

# 6. PRECOMMIT VERIFICATION (BEFORE ANY CHANGE)

# =====================================================================

K61: PRECOMMIT_VERIFICATION_RUN_USING_COMBINED_SSoT == TRUE
K62: FS_RESCAN_MATCHES_SSoT == TRUE
K63: NO_PATH_COLLISIONS == TRUE
K64: NO_DEPTH_LIMIT_VIOLATION(<=7) == TRUE
K65: NO_PROTECTED_PATH_VIOLATIONS == TRUE
K66: ALL_CACHE_REFERENCES_STILL_EXIST == TRUE
K67: PRECOMMIT_FAILURE_ABORTS_IMMEDIATELY == TRUE

# =====================================================================

# 7. STRUCTURAL EXECUTION

# =====================================================================

# Creation:

K68: CREATE_DIR_OPS_ONLY_CREATE_NEW_DIRS == TRUE
K69: CREATE_FILE_OPS_CREATE_EMPTY_FILE == TRUE
K70: CREATE_FILE_OPS_NEVER_OVERWRITE_EXISTING == TRUE

# Deletion:

K71: DELETE_FILE_OPS_MATCH_PLAN == TRUE
K72: DELETE_FILE_OPS_NEVER_TOUCH_PROTECTED == TRUE
K73: DELETE_DIR_OPS_APPLY_ONLY_TO_EMPTY_OR_FLAGGED == TRUE
K74: DELETE_DIR_OPS_NEVER_TOUCH_PROTECTED_PARENTS == TRUE

# Movement:

K75: MOVE_OPS_PRESERVE_BYTES_AND_PERMISSIONS == TRUE
K76: MOVE_OPS_NOT_APPLIED_TO_PROTECTED == TRUE

# Rename:

K77: RENAME_OPS_PRESERVE_EXTENSION == TRUE
K78: RENAME_OPS_NEVER_TOUCH_PROTECTED == TRUE

# Logging:

K79: ALL_STRUCTURAL_OPS_LOGGED == TRUE

# =====================================================================

# 8. CODE REWRITE EXECUTION — SEMANTIC OPERATIONS

# =====================================================================

# Full-file rewrite (canonical overwrite using golden form)

K80: REWRITE_OP_USES_EXACT_GOLDEN_CONTENT == TRUE
K81: REWRITE_OP_IDEMPOTENT == TRUE

# Merge:

K82: MERGE_OP_APPLIES_DETERMINISTICALLY == TRUE
K83: MERGE_OP_PRESERVES_NON_CONFLICTING_LINES == TRUE
K84: MERGE_CONFLICT → TRIGGER_ROLLBACK == TRUE

# AST patch:

K85: PATCH_REGION_OP_BOUND_TO_CANONICAL_AST_RANGES == TRUE
K86: PATCH_REGION_OP_MAINTAINS_SYNTAX == TRUE

# Insert/delete semantic blocks:

K87: INSERT_BLOCK_OP_PLACES_AT_CANONICAL_LOCATION == TRUE
K88: DELETE_BLOCK_OP_REMOVES_ONLY_INTENDED_REGION == TRUE

# Golden canonical rewrite:

K89: CANONICAL_REWRITE_OP_REPLACES_WITH_GOLDEN == TRUE
K90: CANONICAL_REWRITE_OP_VERIFIED_FOR_SYNTAX == TRUE

# Safety:

K91: NO_SEMANTIC_OP_EXECUTES_TARGET_CODE == TRUE
K92: ALL_CODE_OPS_LOGGED == TRUE

# =====================================================================

# 9. SAFETY AGAINST CROSS-ROOT MUTATION

# =====================================================================

K93: NO_MUTATION_OUTSIDE_TARGET_ROOT == TRUE
K94: NO_WRITES_TO_REPO_ROOT == TRUE
K95: NO_WRITES_TO_SEMANTIC_CACHE == TRUE
K96: NO_WRITES_TO_OTHER_ROOTS == TRUE
K97: ONLY_EXECUTION_REPORTS_WRITTEN_OUTSIDE_TARGET_ROOT == TRUE

# =====================================================================

# 10. PURITY & DETERMINISM

# =====================================================================

K98: NO_LLM_CALLS == TRUE
K99: NO_NETWORK_CALLS == TRUE
K100: NO_DYNAMIC_CODE_EVAL == TRUE
K101: NO_RANDOMNESS == TRUE
K102: NO_TIME_DEPENDENCE == TRUE
K103: REPEATED_EXECUTION_WITH_SAME_PLAN → NO_OP == TRUE

# =====================================================================

# 11. POSTCOMMIT VERIFICATION (AFTER SUCCESSFUL EXECUTION)

# =====================================================================

K104: POSTCOMMIT_RUNS == TRUE
K105: POSTCOMMIT_RESCAN_MATCHES_SSoT == TRUE
K106: PROTECTED_PATHS_PRESENT == TRUE
K107: NO_EXTRA_PATHS == TRUE
K108: NO_MISSING_PATHS == TRUE
K109: NO_MUTATIONS_OUTSIDE_TARGET_ROOT == TRUE
K110: POSTCOMMIT_HASH_TREE_MATCHES_PLAN == TRUE   # new requirement

# =====================================================================

# 12. EXECUTION REPORTING (MANDATORY)

# =====================================================================

K111: REPORT_WRITTEN_TO("06_data/meta/") == TRUE
K112: REPORT_SUMMARY_INCLUDES_OPERATION_COUNTS == TRUE
K113: REPORT_INCLUDES_ROLLBACK_STATUS == TRUE
K114: REPORT_CONTAINS_NO_SOURCE_SNIPPETS == TRUE
K115: REPORT_IDEMPOTENT == TRUE

# =====================================================================

# 13. COMPLETION GATE

# =====================================================================

K116: NO_ROLLBACK_OCCURRED == TRUE
K117: FINAL_FS_MATCHES_SSoT == TRUE
K118: FINAL_CODE_MATCHES_PLAN_INTENT == TRUE
K119: ALL_KEYS_K1_TO_K118_PASS == TRUE

# =====================================================================

# END PHASE 3 — ZERO-LOSS OVERWRITE

# =====================================================================
