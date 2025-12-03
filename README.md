# Agentic-Workflow Project

## Project Structure

This project follows a strict root-immutable structure with exactly 10 canonical folders:

```text
C:/Git/Agentic-Workflow/
├── 01_agentic_core/
├── 02_schemas/
├── 03_runtime/
├── 04_prompt_governance/
├── 05_config/
├── 06_data/
│   └── semantic_cache/          # Generated semantic cache
├── 07_observability/
├── 08_scripts/
│   └── phase_0_5_semantic_cache_rebuild.py
├── 09_apps/
├── 10_tests/
├── unified_structure_subatomic.yaml
├── unified_structure_subatomic_meta.yaml
└── README.md
```

## Phase 0.5 Semantic Cache Rebuild

### Overview

The Phase 0.5 pipeline rebuilds the semantic cache with 89 validation criteria across A-G series.

### Running the Pipeline

```bash
cd C:/Git/Agentic-Workflow
python 08_scripts/phase_0_5_semantic_cache_rebuild.py
```

### Architecture

- **PROJECT_ROOT**: `C:/Git/Agentic-Workflow` - All project files and outputs
- **ARCHIVE_ROOT**: `C:/Git` - Historical archive data (external input)

### Pipeline Stages

1. **Archive Scanner** - Scans historical archives with prohibited path filtering
2. **Hash Generator** - Generates SHA256 hashes for eligible files
3. **Global Artifact Writer** - Creates global artifacts (ast, embeddings, diffs, etc.)
4. **Canonical Mapper** - Generates canonical mappings and pointer files
5. **Validator** - Runs all 89 validation criteria

### Key Features

- **Zero-Loss Guarantees**: No files lost during processing
- **Hash Collision Handling**: Preserves all files with identical content
- **POSIX Path Compliance**: All paths stored in POSIX format
- **Comprehensive Validation**: 89 criteria ensure pipeline integrity

### Output Locations

- **Semantic Cache**: `06_data/semantic_cache/`
- **Global Artifacts**: `06_data/semantic_cache/{ast,embeddings,diffs,golden,safety,integrity,meta}/`
- **Pointer Files**: Generated under appropriate canonical roots
- **Audit Logs**: `duplicate_files_audit.json` in semantic cache

## Archive Data

Historical archives remain at the Git root level:

- `C:/Git/Resume Engine Archive/`
- `C:/Git/Reachout Engine Archive/`

These are external inputs and intentionally separate from the project structure.

## Validation Results

All 89 validation criteria must pass:

- **A-SERIES**: SSoT/META validation (10 criteria)
- **B-SERIES**: Archive ingest health (14 criteria)  
- **C-SERIES**: Hash integrity + global artifacts (15 criteria)
- **D-SERIES**: Canonical mapping engine (20 criteria)
- **E-SERIES**: Per-root completeness (10 criteria)
- **F-SERIES**: Sandbox + safety + path rules (10 criteria)
- **G-SERIES**: Phase 2 readiness (10 criteria)

Exit codes:

- `0` = SUCCESS (all criteria pass)
- `1` = VALIDATION FAILURE (any criterion fails)
- `2` = SYSTEM ERROR (crash, I/O error, etc.)

## Development Notes

- Generated semantic cache should not be versioned
- All project modifications must respect protected paths
- No writes outside the project root are allowed
- All paths must be POSIX-compliant
