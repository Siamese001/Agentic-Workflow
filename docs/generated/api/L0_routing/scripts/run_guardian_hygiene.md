# API Documentation: run_guardian_hygiene

**Target Audience**: developers, api_users

# run_guardian_hygiene API Documentation

**File**: `run_guardian_hygiene.py`
**Classes**: 0
**Functions**: 5


## Functions

- **scan_temp_artifacts** -> list[str] | ScanBudgetExceeded
- **scan_empty_folders** -> list[str]
- **scan_init_only_folders** -> list[str]
- **run_hygiene_guardian** -> GuardianResult
- **main** -> int


## Function: scan_temp_artifacts

**Parameters**: repo_root, allowed_roots
**Returns**: list[str] | ScanBudgetExceeded
**Description**: 
    Return repo-relative POSIX paths of temporary artifacts.

    Enforces MAX_FILES_PER_SCAN and MAX_FOLDER_DEPTH caps.
    Returns ScanBudgetExceeded sentinel on cap breach instead of raising.
    



## Function: scan_empty_folders

**Parameters**: repo_root, allowed_roots
**Returns**: list[str]
**Description**: Return repo-relative POSIX paths of truly empty folders.



## Function: scan_init_only_folders

**Parameters**: repo_root, allowed_roots
**Returns**: list[str]
**Description**: Return repo-relative POSIX paths of folders containing only __init__.py.



## Function: run_hygiene_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp
**Returns**: GuardianResult
**Description**: 
    Execute the hygiene guardian and return a schema-locked GuardianResult.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism (omitted if None).

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    



## Function: main

**Returns**: int


## Usage Examples

### Function Usage

```python
# Using scan_temp_artifacts
result = scan_temp_artifacts(repo_root, allowed_roots)
```

```python
# Using scan_empty_folders
result = scan_empty_folders(repo_root, allowed_roots)
```

```python
# Using scan_init_only_folders
result = scan_init_only_folders(repo_root, allowed_roots)
```



---
**Generated**: 2026-03-26T09:39:03.231759
**Type**: api_reference
**Quality**: comprehensive
