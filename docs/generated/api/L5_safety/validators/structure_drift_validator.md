# API Documentation: structure_drift_validator

**Target Audience**: developers, api_users

# structure_drift_validator API Documentation

**File**: `structure_drift_validator.py`
**Classes**: 0
**Functions**: 2


## Functions

- **generate_structure_manifest** -> dict[str, Any]
- **load_manifest** -> dict[str, Any]


## Function: generate_structure_manifest

**Returns**: dict[str, Any]
**Description**: Generate a deterministic structure manifest of the codebase.

    Returns:
        A dictionary containing the structure manifest with:
        - directories: List of all directories in the codebase
        - python_files: List of all Python files with their relative paths
        - hash: SHA256 hash of the manifest content for integrity checking
    



## Function: load_manifest

**Parameters**: manifest_path
**Returns**: dict[str, Any]
**Description**: Load a structure manifest from a file.

    Args:
        manifest_path: Path to the manifest file

    Returns:
        The loaded structure manifest
    



## Usage Examples

### Function Usage

```python
# Using generate_structure_manifest
result = generate_structure_manifest()
```

```python
# Using load_manifest
result = load_manifest(manifest_path)
```



---
**Generated**: 2026-03-26T09:39:05.881847
**Type**: api_reference
**Quality**: comprehensive
