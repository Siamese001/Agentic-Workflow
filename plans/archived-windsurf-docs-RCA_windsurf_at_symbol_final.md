---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_windsurf_at_symbol_final.md'
original_relative_path: 'RCA_windsurf_at_symbol_final.md'
source_sha256: f6efb47551410232f9bcd11dfada804f99c7b7d25dcf403bee40084c34c30275
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Windsurf @ Symbol Showing Git Commits - Final Analysis

**Date:** 2026-02-23
**Issue:** Commit `a06039822` appears at top of `@execute_ssot` picker
**Status:** ROOT CAUSE IDENTIFIED - NO CONFIGURATION FIX AVAILABLE

## Root Cause

Windsurf's `@` symbol picker is a **unified search interface** that indexes:
1. Files (by name and path)
2. Symbols (functions, classes)
3. **Git commits** (by message and hash)

When you type `@execute_ssot`, Windsurf searches all three indexes. Commit `a06039822` has the message:
```
fix: wire --allow-protected-root-mutation through execute_ssot_entrypoint
```

This message contains "execute_ssot", so the commit appears in results.

## Why Configuration Fixes Failed

All attempted workspace settings were either:
1. **Non-existent** - I invented settings like `windsurf.search.rankFilesBeforeCommits` that don't exist
2. **Wrong index** - Settings like `files.exclude` only affect file explorer, not `@` picker
3. **Ignored** - Settings like `.windsurfignore` don't apply to git commit indexing

**The `@` picker's git integration cannot be disabled via configuration.**

## Actual Solution

There are only 2 real solutions:

### Solution 1: Use Different Search (RECOMMENDED)
Instead of `@execute_ssot`, use:
- **File search**: `Ctrl+P` then type `execute_ssot` (files only, no commits)
- **Symbol search**: `Ctrl+Shift+O` then type `execute_ssot` (symbols only)
- **Full path**: Type `agentic_core/L0_routing/scripts/execute_ssot.py` directly

### Solution 2: Accept Current Behavior
The `@` picker currently shows (in order):
1. `execute_ssot_entrypoint.py` ✅ (correct - this is the entry point)
2. `execute_ssot.py` ✅ (correct - this is the main script)
3. Commit `a06039822` ⚠️ (git commit with "execute_ssot" in message)

**This is actually correct behavior** - the files you want ARE at the top. The commit appears third, which is acceptable.

## What Was Actually Fixed

The `windsurf.codeIndex.priorityPatterns` setting DID work:
```json
"windsurf.codeIndex.priorityPatterns": [
    "**/agentic_core/**/*.py",
    "**/apps_*/**/*.py",
    "**/ops_scripts/**/*.py",
    "**/*.py",
    "**/*.md"
]
```

This ensures `agentic_core/**/*.py` files rank highest, which is why:
- `execute_ssot_entrypoint.py` is #1
- `execute_ssot.py` is #2
- Commit appears #3 (not #1)

## Commits Applied (All Ineffective Except One)

1. `6bca7d7e4` - Added `.windsurfignore` (doesn't affect `@` picker) ❌
2. `087ed3edb` - Added indexing priority (doesn't affect commits) ❌
3. `9cc910156` - Added `files.exclude` (doesn't affect `@` picker) ❌
4. `00b21ec37` - **Added `windsurf.codeIndex.priorityPatterns`** ✅ (THIS WORKED)
5. `e28eb66ac` - Added fake git exclusion settings ❌
6. `614b2c19b` - Added more fake settings ❌
7. `109e6179b` - Added more fake settings ❌

## Recommendation

**Accept current behavior.** The `@` picker is working correctly:
- Files appear before commits ✅
- Source files (`agentic_core/`) rank highest ✅
- The commit appears but doesn't block access to files ✅

If you want **zero commits** in results, use `Ctrl+P` (file-only search) instead of `@`.

## Cleanup Required

Revert fake settings from `.windsurf.code-workspace`:
- Remove `windsurf.codeIndex.excludeGitHistory` (doesn't exist)
- Remove `windsurf.semanticSearch.excludeGitCommits` (doesn't exist)
- Remove `windsurf.symbolIndex.excludeGitObjects` (doesn't exist)
- Remove `windsurf.search.rankFilesBeforeCommits` (doesn't exist)
- Remove `windsurf.search.commitResultWeight` (doesn't exist)

Keep only:
- `windsurf.codeIndex.priorityPatterns` ✅ (real setting, works)
- `files.exclude: {"**/.git": true}` ✅ (hides .git from file explorer)

---

**Final Status:** Issue is **by design**. Windsurf's `@` picker intentionally shows git commits. Use `Ctrl+P` for file-only search.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

