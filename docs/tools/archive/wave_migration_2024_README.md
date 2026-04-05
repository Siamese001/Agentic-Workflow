# Wave Migration Scripts Archive (2024)

This directory contains the wave-based migration scripts used during the 2024 test infrastructure migration. These scripts were executed once during the migration and are preserved here for historical reference.

## Overview

The wave migration was a systematic approach to fixing syntax errors and migration artifacts across the test suite. Each wave targeted specific categories of issues:

### Wave Categories

| Wave | Name | Purpose |
|------|------|---------|
| 1 | basic_cleanup | Remove obvious migration artifacts, legacy comments, orphaned lines |
| 2 | fix_collection_errors | Fix pytest fixture collection errors by deferring import failures |
| 3 | block_removal | Remove entire problematic code blocks causing syntax errors |
| 4 | final_validation | Apply minimal targeted fixes for syntax validity |
| 5 | complete_fix | Comprehensive fixes for remaining syntax errors |
| 6-40 | Various | Incremental fixes for specific error patterns (indentation, blocks, imports, etc.) |

### Common Pattern

Most waves followed a consistent structure:

```python
class WaveX:
    def __init__(self, repo_root: pathlib.Path)
    def process_files(self) -> Dict  # Iterate tests/ directory
    def process_file(self, path) -> bool  # Fix individual file
```

### Key Files

- `wave_state_manager.py` - Tracks wave execution state for idempotency
- `wave[1-40]_*.py` - Individual wave scripts targeting specific error patterns

## Status

**ARCHIVED**: These scripts served their purpose during the 2024 migration. They are:
- Not referenced in CI/CD workflows
- Not imported by active code
- Marked as `hollow_file` in burndown budget
- Preserved for historical reference only

## Usage (Historical)

These scripts were designed to be run sequentially:

```bash
# During migration (2024)
python tools/wave1_basic_cleanup.py
python tools/wave2_fix_collection_errors.py
python tools/wave3_block_removal.py
# ... etc
```

## See Also

- `tools/adg/` - Current ADG tooling (replaces wave-based approach)
- `ops_scripts/hooks/burndown_budget.json` - Records these as one-time scripts
