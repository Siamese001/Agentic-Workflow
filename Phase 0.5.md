
---

# ✅ **PHASE 0.5 — SEMANTIC CACHE REBUILD v5 (FULL CLEAN OVERWRITE)**

### **(FINAL, CANONICAL, ZERO-LOSS, STRICT-MODE COMPLIANT)**

```markdown
# =====================================================================
# PHASE 0.5 — SEMANTIC CACHE REBUILD v5
# ARCHIVE-ONLY INPUTS → HASH GLOBAL ARTIFACTS → CANONICAL POINTERS
# STRICT-MODE READY (ALL 89 EXTREME CRITERIA)
# =====================================================================

## PURPOSE
Phase 0.5 rebuilds the **semantic cache** used by Phase 2 and Phase 3 by:

1. Scanning **historical RG and LIC archives** (ONLY these — never live folders)
2. Generating **global semantic artifacts** for every unique file hash
3. Mapping each archived file onto the **canonical SSoT structure** (L1–L5 / P1–P4)
4. Writing **pointer artifacts** in the 10 canonical semantic buckets matching
   the live tree:
   - agentic_core
   - schemas
   - runtime
   - prompt_governance
   - config
   - data_source
   - observability
   - scripts
   - apps
   - tests
5. Ensuring all output uses **POSIX path rules, forward slashes, and no backslashes**
6. Guaranteeing **zero-loss**, **idempotency**, and **full strict-mode validation**

This version fixes all previously observed defects:
- Windows backslashes in filenames  
- Incorrect directory names (embedding → embeddings)  
- Missing directory creation  
- Global artifacts written to wrong paths  
- Pointer filenames containing nested paths  
- canonical_relative not normalized  
- Mapping failures (D1.x, D2.x, E3.x, G-series)  
- Archive zip UTF-8 decode errors  
- Inconsistent global/pointer artifact counts  

---

# =====================================================================
# 0. GLOBAL NON-NEGOTIABLE RULES
# =====================================================================

### H1 — **Do NOT scan live folders** (01–10)
All semantic lineage must come ONLY from historical archives.

### H2 — **Rebuild semantic_cache/ clean each run**
Delete the entire folder before execution:
```

06_data/semantic_cache/

```

### H3 — **All filesystem writes MUST use forward slashes**
No Windows backslashes in:
- filenames
- directories
- canonical paths
- pointer filenames
- global artifact paths

### H4 — **All artifact directories must be created before writes**
No attempted writes to missing folders.

### H5 — **canonical_relative must be normalized BEFORE writing**
Correct:
```

canonical_relative = canonical_relative.replace("\", "/")

```

### H6 — **Pointer filenames must NOT include directory separators**
Correct pattern:
```

<canonical_dir>/<file_stem>.<artifact_type>

```

### H7 — **Global directories MUST use PLURAL names**
```

ast/
embeddings/
diffs/
golden/
safety/
integrity/
meta/

```
Any mismatch → FAIL.

### H8 — **Each pointer artifact must contain a valid JSON object**
```

{
"hash": "<H>",
"type": "<artifact_type>",
"global": "06_data/semantic_cache/<bucket>/<H>.<ext>"
}

```

### H9 — **All artifacts must be non-empty**
No stub files, placeholders, or incomplete writes.

### H10 — **ALL 89 extreme validation criteria must pass**
This is the final readiness gate before Phase 2.

---

# =====================================================================
# 1. PROJECT DIRECTORY EXPECTATION
# =====================================================================

```

Agentic-Workflow/
phase05/
**init**.py
orchestrator.py
ssot_loader.py
archive_scanner.py
semantic_artifact_generator.py
dual_write_coordinator.py
validation_engine.py
extreme_validation.py
common.py

```
01_agentic_core/
02_schemas/
...
06_data/semantic_cache/   (recreated each run)
...
unified_structure_subatomic.yaml
unified_structure_subatomic_meta.yaml
```

```

---

# =====================================================================
# 2. ARCHIVE INPUT ROOTS (SCANNED)
# =====================================================================

### Historical Resume Engine (RG):
- Agentic-Workflow-10_11  
- Agentic_Workflow-10_10  
- Agentic-Workflow-10_9  
- Agentic-Workflow-10_8_core  
- Agentic-Workflow-10_7_main  
- Microservices Model  
- Monolith  
- Monolithic  
- v2  
- v6.0  

### Historical Outreach Engine (LIC):
- Agentic-LIC  
- Agentic LIC  
- Monolithic  
- Old LIC  
- deprecated in v13  

### Special-case:
Only 4 files scanned in “Old Resume Gen Python”.

### Explicitly NOT scanned:
- All ZIP files  
- All non-UTF-8 binary formats  
- All live folders (01–10)  

If UTF-8 decode fails:
- **Skip file**, generate integrity-only artifact, DO NOT crash.

---

# =====================================================================
# 3. ARCHIVE SCANNING BEHAVIOR
# =====================================================================

### Eligibility:
✓ .py  
✓ .json  
✓ .yaml / .yml  
✓ .md  
✓ .txt  

### Ineligible:
✗ binaries  
✗ images  
✗ *.zip / *.tar / *.7z  
✗ *.pyc / *.pyo / *.pyd  
✗ *.db / *.sqlite  

### Required behavior:
- Depth ≤ 7  
- Path normalization (replace backslashes)  
- Generate integrity artifact for ANY skipped or unreadable file  
- For eligible files:
  - read raw bytes  
  - hash = SHA256(bytes)  
  - record hash + metadata  

---

# =====================================================================
# 4. GLOBAL ARTIFACT GENERATION (HASH-DEDUPED)
# =====================================================================

For each unique hash H:

Generate (if missing):
```

ast/<H>.ast
ast/<H>.ast.meta.json
embeddings/<H>.embedding
embeddings/<H>.embedding.meta.json
diffs/<H>.diff.json
golden/<H>.golden.json
safety/<H>.safety.json
integrity/<H>.integrity.json
meta/<H>.meta.json

```

### Requirements:
- Create directories FIRST
- File write must be atomic
- No empty content
- No corruption allowed
- Pointer creation MUST come after global creation

---

# =====================================================================
# 5. CANONICAL MAPPING ENGINE (CRITICAL)
# =====================================================================

### Steps for each archive file F with hash H:

#### **5.1 Compute canonical root**
Use SSoT + META to map archive path → one of:

```

agentic_core
schemas
runtime
prompt_governance
config
data_source
observability
scripts
apps
tests

```

#### **5.2 Compute canonical_relative**
Must follow SSoT grammar:

```

<LAYER>/<PHASE>/<VERB_GROUP>/<DOMAIN>/<FILE>

```

#### **5.3 Normalize canonical_relative**
MANDATORY:

```

canonical_relative = canonical_relative.replace("\", "/")

```

#### **5.4 Build directory path**
```

parts = canonical_relative.split("/")
canonical_dir = semantic_cache/<root>/Path(*parts[:-1])
file_stem = parts[-1].split(".")[0]

```

#### **5.5 Create directories**
```

canonical_dir.mkdir(parents=True, exist_ok=True)

```

#### **5.6 Write pointer artifacts**
For each artifact type T ∈:
```

["ast","ast.meta","embedding","embedding.meta","diff","golden","safety","integrity"]

```

Write:
```

<canonical_dir>/<file_stem>.<ext>

```

#### **5.7 Pointer JSON structure**
```

{
"hash": "<H>",
"type": "<artifact_type>",
"global": "06_data/semantic_cache/<bucket>/<H>.<ext>"
}

```

### Pointer filenames MUST NOT contain `/` or `\`.

If mapping fails → mark “unmapped” and write only integrity.json.

---

# =====================================================================
# 6. PER-ROOT COMPLETENESS CHECK
# =====================================================================

Each canonical root must satisfy:

- Pointer artifacts exist for every mapped file  
- Count(pointer.ast) = count(pointer.golden)  
- All pointers reference existing global H files  
- No pointer directory contains backslashes  
- All path components POSIX-only  
- No orphan directories  

---

# =====================================================================
# 7. EXTREME VALIDATION (89 CRITERIA)
# =====================================================================

**ALL** sections must pass:

- **A-series**: SSoT + META validity  
- **B-series**: Archive ingest health  
- **C-series**: Hash integrity & global artifacts  
- **D-series**: Canonical mapping correctness  
- **E-series**: Per-root completeness  
- **F-series**: Sandbox + path safety (F1.4 = NO BACKSLASH ANYWHERE)  
- **G-series**: Phase 2 readiness gate  

Any failure → Phase 0.5 terminates → Phase 2 MUST NOT run.

---

# =====================================================================
# 8. COMPLETION CONDITION (PHASE 2 READINESS)
# =====================================================================

PHASE 0.5 is COMPLETE ONLY IF:

```

ALL 89 EXTREME VALIDATION CRITERIA PASS
NO WINDOWS BACKSLASHES EXIST ANYWHERE
GLOBAL ARTIFACTS ARE COMPLETE
POINTER ARTIFACTS ARE COMPLETE
ALL DIRECTORIES ARE CORRECT (plural)
CANONICAL MAPPING SUCCEEDED FOR ALL MAPPABLE FILES
NO PLACEHOLDERS OR EMPTY FILES
STRICT-MODE EXIT CODE == 0

```

If ANY condition fails:
- Zero-loss guarantee is violated  
- Phase 2 must NOT begin  

---

# =====================================================================
# END — PHASE 0.5 (v5 FINAL, STRICT-MODE SAFE)
# =====================================================================
```
