# API Documentation: run_guardian_manifest

**Target Audience**: developers, api_users

# run_guardian_manifest API Documentation

**File**: `run_guardian_manifest.py`
**Classes**: 0
**Functions**: 3


## Functions

- **_sha256** -> str
- **run_manifest_guardian** -> GuardianResult
- **main** -> int


## Function: _sha256

**Parameters**: file_path
**Returns**: str
**Description**: Compute SHA-256 hex digest of a file.



## Function: run_manifest_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp
**Returns**: GuardianResult
**Description**: 
    Execute the manifest integrity guardian.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    



## Function: main

**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _sha256
result = _sha256(file_path)
```

```python
# Using run_manifest_guardian
result = run_manifest_guardian(repo_root, write_artifacts_dir)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:03.237548
**Type**: api_reference
**Quality**: comprehensive
