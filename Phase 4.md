# =====================================================================
# PHASE 4 — CRYPTOGRAPHIC FREEZE (ZERO-LOSS OVERWRITE)
# =====================================================================
# PURPOSE:
#   Produce a deterministic, machine-verifiable cryptographic snapshot of
#   the post-Phase-3 tree under <TARGET_ROOT>/ by hashing:
#       • all file paths (relative)
#       • all file contents (sha256)
#       • all file sizes (bytes)
#
#   and writing a SINGLE freeze report INSIDE <TARGET_ROOT>/ ONLY.
#
#   Phase 4 MUST:
#       • perform NO structural mutation
#       • perform NO code mutation
#       • never touch semantic cache contents
#       • be fully deterministic and reproducible
#
#   Phase 4 MUST be runnable standalone given:
#       • SSoT YAML (unified_structure_subatomic.yaml)
#       • final FS state after Phase 3
# =====================================================================


# =====================================================================
# 0. GLOBAL PATHS & CONTEXT
# =====================================================================
# Project root structure (inside Docker container):
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
# Semantic cache root (read-only in Phase 4):
#   06_data/semantic_cache/
#
# Target root example:
#   <TARGET_ROOT>/ == "01_agentic_core/", "03_runtime/", etc.
#
# Freeze report path for <TARGET_ROOT>/:
#   <TARGET_ROOT>/<TARGET_ROOT>_freeze_report.json
#   e.g. 01_agentic_core/agentic_core_freeze_report.json
# =====================================================================


# =====================================================================
# 1. PRECONDITIONS
# =====================================================================
K1:  EXECUTION_ENVIRONMENT_IS_DOCKER == TRUE
K2:  ROOT_STRUCTURE_IS_CANONICAL_10_FOLDERS == TRUE
K3:  UNIFIED_STRUCTURE_SUBATOMIC_YAML_EXISTS == TRUE

K4:  PHASE_1_COMPLETED_SUCCESSFULLY == TRUE
K5:  PHASE_2_COMPLETED_SUCCESSFULLY == TRUE
K6:  PHASE_3_COMPLETED_SUCCESSFULLY == TRUE

K7:  FS_STRUCTURE_MATCHES_SSoT_EXACTLY_AT_ENTRY == TRUE
K8:  TARGET_ROOT_IN({
        "01_agentic_core","02_schemas","03_runtime","04_prompt_governance",
        "05_config","06_data","07_observability","08_scripts","09_apps","10_tests"
     }) == TRUE


# =====================================================================
# 2. ROOT & SCOPE IMMUTABILITY (PHASE 4)
# =====================================================================
K9:  PHASE_4_WRITES_ONLY_TO_TARGET_ROOT_FREEZE_REPORT == TRUE
K10: PHASE_4_CREATES_NO_OTHER_FILES_UNDER_TARGET_ROOT == TRUE
K11: PHASE_4_CREATES_NO_DIRECTORIES_UNDER_TARGET_ROOT == TRUE
K12: PHASE_4_DELETES_NO_FILES_UNDER_TARGET_ROOT == TRUE
K13: PHASE_4_RENAMES_NO_FILES_OR_DIRS_UNDER_TARGET_ROOT == TRUE
K14: PHASE_4_MAKES_NO_CHANGES_OUTSIDE_TARGET_ROOT == TRUE
K15: PHASE_4_WRITES_NOTHING_TO_PROJECT_ROOT == TRUE
K16: PHASE_4_DOES_NOT_WRITE_TO("06_data/semantic_cache/") == TRUE


# =====================================================================
# 3. FREEZE REPORT LOCATION & FORMAT
# =====================================================================
K17: FREEZE_REPORT_PATH_FOR_TARGET_ROOT_COMPUTED == TRUE
K18: FREEZE_REPORT_PATH == "<TARGET_ROOT>/<TARGET_ROOT>_freeze_report.json" == TRUE
K19: FREEZE_REPORT_PARENT_DIRECTORY_EXISTS == TRUE

K20: FREEZE_REPORT_IS_VALID_JSON_OBJECT == TRUE
K21: FREEZE_REPORT_HAS_FIELD("schema_version") == TRUE
K22: FREEZE_REPORT_SCHEMA_VERSION == "v1" == TRUE
K23: FREEZE_REPORT_HAS_FIELD("root") == TRUE
K24: FREEZE_REPORT_ROOT == "<TARGET_ROOT>/" == TRUE
K25: FREEZE_REPORT_HAS_FIELD("files") == TRUE
K26: FREEZE_REPORT_FILES_IS_OBJECT == TRUE
K27: FREEZE_REPORT_HAS_NO_ADDITIONAL_TOP_LEVEL_FIELDS == TRUE


# =====================================================================
# 4. FS SCAN & CANONICALIZATION (READ-ONLY)
# =====================================================================
K28: FS_SCAN_FOR_TARGET_ROOT_COMPLETES == TRUE
K29: FS_PATHS_UNDER_TARGET_ROOT_NORMALIZED_TO_FORWARD_SLASH == TRUE
K30: FS_EXCLUDES_SYSTEM_DIRS(".git",".venv","__pycache__",".mypy_cache") == TRUE
K31: FS_DEPTH_LIMIT_NOT_EXCEEDED(<=7) == TRUE
K32: EACH_ENTRY_UNDER_TARGET_ROOT_CLASSIFIED_AS_DIR_OR_FILE == TRUE

K33: DIRECTORY_SET_FOR_TARGET_ROOT_COMPUTED == TRUE
K34: FILE_SET_FOR_TARGET_ROOT_COMPUTED == TRUE


# =====================================================================
# 5. FILE COVERAGE RULES
# =====================================================================
# Freeze report must include ALL files and ONLY files, not directories.

K35: EVERY_FILE_UNDER_TARGET_ROOT_HAS_FREEZE_ENTRY == TRUE
K36: NO_DIRECTORY_PATH_APPEARS_IN_FREEZE_REPORT_FILES == TRUE
K37: ALL_FREEZE_REPORT_KEYS_ARE_RELATIVE_FILE_PATHS == TRUE
K38: ALL_FREEZE_REPORT_KEYS_USE_FORWARD_SLASH == TRUE
K39: NO_DUPLICATE_PATH_KEYS_IN_FREEZE_REPORT == TRUE
K40: FREEZE_REPORT_FILE_COUNT_EQUALS_ACTUAL_FILE_COUNT == TRUE


# =====================================================================
# 6. HASH & SIZE CORRECTNESS
# =====================================================================
K41: EACH_FILE_ENTRY_HAS_FIELD("sha256") == TRUE
K42: EACH_FILE_ENTRY_HAS_FIELD("size_bytes") == TRUE

K43: ALL_SHA256_VALUES_ARE_64_HEX_CHARACTERS == TRUE
K44: ALL_SIZE_BYTES_VALUES_ARE_NON_NEGATIVE_INTEGERS == TRUE

K45: FOR_EACH_FILE_REPORTED_SHA256_MATCHES_ACTUAL_BYTES == TRUE
K46: FOR_EACH_FILE_REPORTED_SIZE_BYTES_MATCHES_ACTUAL_SIZE == TRUE


# =====================================================================
# 7. DETERMINISM & REPEATABILITY
# =====================================================================
K47: FREEZE_REPORT_FILE_KEYS_SORTED_LEXICOGRAPHICALLY == TRUE
K48: FREEZE_REPORT_CONTAINS_NO_TIMESTAMP_FIELDS == TRUE
K49: FREEZE_REPORT_CONTAINS_NO_RANDOM_VALUES == TRUE
K50: FREEZE_REPORT_CONTAINS_NO_MACHINE_SPECIFIC_IDENTIFIERS == TRUE
K51: FREEZE_REPORT_DOES_NOT_USE_MTIME_OR_CTIME == TRUE
K52: PATH_NORMALIZATION_RULES_MATCH_PHASE_1_AND_3 == TRUE
K53: REPEATED_PHASE_4_RUN_WITHOUT_FS_CHANGES_PRODUCES_BIT_IDENTICAL_FREEZE_REPORT == TRUE


# =====================================================================
# 8. PROTECTED PATH SAFETY (READ-ONLY VERIFICATION)
# =====================================================================
# Protected paths (e.g., **/__init__.py) must:
#   • exist in final state
#   • appear in freeze report
#   • be hashed like all other files
#   • never be modified during Phase 4.

K54: PROTECTED_PATH_PATTERNS_DEFINED == TRUE
K55: PROTECTED_PATHS_UNDER_TARGET_ROOT_EXPANDED == TRUE
K56: PROTECTED_PATHS_NORMALIZED_TO_FORWARD_SLASH == TRUE

K57: EVERY_PROTECTED_PATH_EXISTS_ON_FS_AT_ENTRY == TRUE
K58: EVERY_PROTECTED_PATH_HAS_FREEZE_REPORT_ENTRY == TRUE
K59: PROTECTED_PATH_SHA256_VALUES_CORRECT == TRUE
K60: PROTECTED_PATH_SIZE_BYTES_VALUES_CORRECT == TRUE

K61: PHASE_4_DOES_NOT_MODIFY_PROTECTED_PATH_CONTENT == TRUE
K62: PHASE_4_DOES_NOT_DELETE_OR_RENAME_PROTECTED_PATHS == TRUE


# =====================================================================
# 9. SEMANTIC CACHE ISOLATION
# =====================================================================
K63: PHASE_4_DOES_NOT_READ_OR_WRITE("06_data/semantic_cache/") == TRUE
# (Optional: if you want to allow sanity checks, split read/write)
# For now, Phase 4 is strictly independent from semantic cache.


# =====================================================================
# 10. NO MUTATION OF EXISTING FILES
# =====================================================================
K64: PHASE_4_DOES_NOT_MODIFY_ANY_EXISTING_FILE_CONTENT == TRUE
K65: PHASE_4_DOES_NOT_MODIFY_PERMISSIONS == TRUE
K66: PHASE_4_DOES_NOT_MODIFY_TIMESTAMPS == TRUE
K67: PHASE_4_CREATES_NO_TEMP_FILES == TRUE
K68: PHASE_4_CREATES_NO_TEMP_DIRECTORIES == TRUE


# =====================================================================
# 11. TOOLING SAFETY & LOCAL PURITY
# =====================================================================
K69: PHASE_4_MAKES_NO_LLM_CALLS == TRUE
K70: PHASE_4_MAKES_NO_NETWORK_CALLS == TRUE
K71: PHASE_4_EXECUTES_NO_PYTHON_MODULES_FROM_TARGET_ROOT == TRUE
K72: PHASE_4_PERFORMS_ONLY_LOCAL_IO_AND_HASHING == TRUE


# =====================================================================
# 12. POST-FREEZE INTEGRITY CHECKS
# =====================================================================
K73: DIRECTORY_SET_FOR_TARGET_ROOT_UNCHANGED_DURING_PHASE_4 == TRUE
K74: FILE_SET_FOR_TARGET_ROOT_UNCHANGED_DURING_PHASE_4 == TRUE
K75: FS_STRUCTURE_STILL_MATCHES_SSoT_AT_EXIT == TRUE
K76: REHASHING_RANDOM_SAMPLE_OF_FILES_MATCHES_FREEZE_REPORT == TRUE
K77: IMPORTING_TARGET_ROOT_MODULES_SUCCEEDS_WITHOUT_SIDE_EFFECTS (IF APPLICABLE) == TRUE


# =====================================================================
# 13. FREEZE REPORT OUTPUT INTEGRITY
# =====================================================================
K78: FREEZE_REPORT_WRITTEN_ATOMICALLY (WRITE-THEN-RENAME_OR_EQUIVALENT) == TRUE
K79: FREEZE_REPORT_WRITTEN_WITH_FSYNC_OR_EQUIVALENT_DURABILITY == TRUE
K80: FREEZE_REPORT_CONTAINS_ONLY_FIELDS("schema_version","root","files") == TRUE
K81: FREEZE_REPORT_CONTAINS_NO_SOURCE_CODE_SNIPPETS == TRUE
K82: FREEZE_REPORT_CONTAINS_NO_SECRETS_OR_SENSITIVE_DATA == TRUE


# =====================================================================
# 14. COMPLETION GATE
# =====================================================================
K83: FREEZE_REPORT_GENERATED_SUCCESSFULLY == TRUE
K84: ALL_KEYS_K1_TO_K83_PASS == TRUE

# =====================================================================
# END OF PHASE 4 — CRYPTOGRAPHIC FREEZE
# =====================================================================
