# API Documentation: run_guardian_location_alignment

**Target Audience**: developers, api_users

# run_guardian_location_alignment API Documentation

**File**: `run_guardian_location_alignment.py`
**Classes**: 0
**Functions**: 4


## Functions

- **scan_missing_directories** -> list[str]
- **scan_misplaced_files** -> list[str]
- **run_location_alignment_guardian** -> GuardianResult
- **main** -> int


## Function: scan_missing_directories

**Parameters**: repo_root, required_roots
**Returns**: list[str]
**Description**: Return sorted list of required sovereign roots that are missing or not directories.

    Reproduces ``LocationValidatorAgent.validate_sovereign_roots()``.
    



## Function: scan_misplaced_files

**Parameters**: repo_root, scan_roots
**Returns**: list[str]
**Description**: Return sorted repo-relative POSIX paths of misplaced Python files.

    Reproduces key structural checks from ``LocationValidatorAgent.run()``
    and ``validate_file_location()``:

    1. Python files sitting directly at a sovereign territory root
       (should be in a recognized subfolder; __init__.py exempt).
    2. Files with forbidden backup/temp patterns anywhere in territories.
    



## Function: run_location_alignment_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp, required_roots, scan_roots
**Returns**: GuardianResult
**Description**: 
    Execute the location alignment guardian and return a schema-locked GuardianResult.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism (omitted if None).
        required_roots: Override ROOT_WHITELIST for testing.
        scan_roots: Override scan scope for testing.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    



## Function: main

**Returns**: int


## Usage Examples

### Function Usage

```python
# Using scan_missing_directories
result = scan_missing_directories(repo_root, required_roots)
```

```python
# Using scan_misplaced_files
result = scan_misplaced_files(repo_root, scan_roots)
```

```python
# Using run_location_alignment_guardian
result = run_location_alignment_guardian(repo_root, write_artifacts_dir)
```



---
**Generated**: 2026-03-26T09:39:03.234410
**Type**: api_reference
**Quality**: comprehensive
