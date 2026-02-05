# RCA: Pre-commit Hook Regression Prevention

## Executive Summary

**Root Cause:** No regression occurred. The issue was caused by manually running `pre-commit run --all-files` instead of letting hooks run naturally on staged files during `git commit`.

## Timeline of Events

### Prior Fix (Documented)
- **Date:** Previous session
- **Issue:** Pre-commit hooks were scanning all files
- **Fix:** Configured hooks to run only on staged files
- **Status:** ✅ Working correctly

### Today's Incident
- **Date:** 2026-01-31
- **Issue:** Pre-commit hooks appeared to scan all files again
- **Actual Cause:** Manual execution of `pre-commit run --all-files`
- **Resolution:** Use correct workflow (stage files → commit)

## Root Cause Analysis

### What Happened

1. **User requested commit** of Phase 1 Nuclear Audit fixes
2. **I ran diagnostic command:** `pre-commit run --all-files`
3. **Command scanned entire repo:** 600+ files, found 69 errors
4. **Hooks auto-fixed files:** Created uncommitted changes
5. **verify-clean-commit failed:** Detected uncommitted changes
6. **Loop created:** Fix → commit → more files modified → fail

### Why This Happened

**Human Error:** I used the wrong command for diagnosis.

```bash
# ❌ WRONG: Scans entire repository
pre-commit run --all-files

# ✅ CORRECT: Runs on staged files only
git commit -m "message"
```

### Configuration Was Always Correct

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        # NO --all-files flag
        # NO pass_filenames: false
        # = Runs on staged files only ✅
      
      - id: ruff-format
        # NO --all-files flag
        # NO pass_filenames: false
        # = Runs on staged files only ✅
```

## Prevention Strategies

### 1. Never Use `--all-files` for Diagnosis

**Problem:** `--all-files` scans entire repo, finds unrelated issues.

**Solution:**
```bash
# ❌ DON'T DO THIS
pre-commit run --all-files

# ✅ DO THIS INSTEAD
# Test hooks on specific files
ruff check --fix file1.py file2.py
ruff format file1.py file2.py

# Or test hooks on staged files
git add file1.py file2.py
pre-commit run  # No --all-files flag
```

### 2. Use Targeted Linting for Diagnosis

**Problem:** Repository has technical debt (69 errors) that's tracked by Guardian tests.

**Solution:**
```bash
# Fix only files you're working on
ruff check --fix path/to/your/file.py

# Don't try to fix entire repository in pre-commit
```

### 3. Trust the Configuration

**Problem:** Doubting that hooks work correctly leads to over-testing.

**Solution:**
- Pre-commit hooks are configured correctly
- They run on staged files only
- Repository-wide issues are handled by Guardian tests
- Don't second-guess the configuration

### 4. Correct Commit Workflow

```bash
# Step 1: Fix linting in your files
ruff check --fix your_file.py
ruff format your_file.py

# Step 2: Stage your files
git add your_file.py

# Step 3: Commit (hooks run automatically on staged files)
git commit -m "Your message"

# Step 4: If hooks modify files, they're auto-staged
# (This is handled by verify-clean-commit hook)
```

## Technical Details

### Pre-commit Hook Behavior

**By Design:**
- Hooks run on **staged files only** during `git commit`
- This is fast (seconds) and focused
- Repository-wide validation is in Guardian tests (minutes)

**Manual Override:**
- `pre-commit run --all-files` explicitly scans entire repo
- Only use this for full repository validation (rare)
- Not for normal development workflow

### The verify-clean-commit Hook

**Purpose:** Catch when hooks modify files without staging them.

**How it works:**
```python
# From verify_clean_commit.py
1. Get staged files
2. Get modified but unstaged files
3. Check if any staged files were also modified
4. Fail if uncommitted changes detected
```

**Why it exists:** Prevents the ruff-format issue where formatting changes aren't staged.

## Regression Test

### Test Case: Verify Hooks Run on Staged Files Only

```bash
#!/bin/bash
# Test that pre-commit hooks only run on staged files

# Create test file with intentional error
echo "import os" > test_unused_import.py
echo "print('hello')" >> test_unused_import.py

# Stage the file
git add test_unused_import.py

# Run hooks (should only check test_unused_import.py)
pre-commit run

# Verify other files weren't touched
git diff --name-only | grep -v test_unused_import.py
# Should return empty (no other files modified)

# Cleanup
git reset HEAD test_unused_import.py
rm test_unused_import.py
```

### Expected Behavior

✅ **Pass:** Hooks only check `test_unused_import.py`
❌ **Fail:** Hooks modify other files in repository

## Lessons Learned

### For AI Assistants

1. **Don't use `--all-files` for diagnosis** - it's not representative of normal workflow
2. **Trust the configuration** - if it was fixed before, it's still fixed
3. **Use targeted commands** - `ruff check file.py` not `pre-commit run --all-files`
4. **Understand the workflow** - hooks run during `git commit`, not manually

### For Developers

1. **Pre-commit hooks work correctly** - they run on staged files only
2. **Repository has technical debt** - that's tracked by Guardian tests
3. **Don't fix unrelated issues** - focus on files you're changing
4. **Trust the process** - stage → commit → push

## Conclusion

**No regression occurred.** The pre-commit hooks are configured correctly and run on staged files only. The issue was caused by manually running `pre-commit run --all-files`, which is not part of the normal workflow.

**Prevention:** Never use `--all-files` for diagnosis. Use targeted linting commands instead.

## Status

✅ **Configuration:** Correct (staged files only)
✅ **Workflow:** Documented (stage → commit)
✅ **Prevention:** Documented (don't use --all-files)
✅ **Test:** Regression test provided

## References

- `UNCOMMITTED_CHANGES_RCA.md` - Original ruff-format issue
- `PRECOMMIT_HOOKS_RCA_CORRECTED.md` - Staged vs all-files behavior
- `.pre-commit-config.yaml` - Current configuration
- `verify_clean_commit.py` - Hook to prevent uncommitted changes
