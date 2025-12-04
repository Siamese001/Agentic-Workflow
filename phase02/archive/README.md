# Phase 2 Semantic Structural & Code Diff Planning

## Overview

Phase 2 implements semantic structural and code diff planning for the Agentic-Workflow system. It produces a complete, deterministic unified plan for the `01_agentic_core/` subtree by incorporating both structural state (SSoT YAML + META vs filesystem) and semantic lineage state (Phase 0.5 cache).

## Architecture

The Phase 2 implementation follows the proven Phase 0.5 architecture with modular components, dependency injection, and comprehensive validation:

### Core Components

1. **common.py** - Shared data structures, constants, and 88 K-key validation groups
2. **ssot_filesystem_loader.py** - Loads SSoT and filesystem state (K1-K10 validation)
3. **semantic_cache_loader.py** - Loads Phase 0.5 cache with path normalization (K11-K16 validation)
4. **structural_diff_engine.py** - Computes structural diffs (K17-K24 validation)
5. **semantic_diff_engine.py** - Computes semantic diffs using AST, embeddings, golden records (K25-K36 validation)
6. **composite_intent_generator.py** - Generates deterministic intent (K37-K43 validation)
7. **unified_plan_generator.py** - Creates JSON migration plan (K44-K88 validation)
8. **phase02_orchestrator.py** - Complete pipeline orchestration with checkpoint/resume

### Pipeline Flow

```text
SSoT/FS Loading → Cache Loading → Structural Diff → Semantic Diff → Intent Generation → Plan Generation → Final Validation
     K1-K10          K11-K16         K17-K24          K25-K36            K37-K43             K44-K88
```

## Key Features

### Zero-Loss Compliance

- Read-only operations for FS and semantic cache
- Docker-safe paths only (forward slashes)
- No mutations during Phase 2 execution
- Protected path rules enforced (__init__.py files)

### Deterministic Computation

- Weighted confidence scoring for semantic diffs
- Priority ordering for intent computation
- AST-based structural comparison
- No LLM calls, network calls, or randomness

### Comprehensive Validation

- 88 K-key validations in phased approach
- Transaction manifest for checkpoint/resume
- Detailed validation reporting
- Error recovery and rollback support

### Semantic Diff Computation

- **AST Diffs**: Structural comparison between cached and live code
- **Embedding Distances**: Similarity metrics using cached embeddings
- **Golden Record Differences**: Ground truth comparison
- **Tool Usage Diffs**: Function call changes
- **Behavior Diffs**: Class and method signature changes
- **Layer Mismatches**: L1-L5 layer validation

## Usage

### Command Line

```bash
# Full pipeline execution
python phase02_orchestrator.py

# Dry run mode (no file writes)
python phase02_orchestrator.py --dry-run

# Verbose output
python phase02_orchestrator.py --verbose

# Resume from specific step
python phase02_orchestrator.py --resume-from SEMANTIC_DIFF

# Validation only
python phase02_orchestrator.py --validate-only
```

### Python API

```python
from phase02 import Phase02Orchestrator, Phase2Config

# Create configuration
config = Phase2Config(
    dry_run=False,
    verbose=True,
    resume_from=None
)

# Run pipeline
orchestrator = Phase02Orchestrator(config)
success = orchestrator.run_pipeline()

if success:
    migration_plan = orchestrator.migration_plan
    print(f"Generated {len(migration_plan.operations)} operations")
```

## Validation Keys

### Precondition Validation (K1-K7)
- K1: Phase 1 completed successfully
- K2: FS structure matches SSoT exactly
- K3-K7: Semantic cache and environment validation

### Loading Validation (K8-K16)
- K8-K10: SSoT and filesystem loading
- K11-K16: Semantic cache loading and path normalization

### Structural Diff Validation (K17-K24)
- K17-K23: Structural diff computation
- K24: Structural diff is empty (Phase 1 requirement)

### Semantic Diff Validation (K25-K36)
- K25-K29: Per-file artifact loading
- K30-K36: Semantic diff computation and META alignment

### Intent Validation

- K37-K42: Intent computation for all operation types
- K43: Intent determinism validation

### Plan Generation Validation

- K44-K55: Plan structure and schema validation
- K56-K63: Operation and path rules
- K64-K68: Protected path compliance
- K69-K73: Immutability guarantees
- K74-K79: Determinism validation
- K80-K83: Summary validation
- K84-K88: Completion validation

## Output Files

### Primary Output
- `02_schemas/01_agentic_core_migration_and_rewrite_plan.json` - Complete migration plan

### Reports and Checkpoints
- `02_schemas/phase02_loading_report.json` - SSoT and filesystem loading report
- `02_schemas/phase02_semantic_cache_loading_report.json` - Cache loading report
- `02_schemas/phase02_structural_diff_report.json` - Structural diff report
- `02_schemas/phase02_semantic_diff_report.json` - Semantic diff report
- `02_schemas/phase02_composite_intent_report.json` - Intent generation report
- `02_schemas/phase02_transaction_manifest.json` - Transaction manifest (checkpoint/resume)

## Migration Plan Schema

```json
{
  "schema_version": "v1",
  "target_root": "01_agentic_core/",
  "mode": "semantic_structural_unified",
  "operations": [
    {
      "operation_type": "rewrite_file_from_cache",
      "target_path": "01_agentic_core/L1_cognition/P1_retrieve/example.py",
      "metadata": {
        "confidence": 0.85,
        "diff_type": "ast_diff",
        "reason": "High confidence semantic diff requires rewrite"
      }
    }
  ],
  "summary": {
    "total_operations": 1,
    "operation_counts": {...},
    "structural_operations": 0,
    "semantic_operations": 1
  },
  "metadata": {
    "validation_summary": {...},
    "zero_loss_compliance": true,
    "docker_safe": true
  }
}
```

## Operation Types

### Structural Operations

- `create_dir` - Create directory
- `create_file` - Create file
- `delete_dir` - Delete directory (not for protected paths)
- `delete_file` - Delete file (not for protected paths)
- `move_path` - Move/rename path (not for protected paths)
- `rename_path` - Rename path (not for protected paths)

### Semantic Operations

- `rewrite_file_from_cache` - Complete file rewrite from cache
- `merge_file_from_cache` - Merge file with cache version
- `patch_region_from_cache` - Apply specific patches from cache
- `insert_semantic_block` - Insert semantic code block
- `delete_semantic_block` - Delete semantic code block
- `canonical_rewrite` - Canonical form rewrite

## Protected Paths

The following paths are protected from structural operations:
- `__init__.py`
- `01_agentic_core/__init__.py`
- `01_agentic_core/**/__init__.py`

Semantic operations (rewrite, merge, patch) are allowed on protected paths.

## Error Handling

### Checkpoint/Resume

- Transaction manifest saves pipeline state after each step
- Resume from any failed step using `--resume-from`
- Detailed error messages and validation failures

### Validation Failures

- All validation keys must pass for successful completion
- Detailed failure reports with specific K-key information
- Automatic retry capability for transient failures

## Integration with Phase 0.5

Phase 2 depends on Phase 0.5 semantic cache:
- Reads AST, embeddings, diffs, golden records from `06_data/semantic_cache/agentic_core/`
- Uses global artifacts and hash indexes for deduplication
- Leverages path mappings for cache-to-filesystem alignment

## Zero-Loss Guarantees

- No file modifications during Phase 2 execution
- Read-only access to semantic cache and filesystem
- Comprehensive validation prevents data loss
- Transaction logging ensures auditability

## Docker Compliance

- All paths use forward slashes
- No host-specific path references
- Container-safe file operations
- No external service dependencies

### Performance Considerations

- Efficient AST parsing and comparison
- Hash-based file deduplication
- Parallel component loading where possible
- Memory-efficient semantic artifact processing

## Troubleshooting

### Common Issues

1. **Missing Phase 0.5 Cache**: Ensure Phase 0.5 completed successfully
2. **Path Mapping Failures**: Check semantic cache path normalization
3. **Protected Path Violations**: Review operation generation rules
4. **Validation Failures**: Check specific K-key error messages

### Debug Mode

```bash
# Run with verbose output and dry run
python phase02_orchestrator.py --dry-run --verbose

# Resume from specific failed step
python phase02_orchestrator.py --resume-from SEMANTIC_DIFF --verbose
```

## Future Enhancements

- Enhanced semantic similarity metrics
- Additional operation types for specific use cases
- Performance optimizations for large codebases
- Integration with external semantic analysis tools
