# API Documentation: run_guardian_cross_layer_mutation

**Target Audience**: developers, api_users

# run_guardian_cross_layer_mutation API Documentation

**File**: `run_guardian_cross_layer_mutation.py`
**Classes**: 0
**Functions**: 6


## Functions

- **_layer_from_path** -> str | None
- **_layer_from_module_string** -> str | None
- **_collect_files** -> list[Path]
- **scan_cross_layer_mutations** -> dict[str, list[dict]]
- **run_cross_layer_mutation_guardian** -> GuardianResult
- **_main** -> int


## Function: _layer_from_path

**Parameters**: path
**Returns**: str | None


## Function: _layer_from_module_string

**Parameters**: module
**Returns**: str | None


## Function: _collect_files

**Parameters**: repo_root
**Returns**: list[Path]


## Function: scan_cross_layer_mutations

**Parameters**: repo_root, files
**Returns**: dict[str, list[dict]]


## Function: run_cross_layer_mutation_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp, correlation_id
**Returns**: GuardianResult


## Function: _main

**Parameters**: argv
**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _layer_from_path
result = _layer_from_path(path)
```

```python
# Using _layer_from_module_string
result = _layer_from_module_string(module)
```

```python
# Using _collect_files
result = _collect_files(repo_root)
```



---
**Generated**: 2026-03-26T09:39:03.214613
**Type**: api_reference
**Quality**: comprehensive
