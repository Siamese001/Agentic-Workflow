# =====================================================================
# PHASE 2 — SEMANTIC STRUCTURAL & CODE DIFF PLANNING (ZERO-LOSS)
# =====================================================================
# PURPOSE:
#   Produce a COMPLETE, DETERMINISTIC migration + rewrite plan combining:
#
#      1. Structural DIFF (FS ↔ SSoT YAML)
#      2. Semantic DIFF (FS code ↔ Full Phase 0.5 Semantic Cache)
#
#   Phase 2 performs NO mutations. It only outputs:
#
#     02_schemas/<TARGET_ROOT>_migration_and_rewrite_plan.json
#
#   Phase 3 will consume this plan.
# =====================================================================


# =====================================================================
# 0. REQUIRED SEMANTIC CACHE LAYOUT (PHASE 0.5 v2)
# =====================================================================
# Phase 2 MUST use the following directories built by Phase 0.5:
#
#   06_data/semantic_cache/
#       resume_engine/
#       outreach_engine/
#       agentic_core/
#       schemas/
#       runtime/
#       prompt_governance/
#       config/
#       data_source/
#       observability/
#       scripts/
#       apps/
#       tests/
#
#   GLOBAL semantic objects:
#       06_data/semantic_cache/ast/*.ast
#       06_data/semantic_cache/embeddings/*.embedding
#       06_data/semantic_cache/diffs/*.diff.json
#       06_data/semantic_cache/golden/*.golden.json
#       06_data/semantic_cache/safety/*.safety.json
#       06_data/semantic_cache/integrity/*.integrity.json
#       06_data/semantic_cache/meta/*.meta.json
#
# Every file in <TARGET_ROOT> *must* have corresponding semantic-cache
# lineage artifacts in its matching lineage directory.
# =====================================================================


# =====================================================================
# 1. PRECONDITIONS
# =====================================================================
K1:  PHASE_1_COMPLETED_SUCCESSFULLY == TRUE
K2:  FS_STRUCTURE_MATCHES_SSoT_EXACTLY == TRUE

# CRITICAL NEW BEHAVIOR:
# Phase 2 now REQUIRES the full 10-folder semantic cache from Phase 0.5.
K3:  SEMANTIC_CACHE_EXISTS_FOR_TARGET_ROOT == TRUE
K4:  SEMANTIC_CACHE_HEALTHY_FOR_TARGET_ROOT == TRUE

K5:  EXECUTION_ENVIRONMENT_IS_DOCKER == TRUE
K6:  ROOT_STRUCTURE_IS_CANONICAL_10_FOLDERS == TRUE
K7:  SEMANTIC_CACHE_GLOBAL_BUCKETS_PRESENT == TRUE   # ast/, diffs/, etc.


# =====================================================================
# 2. LOAD ALL VIEWS (SSoT, FS, SEMANTIC)
# =====================================================================
K8:  SSoT_YAML_LOADED_AND_VALID == TRUE
K9:  SSoT_YAML_SUBTREE_FOR_TARGET_ROOT_EXISTS == TRUE
K10: FS_STRUCTURE_LOADED_AND_NORMALIZED == TRUE

# SEMANTIC CACHE LOADING — NOW FULLY FOLDER-AWARE
K11: SEMANTIC_CACHE_LOADED_READONLY == TRUE
K12: SEMANTIC_CACHE_FOR_TARGET_ROOT_LOADED == TRUE        # e.g. agentic_core/
K13: GLOBAL_SEMANTIC_OBJECTS_LOADED == TRUE               # ast/, diffs/, etc.
K14: SEMANTIC_CACHE_PATHS_NORMALIZED == TRUE
K15: FS_AND_CACHE_PATHS_SHARE_CANONICAL_RELATIVE_PREFIX == TRUE

K16: NO_SYSTEM_DIRS_INCLUDED == TRUE


# =====================================================================
# 3. STRUCTURAL DIFF (SSoT ↔ FS)
# =====================================================================
# These must be empty because Phase 1 already enforced structure.
K17: YAML_ONLY_DIRS_IDENTIFIED == TRUE
K18: YAML_ONLY_FILES_IDENTIFIED == TRUE
K19: FS_ONLY_DIRS_IDENTIFIED == TRUE
K20: FS_ONLY_FILES_IDENTIFIED == TRUE
K21: MISPLACED_PATHS_IDENTIFIED == TRUE
K22: NAME_MISMATCHES_IDENTIFIED == TRUE
K23: STRUCTURAL_DIFF_SETS_SORTED == TRUE

K24: STRUCTURAL_DIFF_SET_EMPTY == TRUE   # MUST BE TRUE OR PHASE 2 FAILS


# =====================================================================
# 4. SEMANTIC DIFF (SEMANTIC CACHE ↔ LIVE CODE)
# =====================================================================
# Every file in <TARGET_ROOT> must have:
#   • <relative_path>.ast
#   • <relative_path>.embedding
#   • <relative_path>.diff.json
#   • <relative_path>.golden.json
#   • <relative_path>.safety.json
#   • <relative_path>.integrity.json
#   • global copies (via hash)
#
# Phase 2 compares LIVE code ←→ Phase 0.5 semantic lineage.

K25: FOR_EACH_FILE_AST_LOADED == TRUE
K26: FOR_EACH_FILE_EMBEDDING_LOADED == TRUE
K27: FOR_EACH_FILE_DIFF_LOADED == TRUE
K28: FOR_EACH_FILE_GOLDEN_LOADED == TRUE
K29: FOR_EACH_FILE_INTEGRITY_LOADED == TRUE

K30: AST_DIFF_FOR_EACH_FILE_COMPUTED == TRUE
K31: EMBEDDING_DISTANCE_COMPUTED == TRUE
K32: GOLDEN_DIFF_COMPUTED == TRUE
K33: TOOL_USAGE_DIFFS_IDENTIFIED == TRUE
K34: BEHAVIOR_DIFFS_IDENTIFIED == TRUE
K35: L1_L5_LAYER_MISMATCHES_IDENTIFIED == TRUE

K36: SEMANTIC_DIFFS_SORTED_CANONICALLY == TRUE


# =====================================================================
# 5. COMPOSITE SEMANTIC INTENT (STRUCT + CODE)
# =====================================================================
# Phase 2 must compute EVERY kind of operation Phase 3 may execute.

K37: STRUCTURAL_REPAIR_INTENT_COMPUTED == TRUE
K38: CODE_REWRITE_INTENT_COMPUTED == TRUE
K39: CODE_MERGE_INTENT_COMPUTED == TRUE
K40: CODE_PATCH_REGION_INTENT_COMPUTED == TRUE
K41: CODE_DELETE_INTENT_COMPUTED_IF_SAFE == TRUE
K42: CODE_CREATE_INTENT_COMPUTED_IF_REQUIRED == TRUE

# Full deterministic ordering:
K43: SEMANTIC_INTENT_IS_DETERMINISTIC == TRUE


# =====================================================================
# 6. UNIFIED PLAN GENERATION
# =====================================================================
PLAN_PATH:
   "02_schemas/<TARGET_ROOT>_migration_and_rewrite_plan.json"

K44: PLAN_PATH_VALID == TRUE
K45: PLAN_FILE_WRITABLE == TRUE

K46: PLAN_WRITTEN_AS_VALID_JSON_OBJECT == TRUE

# Required top-level fields:
K47: PLAN_HAS_FIELD("schema_version") == TRUE
K48: PLAN_SCHEMA_VERSION == "v1"
K49: PLAN_HAS_FIELD("target_root") == TRUE
K50: PLAN_TARGET_ROOT == "<TARGET_ROOT>/"
K51: PLAN_HAS_FIELD("mode") == TRUE
K52: PLAN_MODE == "semantic_structural_unified"
K53: PLAN_HAS_FIELD("operations") == TRUE
K54: OPERATIONS_ARRAY_IS_EMPTY_OR_LIST == TRUE
K55: PLAN_HAS_FIELD("summary") == TRUE

# Operation types allowed:
K56: ALLOWED_STRUCTURAL_OPS = {
        "create_dir", "create_file",
        "delete_dir", "delete_file",
        "move_path", "rename_path"
     } == TRUE

K57: ALLOWED_SEMANTIC_OPS = {
        "rewrite_file_from_cache",    # full-file replacement via golden
        "merge_file_from_cache",      # structural merge via .diff.json
        "patch_region_from_cache",    # precise AST region replacement
        "insert_semantic_block",
        "delete_semantic_block",
        "canonical_rewrite"           # overwrite with golden canonical
     } == TRUE

K58: ALL_OP_TYPES_IN_PLAN_ARE_ALLOWED == TRUE


# =====================================================================
# 7. OPERATION PATH RULES
# =====================================================================
K59: ALL_OP_PATHS_RELATIVE_TO_TARGET_ROOT == TRUE
K60: ALL_OP_PATHS_USE_FORWARD_SLASH == TRUE
K61: NO_OP_CONTAINS_ABSOLUTE_OR_HOST_PATH == TRUE
K62: NO_OP_CONTAINS_TIMESTAMP_OR_RANDOMNESS == TRUE
K63: OPERATION_ORDERING_IS_CANONICAL == TRUE


# =====================================================================
# 8. PROTECTED PATH RULES
# =====================================================================
K64: PROTECTED_PATHS_LIST_DEFINED == TRUE
K65: NO_OP_DELETES_PROTECTED_PATH == TRUE
K66: NO_OP_MOVES_OR_RENAMES_PROTECTED_PATH == TRUE
K67: REWRITE_OPS_FOR_PROTECTED_PATHS_ALLOWED == TRUE
K68: PLAN_FAILS_IF_PROTECTED_PATH_STRUCTURALLY_REMOVED == TRUE


# =====================================================================
# 9. NO SIDE EFFECTS (IMMUTABLE PHASE)
# =====================================================================
K69: PHASE_2_DOES_NOT_MUTATE_FS == TRUE
K70: PHASE_2_DOES_NOT_MUTATE_CODE == TRUE
K71: PHASE_2_DOES_NOT_MUTATE_SEMANTIC_CACHE == TRUE
K72: PHASE_2_DOES_NOT_TOUCH_OTHER_ROOTS == TRUE
K73: NO_WRITES_TO_REPO_ROOT == TRUE


# =====================================================================
# 10. PURE + DETERMINISTIC EXECUTION
# =====================================================================
K74: NO_LLM_CALLS_IN_PHASE_2 == TRUE
K75: NO_NETWORK_CALLS_IN_PHASE_2 == TRUE
K76: NO_EXECUTION_OF_TARGET_CODE == TRUE
K77: NO_RANDOMNESS_USED_IN_PLAN == TRUE
K78: NO_TIME_DEPENDENCE_USED_IN_PLAN == TRUE
K79: REPEATED_2_PRODUCES_BIT_IDENTICAL_PLAN == TRUE


# =====================================================================
# 11. SUMMARY CHECK
# =====================================================================
K80: SUMMARY_COUNTS_MATCH_OPERATION_LIST == TRUE
K81: SUMMARY_INCLUDES_STRUCTURAL_COUNTS == TRUE
K82: SUMMARY_INCLUDES_CODE_REWRITE_COUNTS == TRUE
K83: SUMMARY_DOES_NOT_CONTAIN_SOURCE_CONTENT == TRUE


# =====================================================================
# 12. COMPLETION GATE
# =====================================================================
# All must pass:
K84: PLAN_VALID == TRUE
K85: STRUCTURAL_DIFF_EMPTY == TRUE
K86: SEMANTIC_INTENT_COMPUTED == TRUE
K87: SEMANTIC_CACHE_LINKAGE_CONFIRMED == TRUE
K88: ALL_KEYS_K1_TO_K87_PASS == TRUE

# =====================================================================
# END — PHASE 2 (ZERO-LOSS, SEMANTIC-CACHE-ENABLED EDITION)
# =====================================================================

