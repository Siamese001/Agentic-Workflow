# Hygiene Cleanup Guide

## Overview

The hygiene validation system detects and helps clean up code rot in the `agentic_core` folder:
1. **Dead Code**: Orphaned files that are never imported
2. **Duplicates**: Files with identical content

## Current Status

**Total Hygiene Issues**: 774
- ~770 dead code files (orphaned, never imported)
- ~4 duplicate files

## Tools Available

### 1. Hygiene Validator (Detection)
**Location**: `agentic_core/L0_maintenance/scripts/hygiene_validator.py`

**Usage**:
```bash
python agentic_core/L0_maintenance/scripts/hygiene_validator.py agentic_core
```

**Output**:
- Lists all duplicate files with hash
- Lists all orphaned files (never imported)
- Total issue count

### 2. Hygiene Pruner (Interactive Cleanup)
**Location**: `agentic_core/L0_maintenance/scripts/prune_hygiene_issues.py`

**Usage**:
```bash
python agentic_core/L0_maintenance/scripts/prune_hygiene_issues.py
```

**Features**:
- **Interactive**: Prompts before deleting any file
- **Safe**: Shows file size and location before deletion
- **Bulk operations**: Offers to delete all orphans in a directory at once
- **Summary**: Reports deleted and skipped files

## Cleanup Workflow

### Phase 1: Duplicate Resolution

The pruner will:
1. Show each set of duplicate files
2. Display file paths and sizes
3. Ask which file to keep (others will be deleted)
4. Allow skipping if unsure

**Example**:
```
Set 1/4 (Hash: a1b2c3d4...)
  [0] utils/core_extensions/fix_imports.py (1234 bytes)
  [1] utils/core_extensions/P1_core_fix_imports.py (1234 bytes)

Enter the index of the file to KEEP (0-1), or 's' to skip: 0
  [DELETED] utils/core_extensions/P1_core_fix_imports.py
  -> Kept: utils/core_extensions/fix_imports.py
```

### Phase 2: Orphan Removal

The pruner will:
1. Group orphans by directory
2. Offer bulk delete for directories with 5+ orphans
3. Prompt individually for each file
4. Show file size before deletion

**Example**:
```
Directory: utils/core_extensions (150 orphans)
Delete all 150 orphans in this directory? [y/N]: y
  [DELETED] utils/core_extensions/fix_gravity_breaches.py
  [DELETED] utils/core_extensions/fix_gravity_violations.py
  ...
```

## Safety Features

1. **Confirmation Required**: Every deletion requires user approval
2. **File Size Display**: See file size before deleting
3. **Skip Option**: Can skip any file or directory
4. **Summary Report**: Shows what was deleted vs skipped
5. **No Auto-Delete**: Never deletes without explicit permission

## Recommendations

### High Priority (Safe to Delete)

**1. Renamed Files from SSOT Enforcement** (~67 files)
These files were renamed with folder prefixes during SSOT enforcement and are duplicates:
- `P1_core___init__.py`
- `P2_helpers___init__.py`
- `naming___init__.py`
- etc.

**Action**: Delete all renamed files, keep originals

**2. Old Migration Scripts** (~50 files in `L0_maintenance/scripts`)
One-off scripts used during previous refactorings:
- `fix_*.py`
- `move_*.py`
- `align_*.py`
- `force_*.py`

**Action**: Archive to `archives/deprecated_code` or delete

**3. Utility Scripts in `utils/core_extensions`** (~150 files)
Temporary fix scripts that are no longer needed:
- `fix_gravity_breaches.py`
- `fix_mission_runner.py`
- `flatten_annexed_territories.py`
- etc.

**Action**: Archive or delete after review

### Medium Priority (Review First)

**1. Duplicate `__init__.py` Files**
Some `__init__.py` files may be legitimately empty or similar.

**Action**: Review before deleting

**2. Scripts in Active Use**
Some scripts may be used by CI/CD or manual workflows.

**Action**: Check git history and usage before deleting

### Low Priority (Keep)

**1. Entry Points**
Files like `main.py`, `setup.py`, `conftest.py` are automatically excluded.

**2. Test Files**
Files in `tests/` or with `test_` prefix are automatically excluded.

**3. Scripts**
Files in `scripts/` directories are automatically excluded.

## Warnings

### Static Analysis Limitations

The orphan detection uses static analysis which may miss:
- **Dynamic imports**: `importlib.import_module(variable)`
- **String references**: `__import__('module_name')`
- **Conditional imports**: `if condition: import module`
- **Plugin systems**: Modules loaded via configuration

**Recommendation**: Review carefully before deleting. Check git history to see if file was recently used.

### False Positives

Files may be flagged as orphans if they are:
- Imported via dynamic mechanisms
- Used as CLI entry points
- Loaded by external tools
- Part of plugin architecture

**Recommendation**: When in doubt, skip the file. You can always delete it later.

## Example Session

```bash
$ python agentic_core/L0_maintenance/scripts/prune_hygiene_issues.py

Target directory: C:\Git\Agentic-Workflow\agentic_core
This script will help you clean up dead code and duplicates.
You will be prompted before any files are deleted.

Continue with hygiene pruning? [Y/n]: y

Scanning C:\Git\Agentic-Workflow\agentic_core for hygiene issues...

======================================================================
PHASE 1: DUPLICATE RESOLUTION
======================================================================
Found 4 sets of duplicate files.

Set 1/4 (Hash: a1b2c3d4...)
  [0] utils/core_extensions/fix_imports.py (1234 bytes)
  [1] utils/core_extensions/P1_core_fix_imports.py (1234 bytes)

Enter the index of the file to KEEP (0-1), or 's' to skip: 0
  [DELETED] utils/core_extensions/P1_core_fix_imports.py
  -> Kept: utils/core_extensions/fix_imports.py

...

======================================================================
PHASE 2: ORPHAN REMOVAL
======================================================================
Found 770 potential orphaned files (never imported).
WARNING: Static analysis may miss dynamic imports (e.g. importlib, string refs).
Review carefully before deleting.

Directory: utils/core_extensions (150 orphans)
Delete all 150 orphans in this directory? [y/N]: y
  [DELETED] utils/core_extensions/fix_gravity_breaches.py
  [DELETED] utils/core_extensions/fix_gravity_violations.py
  ...

======================================================================
HYGIENE PRUNING SUMMARY
======================================================================
Files deleted: 154
Files skipped: 620
Total reviewed: 774

=== HYGIENE PRUNING COMPLETE ===
```

## Post-Cleanup

After running the pruner:

1. **Re-run validation** to verify cleanup:
   ```bash
   python agentic_core/L0_maintenance/scripts/hygiene_validator.py agentic_core
   ```

2. **Run structural validation** to ensure no breakage:
   ```bash
   python run_agentic_core_validation.py
   ```

3. **Test the application** to ensure nothing broke

4. **Commit changes** with descriptive message:
   ```bash
   git add -A
   git commit -m "chore: remove dead code and duplicates (774 files cleaned)"
   ```

## Best Practices

1. **Start Small**: Test on a small directory first
2. **Review Carefully**: Don't rush through deletions
3. **Check Git History**: See when file was last modified
4. **Keep Backups**: Commit before running pruner
5. **Test After**: Run tests to ensure nothing broke
6. **Document**: Note any files you intentionally kept

## Troubleshooting

### "File not found" errors
The file may have already been deleted or moved. Skip and continue.

### "Permission denied" errors
File may be in use. Close applications and try again.

### Accidentally deleted important file
Use git to restore:
```bash
git checkout HEAD -- path/to/file.py
```

## Summary

The hygiene pruner is a powerful tool for cleaning up code rot. Use it carefully and review each deletion. When in doubt, skip the file - you can always delete it later after more investigation.

**Estimated cleanup time**: 30-60 minutes for 774 files (with bulk operations)
**Recommended approach**: Delete duplicates first, then review orphans directory by directory
