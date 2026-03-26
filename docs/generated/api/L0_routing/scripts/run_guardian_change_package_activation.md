# API Documentation: run_guardian_change_package_activation

**Target Audience**: developers, api_users

# run_guardian_change_package_activation API Documentation

**File**: `run_guardian_change_package_activation.py`
**Classes**: 0
**Functions**: 4


## Functions

- **_collect_files** -> list[Path]
- **scan_activation_patterns** -> dict[str, list[dict]]
- **run_change_package_activation_guardian** -> GuardianResult
- **_main** -> int


## Function: _collect_files

**Parameters**: repo_root
**Returns**: list[Path]


## Function: scan_activation_patterns

**Parameters**: repo_root, files
**Returns**: dict[str, list[dict]]


## Function: run_change_package_activation_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp, correlation_id
**Returns**: GuardianResult


## Function: _main

**Parameters**: argv
**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _collect_files
result = _collect_files(repo_root)
```

```python
# Using scan_activation_patterns
result = scan_activation_patterns(repo_root, files)
```

```python
# Using run_change_package_activation_guardian
result = run_change_package_activation_guardian(repo_root, write_artifacts_dir)
```



---
**Generated**: 2026-03-26T09:39:03.205126
**Type**: api_reference
**Quality**: comprehensive
