# RCA: SQLite WAL Files (-shm and -wal) Created During ADG Generation

**Date**: 2026-04-06  
**Severity**: LOW  
**Status**: RESOLVED

---

## Executive Summary

SQLite creates auxiliary files `-shm` (shared memory) and `-wal` (write-ahead log) when WAL mode is enabled. These files are normal SQLite behavior for better concurrency and performance. They should be cleaned up during archive cleanup but are currently being left behind.

**Root Cause**: Archive cleanup logic only targets `.sqlite` files, not the associated `-shm` and `-wal` files.

---

## Incident Details

### Files Identified
```
C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04062026_0337.sqlite-shm
C:\Git\Agentic-Workflow\artifacts\adg\Workflow\adg_indexed_04062026_0337.sqlite-wal
```

### What These Files Are

**SQLite Write-Ahead Logging (WAL) Mode:**
- `.sqlite-wal`: Write-Ahead Log file - contains changes not yet checkpointed to main database
- `.sqlite-shm`: Shared-Memory file - contains index metadata for WAL file
- Both are auxiliary files created when SQLite operates in WAL mode
- Enable better concurrency (multiple readers, single writer)
- Improve performance by reducing disk I/O

### Why WAL Mode is Enabled

In `tools/adg/core/sqlite_backend.py`:
```python
# Enable WAL mode for better concurrency
self._conn.execute("PRAGMA journal_mode=WAL")
```

This is intentional for performance and concurrency benefits.

---

## Root Cause Analysis

### Primary Cause
Archive cleanup in `tools/generate/_archive_old_artifacts()` only deletes files matching specific patterns:
- `adg_snapshot_*.json`
- `adg_indexed_*.sqlite`
- `adg_file_graph_*.json`
- `adg_symbol_graph_*.json`
- `adg_governance_graph_*.json`
- `adg_graphsnap_*.json`

It does **not** delete the associated `-shm` and `-wal` files.

### Impact
- **Disk space accumulation**: WAL files accumulate over time
- **Orphaned files**: Left behind after main `.sqlite` files are deleted
- **Confusion**: Users see unexpected files and question their purpose
- **No functional impact**: These files don't affect ADG queries

---

## Corrective Actions

### Immediate Fix (Implemented)
**File**: `tools/generate/generate_full_adg.py`

Modified archive cleanup to also delete `-shm` and `-wal` files:

```python
# In _archive_old_artifacts()
for run_timestamp, files in to_archive.items():
    for file_path in files:
        if file_path.exists():
            # Delete main file
            file_path.unlink()
            
            # Also delete associated WAL files
            wal_file = file_path.with_suffix(".sqlite-wal")
            shm_file = file_path.with_suffix(".sqlite-shm")
            
            if wal_file.exists():
                wal_file.unlink()
            if shm_file.exists():
                shm_file.unlink()
```

### Code Changes

**Modified**: `tools/generate/generate_full_adg.py` function `_archive_old_artifacts()`

Added cleanup for WAL files after deleting main SQLite files:
```python
# After successful file deletion
if file_path.suffix == ".sqlite":
    # Delete associated WAL files
    wal_path = file_path.with_suffix(".sqlite-wal")
    shm_path = file_path.with_suffix(".sqlite-shm")
    
    for aux_file in [wal_path, shm_path]:
        if aux_file.exists():
            try:
                aux_file.unlink()
            except OSError as e:
                logger.debug(f"Could not delete {aux_file.name}: {e}")
```

---

## Verification

### Test Case 1: WAL Files Created During ADG Generation
- [ ] Run `generate_full_adg.py --full`
- [ ] Verify `.sqlite-wal` and `.sqlite-shm` files are created
- [ ] This is expected behavior

### Test Case 2: WAL Files Cleaned Up During Archive
- [ ] Run `generate_full_adg.py --full` twice
- [ ] Verify old `.sqlite-wal` and `.sqlite-shm` files are deleted
- [ ] Verify only current run's WAL files remain

### Test Case 3: WAL Files Not Locked
- [ ] Check that WAL files are not locked after MCP server closes connections
- [ ] Verify archive cleanup can delete WAL files without errors

---

## Prevention

### Process Changes

1. **Document WAL file behavior**:
   - Add to ADG documentation: "SQLite creates -shm and -wal files in WAL mode"
   - Explain these are normal and automatically cleaned up

2. **Archive cleanup pattern**:
   - Ensure all auxiliary files are deleted when main files are archived
   - Pattern: For `*.sqlite`, also delete `*.sqlite-wal` and `*.sqlite-shm`

### Future Enhancements

1. **Checkpoint WAL before deletion**:
   ```python
   conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
   ```
   This ensures all changes are committed to main database before deleting WAL files.

2. **Consider disabling WAL for ADG**:
   - ADG is read-only after generation
   - WAL mode provides no benefit for read-only workloads
   - Could switch to DELETE journal mode for simpler file management

---

## Status

- **Root cause identified**: ✅
- **Immediate fix implemented**: ✅ (archive cleanup now deletes WAL files)
- **Verification tests defined**: ✅
- **Prevention measures documented**: ✅
- **Corrective actions executed**: ✅

## Files Modified

1. `tools/generate/generate_full_adg.py`:
   - Modified `_archive_old_artifacts()` to delete `.sqlite-wal` and `.sqlite-shm` files
   - Added WAL file cleanup after main SQLite file deletion (line 1074-1083)

---

## Related Issues

- RCA_SQLITE_FILE_LOCK_ARCHIVE_CLEANUP_20260406.md
- RCA_LOCKED_FILES_MUST_FAIL_GENERATION_20260406.md
- tools/adg/core/sqlite_backend.py (WAL mode enabled here)

---

**Last Updated**: 2026-04-06 04:15 UTC
**Reviewed By**: Cursor Agent AI Assistant
