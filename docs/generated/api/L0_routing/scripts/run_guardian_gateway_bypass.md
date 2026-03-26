# API Documentation: run_guardian_gateway_bypass

**Target Audience**: developers, api_users

# run_guardian_gateway_bypass API Documentation

**File**: `run_guardian_gateway_bypass.py`
**Classes**: 0
**Functions**: 5


## Functions

- **_collect_files** -> list[Path]
- **scan_provider_sdk_imports** -> list[dict]
- **scan_direct_model_calls** -> list[dict]
- **run_gateway_bypass_guardian** -> GuardianResult
- **_main** -> int


## Function: _collect_files

**Parameters**: repo_root
**Returns**: list[Path]


## Function: scan_provider_sdk_imports

**Parameters**: repo_root, files
**Returns**: list[dict]
**Description**: Return sorted violation dicts for forbidden SDK imports.



## Function: scan_direct_model_calls

**Parameters**: repo_root, files
**Returns**: list[dict]
**Description**: Return sorted violation dicts for direct model instantiation.



## Function: run_gateway_bypass_guardian

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
# Using scan_provider_sdk_imports
result = scan_provider_sdk_imports(repo_root, files)
```

```python
# Using scan_direct_model_calls
result = scan_direct_model_calls(repo_root, files)
```



---
**Generated**: 2026-03-26T09:39:03.223403
**Type**: api_reference
**Quality**: comprehensive
