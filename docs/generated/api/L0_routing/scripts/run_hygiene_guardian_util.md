# API Documentation: run_hygiene_guardian_util

**Target Audience**: developers, api_users

# run_hygiene_guardian_util API Documentation

**File**: `run_hygiene_guardian_util.py`
**Classes**: 0
**Functions**: 6


## Functions

- **scan_temp_artifacts** -> list[Path]
- **scan_empty_folders** -> list[Path]
- **scan_folders_with_only_init** -> list[Path]
- **remove_artifacts** -> tuple[int, list[str]]
- **remove_empty_folders** -> tuple[int, list[str]]
- **main**


## Function: scan_temp_artifacts

**Parameters**: root
**Returns**: list[Path]
**Description**: Scan for temporary artifacts without removing them.



## Function: scan_empty_folders

**Parameters**: root
**Returns**: list[Path]
**Description**: Scan for empty folders without removing them.



## Function: scan_folders_with_only_init

**Parameters**: root
**Returns**: list[Path]
**Description**: Scan for folders that only contain __init__.py (no other meaningful content).



## Function: remove_artifacts

**Parameters**: artifacts
**Returns**: tuple[int, list[str]]
**Description**: Remove artifacts and return count and errors.



## Function: remove_empty_folders

**Parameters**: folders
**Returns**: tuple[int, list[str]]
**Description**: Remove empty folders and return count and errors.



## Function: main



## Usage Examples

### Function Usage

```python
# Using scan_temp_artifacts
result = scan_temp_artifacts(root)
```

```python
# Using scan_empty_folders
result = scan_empty_folders(root)
```

```python
# Using scan_folders_with_only_init
result = scan_folders_with_only_init(root)
```



---
**Generated**: 2026-03-26T09:39:03.244224
**Type**: api_reference
**Quality**: comprehensive
