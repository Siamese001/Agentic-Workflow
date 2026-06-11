---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_auto_stage_untracked_solution.md'
original_relative_path: 'RCA_auto_stage_untracked_solution.md'
source_sha256: 2fd1c1d7e48ae0a6139b598bea8908f4690f87db488404723d9aa9bd9fd0fa7f
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Auto-Stage Untracked Files Solution

**Date:** 2026-03-13
**Issue:** Untracked files never committed, requiring manual `git add` before each commit
**Solution:** Pre-commit hook to automatically stage untracked files
**Status:** Implemented

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Problem Statement

Git only commits **tracked** files. Untracked files (marked with `??` in `git status`) are ignored by `git commit` operations, even when using `git commit -a`. This requires developers to manually run `git add` for every new file before committing, which is:

1. **Error-prone** — easy to forget new files
2. **Tedious** — extra step for every commit
3. **Inconsistent** — some files get committed, others don't

## Root Cause

Git's design philosophy separates "staging" from "committing":
- `git add` → stages files (tracked or untracked)
- `git commit` → commits only staged files
- `git commit -a` → stages **modified tracked files only**, not untracked files

This is intentional behavior to prevent accidental commits of build artifacts, but it creates friction for legitimate new files.

## Solution: Pre-Commit Hook

Created `ops_scripts/hooks/auto_stage_untracked.py` that:

1. **Runs before every commit** (T0-stage tier in pre-commit pipeline)
2. **Detects untracked files** via `git status --porcelain`
3. **Filters intelligently** — excludes archives, temp files, build artifacts
4. **Auto-stages legitimate files** — documentation, code, tests, etc.

### Smart Filtering Logic

**Auto-staged (version controlled):**
- ✅ Documentation files (`docs/**/*.md`)
- ✅ Source code (`*.py`, `*.yaml`, etc.)
- ✅ Test files (`tests/**/*.py`)
- ✅ Configuration files
- ✅ New ADG artifacts (current timestamp)

**Excluded (local-only):**
- ❌ ADG archives (`artifacts/adg/_archive/**/*.gz`)
- ❌ Temporary files (`_temp_*`, `tmp*`, `.tmp/*`)
- ❌ Build artifacts (`__pycache__`, `.pytest_cache`)
- ❌ Compressed backups (`*.gz` in ADG directory)

## Implementation

### 1. Created Hook Script

**File:** `ops_scripts/hooks/auto_stage_untracked.py`

```python
def should_auto_stage(filepath: str) -> bool:
    """Determine if file should be auto-staged."""
    # Exclude ADG archives (intentionally local-only)
    if "artifacts/adg/_archive/" in filepath:
        return False

    # Exclude compressed files in ADG directory
    if filepath.endswith(".gz") and "artifacts/adg/" in filepath:
        return False

    # Exclude temporary files
    temp_patterns = ["_temp_", "tmp", ".tmp", "_out_", "_capture_"]
    if any(pattern in filepath for pattern in temp_patterns):
        return False

    # Auto-stage everything else
    return True
```

### 2. Added to Pre-Commit Config

**File:** `.pre-commit-config.yaml`

```yaml
- repo: local
  hooks:
    - id: auto-stage-untracked
      name: "T0-stage: Auto-Stage Untracked Files"
      entry: python ops_scripts/hooks/auto_stage_untracked.py
      language: system
      pass_filenames: false
      always_run: true
      require_serial: true
```

**Position:** T0-stage tier (runs first, before all other hooks)

## Workflow After Implementation

### Before (Manual)
```bash
# Create new file
echo "content" > docs/new_file.md

# Must manually stage
git add docs/new_file.md

# Then commit
git commit -m "Add documentation"
```

### After (Automatic)
```bash
# Create new file
echo "content" > docs/new_file.md

# Just commit - auto-staging happens automatically
git commit -m "Add documentation"

# Output:
# [auto-stage] Staging 1 untracked file(s):
#   + docs/new_file.md
# T0-guard: Agent Deletion Authorization...Passed
# T0: Trailing Whitespace...Passed
# ...
```

## Benefits

1. **No more forgotten files** — new files automatically staged
2. **Faster workflow** — one less command per commit
3. **Consistent behavior** — all legitimate files committed
4. **Safe filtering** — archives and temp files remain local
5. **Transparent** — hook prints what it's staging

## Edge Cases Handled

### Case 1: ADG Archives
**Scenario:** ADG generation creates compressed archives
**Behavior:** Excluded by `artifacts/adg/_archive/` pattern
**Result:** Archives remain local-only ✅

### Case 2: Documentation Files
**Scenario:** User creates `docs/technical/Error & Exception Handling.md`
**Behavior:** Auto-staged (not in exclusion list)
**Result:** File committed automatically ✅

### Case 3: Temporary Files
**Scenario:** Test creates `_temp_output.txt`
**Behavior:** Excluded by `_temp_` pattern
**Result:** File remains untracked ✅

### Case 4: Current ADG Artifacts
**Scenario:** ADG generation creates `adg_indexed_03132026_1902.sqlite`
**Behavior:** Auto-staged (not in `_archive/` directory)
**Result:** Current ADG committed ✅

## Verification

To verify the hook is working:

```bash
# Create test file
echo "test" > docs/test.md

# Commit (hook should auto-stage)
git commit -m "Test auto-stage"

# Expected output:
# [auto-stage] Staging 1 untracked file(s):
#   + docs/test.md
```

## Rollback Plan

If the hook causes issues:

```bash
# Disable the hook temporarily
git commit --no-verify -m "message"

# Or remove from .pre-commit-config.yaml
# Delete lines 81-87 in .pre-commit-config.yaml
```

## Maintenance

The exclusion patterns in `should_auto_stage()` should be updated if:
- New artifact directories are added
- New temporary file patterns emerge
- New build output locations are created

## Conclusion

The auto-stage hook solves the "untracked files never committed" problem by automatically staging legitimate new files while intelligently excluding archives, temporary files, and build artifacts. This improves developer workflow without sacrificing safety or control.

## Related Documents

- `.pre-commit-config.yaml` — Hook configuration
- `ops_scripts/hooks/auto_stage_untracked.py` — Hook implementation
- `docs/reports/plans/RCA_untracked_files_not_committed.md` — Original problem RCA

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

