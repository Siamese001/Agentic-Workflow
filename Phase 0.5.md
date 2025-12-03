# =====================================================================
# WINDSURF_RULE_LOADER_ACTIVATE
# =====================================================================
# WORKFLOW:
#    Agentic-Workflow — PHASE 0.5 (Semantic Lineage Cache Rebuild v3-LITE)
#
# GLOBAL OBJECTIVE (ZERO-LOSS):
#    Build a COMPLETE semantic cache for:
#
#    (A) HISTORICAL ENGINES ONLY
#         1. Resume Engine Archive (RG)
#         2. Outreach Engine Archive (LIC)
#
#    (B) SEMANTIC BUCKETS FOR ALL 10 CANONICAL LIVE REPO FOLDERS:
#         01_agentic_core          → agentic_core
#         02_schemas               → schemas
#         03_runtime               → runtime
#         04_prompt_governance     → prompt_governance
#         05_config                → config
#         06_data                  → data_source (SOURCE CODE ONLY)
#         07_observability         → observability
#         08_scripts               → scripts
#         09_apps                  → apps
#         10_tests                 → tests
#
#    CRITICAL: Phase 0.5 DOES NOT scan the live 10 folders.
#              It ONLY reads the archives and maps semantics into
#              the 10 buckets using the SSoT YAML.
#
#    ALL semantic artifacts MUST be written ONLY to:
#
#           06_data/semantic_cache/
#
#    ABSOLUTELY NOTHING MAY BE WRITTEN ANYWHERE ELSE.
# =====================================================================


# =====================================================================
# 0. PROJECT ROOT + REQUIRED OUTPUT STRUCTURE (MANDATORY)
# =====================================================================
C:\Git\Agentic-Workflow\
    01_agentic_core\
    02_schemas\
    03_runtime\
    04_prompt_governance\
    05_config\
    06_data\
    07_observability\
    08_scripts\
    09_apps\
    10_tests\
    unified_structure_subatomic.yaml
    ...

# PHASE 0.5 OUTPUT ROOT:
06_data/semantic_cache/

# REQUIRED SUBDIRECTORIES (MUST EXIST):
06_data/semantic_cache/
    ast/
    diffs/
    embeddings/
    golden/
    integrity/
    meta/
    safety/

    resume_engine/       # archive semantics (RG)
    outreach_engine/     # archive semantics (LIC)

    agentic_core/        # semantic buckets mapped from archives via SSoT
    schemas/
    runtime/
    prompt_governance/
    config/
    data_source/
    observability/
    scripts/
    apps/
    tests/

# NOTE:
#   Folders MUST exist, but they are NOT required to be non-empty on
#   first run. No dummy artifacts should be written just to satisfy
#   "non-empty" conditions.
# =====================================================================


# =====================================================================
# 0.1 FILE ELIGIBILITY RULES + RECURSION DEPTH
# =====================================================================
# MAX DEPTH:
#   Recurse each ARCHIVE input root up to depth = 7.

# ELIGIBLE FILE TYPES:
#   .py
#   .json
#   .yaml, .yml
#   .md
#   .txt

# EXCLUDED DIRECTORIES:
#   __pycache__, .pytest_cache, .mypy_cache, .ruff_cache,
#   .git, .venv, .idea, .vscode

# EXCLUDED / NON-SEMANTIC FILE TYPES:
#   *.pyc, *.pyo, *.pyd, *.db, *.sqlite, *.log, binaries, images

# RULE FOR NON-ELIGIBLE FILES:
#   - Do NOT generate AST/embedding/diff/golden/safety.
#   - MUST generate an integrity record:
#           <ROOT>/<relative>.integrity.json
#           06_data/semantic_cache/integrity/<HASH>.integrity.json
# =====================================================================


# =====================================================================
# 1. HISTORICAL RESUME ENGINE INPUT ROOTS (RG) — PRUNED
# =====================================================================
# Phase 0.5 scans ONLY these RG archive roots:

C:\Git\Resume Engine Archive\Agentic-Workflow-10_11\
C:\Git\Resume Engine Archive\Agentic_Workflow-10_10\
C:\Git\Resume Engine Archive\Agentic-Workflow-10_9\
C:\Git\Resume Engine Archive\Agentic-Workflow-10_8_core\
C:\Git\Resume Engine Archive\Agentic-Workflow-10_7_main\
C:\Git\Resume Engine Archive\Microservices Model\
C:\Git\Resume Engine Archive\Monolith\
C:\Git\Resume Engine Archive\Monolithic\
C:\Git\Resume Engine Archive\v2\
C:\Git\Resume Engine Archive\v6.0\

# DO NOT SCAN (REMOVED VERSIONS):
#   C:\Git\Resume Engine Archive\v7.0\
#   C:\Git\Resume Engine Archive\v8.0\
#   C:\Git\Resume Engine Archive\v9.0\
#   C:\Git\Resume Engine Archive\v10.7\

# SPECIAL CASE: Old Resume Gen Python
#   Only these 4 files are scanned:

C:\Git\Resume Engine Archive\Old Resume Gen Python\Resume_Generation_v14_19.py
C:\Git\Resume Engine Archive\Old Resume Gen Python\Resume_Generation_v11.40.py
C:\Git\Resume Engine Archive\Old Resume Gen Python\Resume_Generation_v9_82.py
C:\Git\Resume Engine Archive\Old Resume Gen Python\Resume_Generation_v5_44.py

#   Every other file under "Old Resume Gen Python" is ignored.

# PER-FILE OUTPUT (RESUME ENGINE, ROOT-LOCAL):
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.ast
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.ast.meta.json
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.embedding
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.embedding.meta.json
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.diff.json
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.golden.json
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.safety.json
06_data/semantic_cache/resume_engine/<archive_name>/<relative>.integrity.json
# =====================================================================


# =====================================================================
# 2. HISTORICAL OUTREACH ENGINE INPUT ROOTS (LIC)
# =====================================================================
# LIC archives are scanned fully:

C:\Git\Reachout Engine Archive\Agentic-LIC\
C:\Git\Reachout Engine Archive\Agentic LIC\
C:\Git\Reachout Engine Archive\Monolithic\
C:\Git\Reachout Engine Archive\Old LIC\
C:\Git\Reachout Engine Archive\deprecated in v13\

# PER-FILE OUTPUT (OUTREACH ENGINE, ROOT-LOCAL):
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.ast
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.ast.meta.json
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.embedding
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.embedding.meta.json
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.diff.json
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.golden.json
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.safety.json
06_data/semantic_cache/outreach_engine/<archive_name>/<relative>.integrity.json
# =====================================================================


# =====================================================================
# 3. LIVE 10-FOLDER SEMANTIC BUCKETS (TARGETS — DO NOT SCAN)
# =====================================================================
# Phase 0.5 MUST NOT scan these folders:
#
#   C:\Git\Agentic-Workflow\01_agentic_core\
#   C:\Git\Agentic-Workflow\02_schemas\
#   C:\Git\Agentic-Workflow\03_runtime\
#   C:\Git\Agentic-Workflow\04_prompt_governance\
#   C:\Git\Agentic-Workflow\05_config\
#   C:\Git\Agentic-Workflow\06_data\
#   C:\Git\Agentic-Workflow\07_observability\
#   C:\Git\Agentic-Workflow\08_scripts\
#   C:\Git\Agentic-Workflow\09_apps\
#   C:\Git\Agentic-Workflow\10_tests\
#
# Instead, Phase 0.5 MUST:
#   - Read unified_structure_subatomic.yaml (SSoT)
#   - For each archived file F, determine its canonical destination
#     live-folder + relative path in the new architecture
#   - Create semantic artifacts under:
#
#      06_data/semantic_cache/<target_root>/<relative_mapped>.*
#
# where <target_root> is one of:
#
#   agentic_core/
#   schemas/
#   runtime/
#   prompt_governance/
#   config/
#   data_source/
#   observability/
#   scripts/
#   apps/
#   tests/
#
# NOTE: These buckets are “semantic targets,” NOT scan inputs.
# =====================================================================


# =====================================================================
# 4. GLOBAL HASH-ADDRESSED ARTIFACTS (MANDATORY, DEDUPED)
# =====================================================================
# Compute SHA256 hash H for each file’s RAW TEXT CONTENT (archives only).

GLOBAL TARGETS (ONE PER HASH VALUE H):
06_data/semantic_cache/ast/<H>.ast
06_data/semantic_cache/ast/<H>.ast.meta.json

06_data/semantic_cache/embeddings/<H>.embedding
06_data/semantic_cache/embeddings/<H>.embedding.meta.json

06_data/semantic_cache/diffs/<H>.diff.json
06_data/semantic_cache/golden/<H>.golden.json
06_data/semantic_cache/safety/<H>.safety.json
06_data/semantic_cache/meta/<H>.meta.json
06_data/semantic_cache/integrity/<H>.integrity.json

# DEDUP RULE:
#   - If <H> already exists globally, DO NOT re-write the global artifacts.
#   - Local (per-root / per-target) artifacts are allowed to be pointers
#     (small JSON references) to the global H artifacts instead of copies.
# =====================================================================


# =====================================================================
# 5. REQUIRED ARTIFACT SET (8 FILES PER ELIGIBLE FILE, LOGICAL)
# =====================================================================
For every ELIGIBLE archived file F, Phase 0.5 MUST logically produce:

1. F.ast  
2. F.ast.meta.json  
3. F.embedding  
4. F.embedding.meta.json  
5. F.diff.json  
6. F.safety.json  
7. F.golden.json  
8. F.integrity.json  

AND ensure that:
- There is a corresponding hash-addressed GLOBAL set for H(F),
  created once and reused.

NO missing files for eligible F.  
NO empty files.  
NO “TODO” stubs.

For NON-ELIGIBLE FILES:
    Only integrity records are generated (local + global).
# =====================================================================


# =====================================================================
# 6. DIFF BASELINE LOGIC (OPTION A)
# =====================================================================
# HISTORICAL ENGINE DIFFS (RG + LIC):
#     baseline = earlier version of same logical file in archive lineage
#     if first appearance: baseline = empty

# LIVE FOLDER BUCKET DIFFS:
#     baseline = previous Phase 0.5 semantic cache snapshot
#     if file has no previous semantic cache → baseline = empty AND mark:
#         "initial_diff": true
# =====================================================================


# =====================================================================
# 7. ZERO-LOSS VALIDATION PER ROOT
# =====================================================================
For each semantic root:

resume_engine/
outreach_engine/
agentic_core/
schemas/
runtime/
prompt_governance/
config/
data_source/
observability/
scripts/
apps/
tests/

Each MUST satisfy:

K17: ROOT_FILECOUNT == ROOT_ARTIFACT_COUNT_FOR_ELIGIBLE_FILES  
K18: NO_ARTIFACTS_MISSING == TRUE  
K19: NO_EXTRA_ARTIFACTS == TRUE  
K20: ROOT_INDEX_WRITTEN == TRUE   # index listing input files and their artifacts

# (No longer require "ROOT_FOLDER_NOT_EMPTY" just to avoid empty dirs.)
# =====================================================================


# =====================================================================
# 8. GLOBAL ZERO-LOSS VALIDATION
# =====================================================================
K21: GLOBAL_AST_COUNT       == TOTAL_ELIGIBLE_INPUT_FILE_COUNT  
K22: GLOBAL_EMBEDDING_COUNT == TOTAL_ELIGIBLE_INPUT_FILE_COUNT  
K23: GLOBAL_META_COUNT      == TOTAL_ELIGIBLE_INPUT_FILE_COUNT  
K24: GLOBAL_DIFF_COUNT      == TOTAL_ELIGIBLE_INPUT_FILE_COUNT  
K25: GLOBAL_GOLDEN_COUNT    == TOTAL_ELIGIBLE_INPUT_FILE_COUNT  
K26: GLOBAL_SAFETY_COUNT    == TOTAL_ELIGIBLE_INPUT_FILE_COUNT  
K27: GLOBAL_INTEGRITY_COUNT >= TOTAL_INPUT_FILE_COUNT  # includes non-eligible files

K28: NO_HASH_COLLISIONS == TRUE  
K29: GLOBAL_INDEX_BUILT == TRUE   # H(F) → all roots mapping

# NOTE: We DO NOT require “ALL_GLOBAL_BUCKETS_NONEMPTY” anymore. Buckets
# may be empty if no files of that type exist yet; no dummy writes.
# =====================================================================


# =====================================================================
# 9. SANDBOX / SAFETY GUARANTEES
# =====================================================================
K30: NO_WRITES_OUTSIDE("06_data/semantic_cache/") == TRUE  
K31: NO_ARCHIVE_FILES_MODIFIED == TRUE  
K32: NO_REPO_SOURCE_MODIFIED   == TRUE  
K33: NO_RUNTIME_EXECUTION_OF_TARGET_CODE == TRUE  
K34: NO_NETWORK_CALLS == TRUE  
# =====================================================================


# =====================================================================
# 10. QUALITY GATES
# =====================================================================
K35: RUFF_CLEAN   == TRUE  
K36: MYPY_CLEAN   == TRUE  
K37: PYTEST_PASS  == TRUE  
K38: IMPORT_HEALTH_PASS == TRUE  
# =====================================================================


# =====================================================================
# 11. COMPLETION GATE (ALL KEYS MUST PASS)
# =====================================================================
K39: ALL_KEYS_K1_TO_K38_PASS == TRUE  
K40: SEMANTIC_CACHE_READY_FOR_PHASE_2 == TRUE  

# No K42/K43 “non-empty” hard requirements that force garbage artifacts.
# =====================================================================
# END PHASE 0.5 — ZERO-LOSS OVERWRITE (ARCHIVE-ONLY, SSoT-MAPPED)
# =====================================================================


