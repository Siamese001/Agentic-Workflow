# Unified Memory Directory

This directory contains all memory files for the Agentic Workflow system.

## Files

- `canon_memory.json` - Main memory file (replaces all fragmented canon_memory.json files)
- `current_context.json` - Current cycle state

## Migration

All memory files have been redirected to this unified directory:

**Before:**
- `observability/memory/canon_memory.json`
- `apps_shared/canon_memory.json`
- `apps_rg/resume_memory.json`
- Various other scattered memory files

**After:**
- `.canon_memory/canon_memory.json` (single source of truth)

## Usage

The Universal Context automatically manages this directory:

```python
from agentic_core.infra.context import context

# Automatically loads from .canon_memory/canon_memory.json
context.save_memory()  # Saves to .canon_memory/canon_memory.json
```

## Structure

```json
{
  "last_cycle_id": 42,
  "last_updated": "2025-12-19T14:45:00",
  "file_hashes": {
    "apps_shared/file.py": "abc123..."
  },
  "signals": ["CONVERGENCE", "HEALING_COMPLETE"],
  "modified_files": ["apps_shared/file.py"],
  "healing_budget_used": 15,
  "status": "COMPLETED"
}
```

## Benefits

1. **Single Source of Truth**: All memory in one location
2. **Version Control Friendly**: Single file to track
3. **Atomic Operations**: No race conditions between memory files
4. **Backup Friendly**: Single directory to backup
5. **Clear Ownership**: Universal Context owns all memory

---

**Created**: December 19, 2025
**Part of**: Nervous System Consolidation (Phase 3)
