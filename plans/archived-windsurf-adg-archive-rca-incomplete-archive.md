---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-archive-rca-incomplete-archive.md'
original_relative_path: 'adg-archive-rca-incomplete-archive.md'
source_sha256: df08a758ca76ca57693e86a6ea05670e24db5831c8748f2b3bf8d03f82aadf7d
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: ADG Archive Cleanup - Incomplete Initial Archive

**Date:** 2026-04-05  
**Status:** RESOLVED  
**Severity:** Medium (operational hygiene issue)

## Executive Summary

The initial ADG archive run failed to archive all old files due to multiple bugs in `tools/archive/archive_old_adg.py`. Three categories of files were missed:
1. Report files (not matching `adg_*` prefix)
2. ZIP files (no pattern in glob list)
3. Files requiring updated timestamp parsing (new format with time suffixes)

## Root Causes

### 1. Incomplete Glob Patterns (PRIMARY)

**Location:** `@C:\Git\Agentic-Workflow\tools\archive\archive_old_adg.py:190-192`

**Problem:** The file discovery patterns only matched:
- `adg_*.json`, `adg_*.sqlite`, `adg_*.md`, `adg_repair_*.json`

**Missed files:**
- `boundary_report_*.json`
- `test_surface_coverage_*.json`
- `mutation_integrity_report_*.json`
- `closure_validation_report_*.json`
- `edge_density_report_*.json`
- `provenance_report_*.json`
- `replay_determinism_report_*.json`
- `layer_coverage_report_*.json`
- `repair_log_*.json`
- `execution_impact_*.json`
- `scan_result_cache.json`
- `adg_*.zip` (run archives)

**Fix Applied:**
```python
# BEFORE:
for pattern in ["adg_*.json", "adg_*.sqlite", "adg_*.md", "adg_repair_*.json"]:

# AFTER:
for pattern in ["adg_*.json", "adg_*.sqlite", "adg_*.md", "adg_repair_*.json",
                "*_report_*.json", "test_surface_coverage_*.json", "*_log_*.json",
                "execution_impact_*.json", "repair_log_*.json", "scan_result_cache.json",
                "adg_*.zip"]:
```

### 2. Timestamp Extraction Failure for New Format

**Location:** `@C:\Git\Agentic-Workflow\tools\archive\archive_old_adg.py:97-137`

**Problem:** Original extraction logic assumed timestamp was always the last underscore-separated component:
```python
# OLD (broken for new format):
ts_with_ext = parts[-1]
ts = ts_with_ext.split(".")[0]
if len(ts) == 8 and ts.isdigit():
    return ts
```

**Failed on:**
- `adg_indexed_04052026_1133.sqlite` → extracted `1133` instead of `04052026_1133`
- `adg_indexed_04052026_1133_probe.sqlite` → extracted `probe` (invalid)

**Fix Applied:**
```python
# NEW (scans for 8-digit date pattern):
for i, part in enumerate(parts):
    if len(part) == 8 and part.isdigit():  # Found MMDDYYYY
        remaining_parts = parts[i:]
        remaining_parts[-1] = remaining_parts[-1].split(".")[0]
        return "_".join(remaining_parts)
```

### 3. Timestamp Parsing Failure for Suffix Format

**Location:** `@C:\Git\Agentic-Workflow\tools\archive\archive_old_adg.py:140-164`

**Problem:** `_parse_timestamp()` didn't handle timestamps with underscores like `04042026_1942`.

**Fix Applied:**
```python
# Added handling for underscore-separated timestamps:
if "_" in ts:
    ts_parts = ts.split("_")
    date_part = ts_parts[0]
    if len(date_part) == 8 and date_part.isdigit():
        return datetime.strptime(date_part, "%m%d%Y")
```

### 4. Broken Import Path (Blocking Issue)

**Location:** `@C:\Git\Agentic-Workflow\tools\archive\archive_old_adg.py:36-74`

**Problem:** Script had non-existent imports:
```python
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_pulls_context, ...
)
```

Module `L_CONTRACTS` doesn't exist in `agentic_core`.

**Fix Applied:** Removed all broken imports and associated ADG edge emission code. These were non-functional instrumentation calls that blocked script execution.

## Impact Assessment

### Files Missed in Initial Archive
| Category | Count | Size |
|----------|-------|------|
| JSON reports | ~20 | ~55 KB |
| ZIP files | 2 | 91 MB |
| SQLite files | 1 | 199 MB |
| execution_impact files | 6 | ~5 KB |

### Final Archive Result (After Fixes)
| Pass | Runs Archived | Files | Original Size | Compressed |
|------|---------------|-------|---------------|------------|
| 1 | 1 | 1 | 198.6 MB | 34.9 MB |
| 2 | 3 | 18 | 1.2 GB | 137.0 MB |
| 3 | 1 | 6 | 414.5 MB | 45.4 MB |
| 4 | 8 | 23 | 55.5 KB | 16.5 KB |
| 5 | 2 | 2 | 91.1 MB | 91.1 MB |
| **Total** | **15** | **50** | **~2 GB** | **~325 MB** |

## Remediation

All fixes applied to `@C:\Git\Agentic-Workflow\tools\archive\archive_old_adg.py`:

1. **Line 36-74:** Removed broken imports and ADG emission code
2. **Line 78:** Fixed `parents[1]` → `parents[2]` for ROOT calculation
3. **Line 97-137:** Rewrote `_extract_timestamp()` for new format support
4. **Line 140-164:** Updated `_parse_timestamp()` for underscore timestamps
5. **Line 150-153:** Added comprehensive glob patterns for all file types

## Verification

**Final state of `artifacts/adg/`:**
- Only 1 run retained: `04052026_1133` (latest)
- All files from older runs archived to `artifacts/adg/_archive/2026-04/`
- **No old files remaining** in primary ADG directory

**Archive verification:**
```powershell
# Verify no old timestamps remain
Get-ChildItem artifacts/adg/ -File | Where-Object { $_.Name -match '04042026' }
# Returns: (empty - no matches)
```

## Prevention

1. **Archive script maintenance:** Update glob patterns when new artifact types are added
2. **Timestamp format stability:** Document and version timestamp formats in ADG generation
3. **Test coverage:** Add dry-run archive verification to CI

---
**Status:** RESOLVED ✅  
**Evidence:** Archive directory contains 39+ compressed files totaling 1.15 GB  
**Primary directory:** Clean - only latest run (04052026_1133) retained
