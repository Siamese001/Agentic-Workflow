---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\pre-commit-staging-rca-20260408.md'
original_relative_path: 'pre-commit-staging-rca-20260408.md'
source_sha256: c9f043ded204a830eaede873ecf04d85ba9c65f5e7c3c2344a90169ef7b986fe
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Pre-commit Auto-fixes Not Staged in Commits

**Date**: 2026-04-08  
**Status**: RESOLVED  
**Severity**: MEDIUM  

## Executive Summary

Pre-commit hooks auto-fixed 100+ files during commits, but these fixes were not included in the final commits. The issue stems from pre-commit's stashing mechanism during hook execution, which auto-fixes files but doesn't automatically add them to the commit staging area.

## Issue Description

**Observed Behavior**:
- Git diff between commits shows 100+ files changed
- Actual commits only contain `.pre-commit-config.yaml`
- Pre-commit hooks (T0a-d) are auto-fixers that modify files
- Auto-fixed files remain unstaged after commit

**Impact**:
- Repository drift: working directory has fixes not in commits
- CI may fail due to unstaged formatting fixes
- Inconsistent code style between local and remote

## Root Cause Analysis

### Primary Cause: Pre-commit Stashing Behavior

1. **Pre-commit execution flow**:
   ```
   git commit → pre-commit stashes unstaged changes → runs hooks → auto-fixes files → restores stash → commit completes
   ```

2. **Auto-fixer hooks involved**:
   - **T0a**: `trailing-whitespace` - removes trailing spaces
   - **T0b**: `end-of-file-fixer` - adds final newline
   - **T0c**: `mixed-line-ending` - converts to LF line endings
   - **T3**: `ruff-format` - reformats Python code

3. **The gap**: Auto-fixed files are modified **after** the initial staging but **before** the commit completes. Pre-commit doesn't automatically re-stage these modifications.

### Secondary Factors

1. **Exclude patterns**: T0a-d exclude `.md$` files, creating inconsistent application
2. **Large file count**: Many test artifact files (`*.json`, `__init__.py`) needed formatting fixes
3. **No explicit re-staging**: User expected auto-fixes to be included automatically

## Evidence

### Git History Analysis
```bash
# Shows only config file in commits
git show --name-only HEAD
→ .pre-commit-config.yaml

# But diff shows 100+ files actually changed
git diff HEAD~1 --name-only | wc -l
→ 100+ files
```

### Pre-commit Configuration
```yaml
# Auto-fixer hooks that modify files
- id: trailing-whitespace    # T0a
- id: end-of-file-fixer      # T0b  
- id: mixed-line-ending      # T0c
- id: ruff-format           # T3
```

## Resolution Applied

### Immediate Fix (Applied)
1. **Committed auto-fixed files**: Added all modified files to capture the formatting fixes
2. **Pushed to GitHub**: Ensured remote repository has consistent formatting

### Long-term Prevention
1. **User education**: Understand that pre-commit auto-fixes require explicit staging
2. **Workflow adjustment**: After pre-commit runs with fixes, run `git add .` before commit
3. **Consider `--no-verify`**: For commits where auto-fixes are not desired

## Corrective Actions

### ✅ COMPLETED
- [x] Identified root cause (pre-commit stashing behavior)
- [x] Committed all auto-fixed files to sync repository state
- [x] Pushed changes to GitHub to resolve drift
- [x] Documented RCA for future reference

### 📋 RECOMMENDED PRACTICES
1. **After pre-commit auto-fixes**: Always run `git add .` then `git commit --amend` or create new commit
2. **Check commit scope**: Use `git diff --cached` before committing to verify staged files
3. **Batch formatting**: Run `pre-commit run --all-files` before major commits to minimize in-commit fixes

## Technical Details

### Pre-commit Hook Types
- **Auto-fixers**: Modify files (T0a-d, T3)
- **Validators**: Check only, no modifications (T1, T4, T5-T7)

### File Categories Affected
- **Python files**: Trailing whitespace, EOF newlines, formatting
- **JSON files**: EOF newlines, line endings
- **Test artifacts**: Index files, snapshot files

### Staging Behavior
```bash
# Pre-commit internal flow (simplified)
1. git stash push --keep-index
2. Run hooks on staged files
3. Auto-fixers modify files in working directory
4. git stash pop
5. git commit (only original staged files)
```

## Lessons Learned

1. **Pre-commit auto-fixes are not automatically staged**
2. **Large-scale formatting changes should be committed separately**
3. **Always verify commit contents with `git show --name-only`**
4. **Consider pre-commit as a quality gate, not a commit formatter**

## Status: RESOLVED

All auto-fixed files have been committed and pushed to GitHub. Repository state is now consistent between local and remote. Future commits should follow the recommended practices to avoid this issue.

---

**Next Review**: None required  
**Related Issues**: None  
**Tags**: pre-commit, git-staging, auto-fix, formatting
