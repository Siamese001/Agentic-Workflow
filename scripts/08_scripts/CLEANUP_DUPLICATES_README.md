# Duplicate File Cleanup Tool

## Overview

This tool detects and removes runaway refactoring artifacts across the Agentic-Workflow project:

- Files with version suffixes: `_2`, `_3`, `_4`, `_5`, etc.
- Files with part suffixes: `_part_2`, `_part_3`, etc.
- Legacy version files: `_v11_2`, `_v11_3`, etc.

## Current State (December 2025)

**Scan Results:**
- **130+ duplicate files** found across the project
- **~81 files** with `_2` suffix
- **~22 files** with `_3` suffix  
- **~40 files** with `_4` suffix
- **~40 files** with `_5` suffix
- **~9 files** with `_part_2` suffix

**Affected Directories:**
- `config/` - Multiple `config_models_2.py`, `config_models_3.py`
- `apps_lic/` - Route models, archetype models
- `apps_rg/` - Brief models, workflow types
- `shared/` - Config types, exception implementations
- `archives/` - Legacy versioned files (v10.2, v6.3, etc.)

## Files

1. **`cleanup_duplicate_files.py`** - Main Python script (Docker-safe)
2. **`cleanup_duplicate_files.sh`** - Bash wrapper for Docker execution
3. **`CLEANUP_DUPLICATES_README.md`** - This documentation

## Usage

### Mode 1: SCAN (Safe - Read-Only)

Analyze and report duplicates without making any changes.

```bash
# Docker execution (recommended)
bash 08_scripts/cleanup_duplicate_files.sh

# Direct Python (if outside Docker)
python 08_scripts/cleanup_duplicate_files.py --mode scan --root /workspace
```

**Output:**
- Console report with statistics
- `duplicate_scan_report.json` - Detailed JSON report

### Mode 2: DELETE IDENTICAL (Safe)

Delete only files that are **byte-for-byte identical** to their originals.

```bash
# Dry run (shows what would be deleted)
bash 08_scripts/cleanup_duplicate_files.sh --delete-identical

# Real deletion (creates backup first)
bash 08_scripts/cleanup_duplicate_files.sh --delete-identical --no-dry-run
```

### Mode 3: DELETE ALL (Dangerous)

Delete **ALL** duplicates, including files with different content.

```bash
# Dry run
bash 08_scripts/cleanup_duplicate_files.sh --delete-all

# Real deletion (requires double confirmation)
bash 08_scripts/cleanup_duplicate_files.sh --delete-all --no-dry-run
```

## Safety Features

### 1. Dry Run by Default
All deletion operations default to `--dry-run` mode, showing what would be deleted without actually deleting.

### 2. Automatic Backups
Before any real deletion, all files are backed up to:
```
archives/cleanup_backup_YYYYMMDD_HHMMSS/
```

### 3. Confirmation Prompts
Real deletions require explicit confirmation:
- Shell script: Type `YES` to proceed
- Python script (delete-all): Type `DELETE ALL` to proceed

### 4. Excluded Directories
The scanner automatically excludes:
- `__pycache__/`
- `.git/`
- `node_modules/`
- `.venv/`, `venv/`
- `.pytest_cache/`, `.mypy_cache/`
- `dist/`, `build/`, `eggs/`, `*.egg-info/`

## Detection Logic

### Pattern Matching
The script detects duplicates using regex patterns:

1. **Numeric suffix**: `_(\d+)\.` → Matches `file_2.py`, `file_3.py`
2. **Part suffix**: `_part_(\d+)\.` → Matches `file_part_2.py`
3. **Legacy version**: `_v(\d+)_(\d+)\.` → Matches `file_v11_2.py`

### Original File Resolution
For each duplicate found, the script:
1. Extracts the base filename (removes suffix)
2. Searches for the original file in the same directory
3. Compares content using MD5 hashing
4. Classifies as IDENTICAL or DIFFERENT

### Orphan Detection
Files with duplicate suffixes but **no original file** are flagged as "ORPHANS" and listed separately.

## Report Structure

### Console Report
```
📊 DUPLICATE FILE SCAN REPORT
================================================================================

📈 Summary:
  Total duplicates found: 130
  Identical to original:  85
  Different from original: 45
  Wasted space (identical): 245,678 bytes (239.92 KB)

🏷️  Duplicates by suffix type:
  _2             : 81 files
  _3             : 22 files
  _4             : 40 files
  _5             : 40 files
  _part_2        :  9 files

📁 Top directories with duplicates:
  config                                                      :  3 files
  apps_lic/L1_cognition/P3_aggregate                          :  2 files
  shared/types                                                :  3 files
  ...

📦 Duplicate groups:
  Original: config/config_models.py
    → config/config_models_2.py
    → config/config_models_3.py
  ...
```

### JSON Report
```json
{
  "total_duplicates": 130,
  "identical_duplicates": 85,
  "different_duplicates": 45,
  "total_wasted_bytes": 245678,
  "duplicates_by_suffix": {
    "_2": 81,
    "_3": 22,
    "_4": 40,
    "_5": 40,
    "_part_2": 9
  },
  "duplicates_by_directory": { ... },
  "duplicate_groups": [ ... ]
}
```

## Recommended Workflow

### Step 1: Initial Scan
```bash
bash 08_scripts/cleanup_duplicate_files.sh
```
Review the report to understand the scope.

### Step 2: Dry Run Deletion (Identical Only)
```bash
bash 08_scripts/cleanup_duplicate_files.sh --delete-identical
```
Review what would be deleted.

### Step 3: Real Deletion (Identical Only)
```bash
bash 08_scripts/cleanup_duplicate_files.sh --delete-identical --no-dry-run
```
Delete identical duplicates (safe - creates backup).

### Step 4: Manual Review of Non-Identical Files
For files flagged as DIFFERENT:
1. Review the content differences
2. Manually consolidate if needed
3. Delete manually or use `--delete-all` mode

### Step 5: Clean Up Orphans
Review ORPHAN files (duplicates with no original):
1. Determine if they should be renamed to originals
2. Or delete if truly redundant

## Example: Cleaning config/ Directory

### Current State
```
config/
  config_models.py       (original)
  config_models_2.py     (duplicate)
  config_models_3.py     (duplicate)
  core/
    config_models.py     (original)
    config_models_2.py   (duplicate)
    config_models_3.py   (duplicate)
```

### After Cleanup
```
config/
  config_models.py       (kept)
  core/
    config_models.py     (kept)
```

## Docker Execution Details

The shell wrapper executes the Python script inside a Docker container:

```bash
docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace \
    python:3.11-slim \
    bash -c "python3 /workspace/08_scripts/cleanup_duplicate_files.py ..."
```

**Benefits:**
- Consistent Linux environment
- No host Python dependencies
- Safe path handling (Linux forward slashes)

## Troubleshooting

### Issue: "Root path does not exist"
**Solution:** Ensure you're running from the project root or adjust `--root` parameter.

### Issue: "Permission denied"
**Solution:** Ensure Docker has access to the project directory.

### Issue: "No duplicates found"
**Solution:** Project is clean! No action needed.

### Issue: "Backup directory already exists"
**Solution:** Previous backup exists. Either delete it or the script will create a new timestamped backup.

## Advanced Usage

### Custom Root Path
```bash
python cleanup_duplicate_files.py --mode scan --root /custom/path
```

### Custom Output File
```bash
python cleanup_duplicate_files.py --mode scan --output my_report.json
```

### Programmatic Usage
```python
from cleanup_duplicate_files import DuplicateFileScanner, DuplicateFileCleaner

# Scan
scanner = DuplicateFileScanner('/workspace')
report = scanner.scan()

# Clean
cleaner = DuplicateFileCleaner('/workspace', scanner)
cleaner.create_backup()
deleted = cleaner.delete_identical_duplicates(dry_run=False)
```

## Zero-Loss Guarantee

This script adheres to the project's **Zero-Loss Guarantee**:

1. **Never deletes originals** - Only files with duplicate suffixes
2. **Automatic backups** - All deleted files backed up before deletion
3. **Dry-run default** - Must explicitly enable real deletion
4. **Content verification** - MD5 hashing ensures accuracy
5. **Detailed logging** - Full audit trail of all operations

## Next Steps

After running cleanup:

1. **Verify functionality** - Run tests to ensure no breakage
2. **Update imports** - Fix any broken imports if non-identical files were deleted
3. **Commit changes** - Git commit the cleanup
4. **Delete backup** - Once verified, remove backup directory

## Support

For issues or questions:
1. Review this README
2. Check the JSON report for details
3. Examine backup directory if files were deleted
4. Restore from backup if needed: `cp -r archives/cleanup_backup_*/* .`
