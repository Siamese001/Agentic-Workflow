# API Documentation: run_guardian_drift_detection

**Target Audience**: developers, api_users

# run_guardian_drift_detection API Documentation

**File**: `run_guardian_drift_detection.py`
**Classes**: 0
**Functions**: 5


## Functions

- **scan_forbidden_root_folders** -> list[str]
- **scan_archived_files_at_root** -> list[str]
- **scan_duplicate_ssot_folders** -> list[dict[str, str]]
- **run_drift_detection_guardian** -> GuardianResult
- **main** -> int


## Function: scan_forbidden_root_folders

**Parameters**: repo_root
**Returns**: list[str]
**Description**: Return sorted list of forbidden folder names found at project root.



## Function: scan_archived_files_at_root

**Parameters**: repo_root
**Returns**: list[str]
**Description**: Return sorted repo-relative POSIX paths of archived files at root.



## Function: scan_duplicate_ssot_folders

**Parameters**: repo_root
**Returns**: list[dict[str, str]]
**Description**: Return sorted list of duplicate folder dicts found at root.

    Each dict has keys: name, root_path, ssot_path (repo-relative POSIX).
    Only reported when BOTH root and SSOT paths exist simultaneously.
    



## Function: run_drift_detection_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp
**Returns**: GuardianResult
**Description**: 
    Execute the drift detection guardian and return a schema-locked GuardianResult.

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
# Using scan_forbidden_root_folders
result = scan_forbidden_root_folders(repo_root)
```

```python
# Using scan_archived_files_at_root
result = scan_archived_files_at_root(repo_root)
```

```python
# Using scan_duplicate_ssot_folders
result = scan_duplicate_ssot_folders(repo_root)
```



---
**Generated**: 2026-03-26T09:39:03.219319
**Type**: api_reference
**Quality**: comprehensive
