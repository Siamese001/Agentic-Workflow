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

