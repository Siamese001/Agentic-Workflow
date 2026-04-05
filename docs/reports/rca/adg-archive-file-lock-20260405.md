# RCA: ADG Archive File Lock Error

## Incident Summary
**Date:** 2026-04-05  
**Error:** `[WinError 32] The process cannot access the file because it is being used by another process: 'C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04052026_1842.sqlite'`  
**Component:** ADG Archiving (`tools/archive/archive_old_adg.py`)  
**Severity:** Medium (blocks ADG cleanup operations)

## Root Cause Analysis

### Direct Cause
The archiving script `archive_old_adg.py` attempted to delete `adg_indexed_04052026_1842.sqlite` after compressing it, but the file was locked by the ADG MCP server process (line 238: `file_path.unlink()`).

### Contributing Factors
1. **No Active Database Check:** The script does not query ADG health to identify the currently active database before attempting deletion
2. **No File Lock Detection:** No mechanism to detect if a file has open handles before attempting deletion
3. **WAL Mode Locking:** SQLite databases in WAL mode (with `-shm` and `-wal` files) maintain file locks that prevent deletion while connections are active

### Evidence
- ADG health check shows: `adg_snapshot_id: "04052026_1842"` (the locked file is the active database)
- File system shows WAL files present: `adg_indexed_04052026_1842.sqlite-shm`, `adg_indexed_04052026_1842.sqlite-wal`
- The archiving script at line 238 performs unconditional `file_path.unlink()` without checking if the file is in use

## Impact
- ADG cleanup operations fail when attempting to archive the currently active database
- Manual intervention required to identify and skip locked files
- Potential accumulation of old ADG artifacts if cleanup is blocked

## Corrective Actions

### Action 1: Add ADG Health Check Integration
**Status:** ✅ COMPLETE
**Description:** Modify `archive_old_adg.py` to query ADG health to identify the active database timestamp. Skip archiving of the active database.

**Implementation:**
- Added `_get_active_adg_timestamp()` function to read ADG snapshot files and identify active database
- Added `active_timestamp` parameter to `archive_run()` function
- Files matching the active timestamp are skipped with clear logging

### Action 2: Add File Lock Detection
**Status:** ✅ COMPLETE
**Description:** Add a Windows-compatible file lock detection mechanism before attempting file deletion.

**Implementation:**
- Added `_is_file_locked()` function that checks for SQLite WAL files (`.sqlite-wal`, `.sqlite-shm`)
- On Windows, attempts exclusive file open to detect locks
- On Unix, relies on WAL file detection
- Locked files are skipped with warning logging

### Action 3: Improve User Feedback
**Status:** ✅ COMPLETE
**Description:** Add clear messaging when files are skipped due to locks or active database status.

**Implementation:**
- Added `files_skipped` and `skip_reasons` to statistics tracking
- Active timestamp is displayed at startup
- Skip reasons are logged during processing
- Summary includes skipped file count and detailed reasons

## Resolution Status
**Status:** ✅ RESOLVED
**Last Updated:** 2026-04-05 19:25 UTC

## Verification
After corrective actions:
1. ✅ Ran `python tools/archive/archive_old_adg.py --keep-runs 1` (dry run)
2. ✅ Active database (04052026_1917) was detected and displayed
3. ✅ Locked file (04052026_1842.sqlite) was detected via WAL file check
4. ✅ Locked file was skipped with clear warning message
5. ✅ Summary showed 1 file skipped with detailed reason
6. ✅ No WinError 32 exceptions occurred

**Test Output:**
```
[ADG Archive] Active ADG timestamp: 04052026_1917
[ADG Archive] Files with this timestamp will be skipped
...
Skipping adg_indexed_04052026_1842.sqlite: file locked by another process
    → 0 files archived, 1 files skipped (locked or active)
...
[ADG Archive] Skipped files (reasons):
    - adg_indexed_04052026_1842.sqlite: file locked by another process
```

## Artifacts
- RCA Document: `` `@c:\Git\Agentic-Workflow\docs\reports\rca\adg-archive-file-lock-20260405.md` ``
- Fixed Script: `` `@c:\Git\Agentic-Workflow\tools\archive\archive_old_adg.py` ``
- Evidence: ADG health check output showing active database (04052026_1842)
- Test Output: Dry-run verification showing locked file detection and skip behavior
