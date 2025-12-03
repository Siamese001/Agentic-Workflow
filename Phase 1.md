# =====================================================================
# PHASE 1 — STRUCTURAL ENFORCEMENT & NORMALIZATION (ZERO-LOSS)
# =====================================================================
# PURPOSE:
#   Ensure the live filesystem under <TARGET_ROOT>/ EXACTLY matches
#   the SSoT YAML structure — directory-by-directory, file-by-file,
#   with no deviations, no extras, no omissions.
#
#   Phase 1 performs ALL STRUCTURAL MUTATION:
#       • create    (missing YAML paths)
#       • delete    (obsolete FS paths)
#       • move      (misplaced FS paths)
#       • rename    (non-matching FS names)
#       • merge     (legacy folder structures)
#
#   Phase 1 NEVER edits code content (semantic mutation is Phase 3).
#
#   Phase 1 is NOT ATOMIC:
#       - All destructive/semantic operations will happen in Phase 3.
#       - Phase 1 is allowed to mutate the FS directly.
#
#   Phase 1 COMPLETES ONLY IF:
#       Canonical(FS) == Canonical(YAML)
#
#   If ANY difference exists → Phase 1 FAILS and must continue fixing.
# =====================================================================


# =====================================================================
# 1. PRECONDITIONS
# =====================================================================
K1:  PHASE_0_5_SEMANTIC_CACHE_EXISTS_BUT_NOT_REQUIRED == TRUE
K2:  EXECUTION_ENVIRONMENT_IS_DOCKER == TRUE
K3:  ROOT_STRUCTURE_IS_CANONICAL_10_FOLDERS == TRUE
K4:  UNIFIED_STRUCTURE_SUBATOMIC_YAML_EXISTS == TRUE
K4b: UNIFIED_STRUCTURE_SUBATOMIC_META_YAML_EXISTS == TRUE
K4c: UNIFIED_STRUCTURE_SUBATOMIC_META_YAML_PARSED == TRUE
K4d: COMBINED_SSoT = MERGE(SSoT_YAML, SSoT_META) == TRUE


# =====================================================================
# 2. LOAD & CANONICALIZE SSoT YAML
# =====================================================================
K5:  SSoT_YAML_PARSED_SUCCESSFULLY == TRUE
K6:  SSoT_YAML_SUBTREE_FOR_TARGET_ROOT_EXISTS == TRUE
K7:  SSoT_YAML_NORMALIZED(PATHS, ORDERING, DEPTH) == TRUE
K8:  SSoT_YAML_CANONICALIZED_TO_YAML_TREE == TRUE  # structure only
K8b: META_YAML_CANONICALIZED == TRUE
K8c: COMBINED_SSoT_CANONICALIZED == TRUE
K9:  YAML_DEPTH_LIMIT_NOT_EXCEEDED(<=7) == TRUE


# =====================================================================
# 3. SCAN & CANONICALIZE LIVE FILESYSTEM
# =====================================================================
K10: FS_SCAN_FOR_TARGET_ROOT_COMPLETES == TRUE
K11: FS_PATHS_NORMALIZED(UNIX_FORWARD_SLASH) == TRUE
K12: FS_EXCLUDES_SYSTEM_DIRS(".git",".venv","__pycache__",".mypy_cache") == TRUE
K13: FS_DEPTH_LIMIT_NOT_EXCEEDED(<=7) == TRUE
K14: FS_CANONICALIZED_TO_YAML_TREE == TRUE  # same normalization as SSoT


# =====================================================================
# 4. EXACT STRUCTURAL DIFF (SSoT vs FS)
# =====================================================================
K15: STRUCTURAL_DIFF_COMPUTED == TRUE
K16: YAML_ONLY_PATHS_IDENTIFIED == TRUE
K17: FS_ONLY_PATHS_IDENTIFIED == TRUE
K18: MISPLACED_PATHS_IDENTIFIED == TRUE
K19: NAME_MISMATCHES_IDENTIFIED == TRUE
K20: STRUCTURAL_DIFF_DETERMINISTICALLY_SORTED == TRUE


# =====================================================================
# 5. STRUCTURAL REPAIR ACTIONS
# =====================================================================
# Phase 1 is allowed to MUTATE structure (but NOT content).

K21: CREATE_DIR_FOR_ALL_YAML_ONLY_DIRS == TRUE
K22: CREATE_FILE_FOR_ALL_YAML_ONLY_FILES == TRUE

K23: DELETE_DIR_FOR_ALL_FS_ONLY_DIRS == TRUE
K24: DELETE_FILE_FOR_ALL_FS_ONLY_FILES == TRUE

K25: MOVE_OR_RENAME_PATHS_TO_MATCH_YAML == TRUE
K26: MERGE_LEGACY_FOLDERS_INTO_YAML_LOCATIONS == TRUE
K27: COLLISION_FREE_MOVES_ONLY == TRUE

K28: NO_CONTENT_EDITING_OCCURS == TRUE
K29: NO_SEMANTIC_REWRITE_OCCURS == TRUE
K30: NO_LAYER_OR_ENGINE_ROLE_CHANGES_OCCUR == TRUE

# Protected paths are allowed pre-Phase 3 to be moved or renamed ONLY
# IF YAML structure requires it; code rewrite still forbidden here.
K31: PROTECTED_PATHS_CAN_BE_RESTRUCTURED_IF_YAML_REQUIRES == TRUE
K32: PROTECTED_PATHS_MUST_NOT_BE_DELETED == TRUE


# =====================================================================
# 6. CANONICALIZE FS AGAIN AFTER FIXES
# =====================================================================
K33: POST_REPAIR_FS_CANONICALIZED == TRUE
K34: POST_REPAIR_FS_NORMALIZED == TRUE


# =====================================================================
# 7. STRICT STRUCTURAL MATCH VALIDATION
# =====================================================================
# The ONLY signal that Phase 1 is complete:
# Byte-for-byte equality between the canonical SSoT YAML tree and the
# canonical filesystem YAML tree.

# Phase 1 strict match:
K35: CANONICAL_FS_TREE_GENERATED == TRUE
K36: CANONICAL_COMBINED_SSoT_TREE_GENERATED == TRUE
K37: BYTE_FOR_BYTE_EQUAL(CANONICAL_FS_TREE, CANONICAL_COMBINED_SSoT_TREE) == TRUE


# =====================================================================
# 8. ZERO-LOSS & BOUNDARY SAFETY
# =====================================================================
K38: NO_CHANGES_OUTSIDE_TARGET_ROOT == TRUE
K39: NO_WRITES_TO_REPO_ROOT == TRUE
K40: NO_UNEXPECTED_FILES_OR_DIRS_IN_ROOT == TRUE
K41: ZERO-LOSS_GUARANTEED_FOR_PROTECTED_PATHS == TRUE
K42: NO_SEMANTIC_CACHE_WRITES_IN_PHASE_1 == TRUE


# =====================================================================
# 9. COMPLETION GATE
# =====================================================================
K43: STRUCTURAL_DIFF == EMPTY_SET == TRUE
K44: FINAL_FS_STRUCTURE_MATCHES_SSoT_TREE == TRUE
K45: ALL_KEYS_K1_TO_K44_PASS == TRUE

# =====================================================================
# END OF PHASE 1
# =====================================================================
