---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_untracked_files_not_committed.md'
original_relative_path: 'RCA_untracked_files_not_committed.md'
source_sha256: fffc8e69f1b03325a1035620e8336350990b0f661054fa3b45b99de515243c1f
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Untracked Files Never Committed

**Date:** 2026-03-13
**Incident:** Untracked files remained uncommitted after git commit operation
**Severity:** Low (documentation/archive files)

## Root Cause

Git only commits **tracked** files (files that have been explicitly added with `git add`). Untracked files are ignored by `git commit` operations.

## Evidence

From `git status --porcelain` output after commit:

```
?? artifacts/adg/_archive/2026-03/adg_file_graph_03132026_1731.json.gz
?? artifacts/adg/_archive/2026-03/adg_file_graph_03132026_1803.json.gz
?? artifacts/adg/_archive/2026-03/adg_governance_graph_03132026_1731.json.gz
?? artifacts/adg/_archive/2026-03/adg_governance_graph_03132026_1803.json.gz
?? artifacts/adg/_archive/2026-03/adg_graphsnap_03132026_1731.json.gz
?? artifacts/adg/_archive/2026-03/adg_graphsnap_03132026_1803.json.gz
?? artifacts/adg/_archive/2026-03/adg_indexed_03132026_1731.sqlite.gz
?? artifacts/adg/_archive/2026-03/adg_indexed_03132026_1803.sqlite.gz
?? artifacts/adg/_archive/2026-03/adg_run_03132026_1731.zip.gz
?? artifacts/adg/_archive/2026-03/adg_run_03132026_1803.zip.gz
?? artifacts/adg/_archive/2026-03/adg_snapshot_03132026_1731.json.gz
?? artifacts/adg/_archive/2026-03/adg_snapshot_03132026_1803.json.gz
?? artifacts/adg/_archive/2026-03/adg_symbol_graph_03132026_1731.json.gz
?? artifacts/adg/_archive/2026-03/adg_symbol_graph_03132026_1803.json.gz
?? "docs/technical/Error & Exception Handling.md"
```

The `??` prefix indicates **untracked** files.

## Why These Files Were Untracked

### 1. ADG Archive Files (`artifacts/adg/_archive/2026-03/*.gz`)
- **Created by:** ADG generation script's automatic archival process
- **Purpose:** Compressed backups of previous ADG runs
- **Why untracked:** Likely in `.gitignore` to prevent bloating repository with large binary archives
- **Expected behavior:** Archives are local-only, not version controlled

### 2. Documentation File (`docs/technical/Error & Exception Handling.md`)
- **Created by:** User or previous session
- **Why untracked:** Never explicitly added with `git add`
- **Expected behavior:** Should be added if intended for version control

## Git Workflow Explanation

```
Untracked → Staged → Committed
   ??         M         [committed]

   ↓ git add

Untracked → Staged → Committed
            A         [committed]
```

**Key Point:** Files must be in "Staged" state (via `git add`) before `git commit` will include them.

## What Actually Committed

From commit output:
```
[ADG_v7 9939f48d76] Confidence routing consolidation - unified system with 0 skipped tests
 23 files changed, 680860 insertions(+), 679313 deletions(-)
```

Only the 23 **staged** files were committed:
- 10 modified Python source files
- 6 ADG artifacts (renamed/updated)
- 5 new test/diagnostic files
- 1 modified documentation file
- 1 deleted CSV file

## Resolution Options

### Option 1: Intentionally Ignore (Recommended for Archives)
Archives should remain local-only. Verify `.gitignore` contains:
```gitignore
artifacts/adg/_archive/
*.gz
```

### Option 2: Add Documentation File
If `Error & Exception Handling.md` should be version controlled:
```bash
git add "docs/technical/Error & Exception Handling.md"
git commit -m "Add error handling documentation"
git push
```

### Option 3: Add All Untracked (Use Carefully)
```bash
git add .
git status  # Review what will be committed
git commit -m "Add remaining files"
```

## Prevention

1. **Always review `git status`** before committing
2. **Use `git add -A`** to stage all changes (tracked + untracked)
3. **Use `git add .`** to stage all in current directory
4. **Use `git add <file>`** for selective staging
5. **Maintain `.gitignore`** for files that should never be tracked

## Conclusion

**This is expected behavior, not a bug.** Git correctly committed only the files that were explicitly staged. The untracked archive files should remain untracked per `.gitignore` rules. The documentation file can be added in a follow-up commit if needed.

## Action Items

- [ ] Verify `.gitignore` includes `artifacts/adg/_archive/` pattern
- [ ] Decide if `Error & Exception Handling.md` should be committed
- [ ] Document git workflow expectations for team

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

