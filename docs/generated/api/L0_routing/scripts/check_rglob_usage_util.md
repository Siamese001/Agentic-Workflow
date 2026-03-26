# API Documentation: check_rglob_usage_util

**Target Audience**: developers, api_users

# check_rglob_usage_util API Documentation

**File**: `check_rglob_usage_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **count_rglob_in_file** -> int
- **should_exclude_path** -> bool
- **scan_for_rglob_usage** -> tuple[int, list[dict]]
- **main**


## Function: count_rglob_in_file

**Parameters**: file_path
**Returns**: int
**Description**: 
    Count rglob/glob calls in a single file.

    Args:
        file_path: Path to the Python file

    Returns:
        Number of rglob/glob calls found
    



## Function: should_exclude_path

**Parameters**: file_path
**Returns**: bool
**Description**: Check if a file path should be excluded from counting.



## Function: scan_for_rglob_usage

**Parameters**: root_dir
**Returns**: tuple[int, list[dict]]
**Description**: 
    Scan directory for rglob/glob usage.

    Args:
        root_dir: Root directory to scan

    Returns:
        Tuple of (total_count, list of offender details)
    



## Function: main

**Description**: Main entry point for CI check.



## Usage Examples

### Function Usage

```python
# Using count_rglob_in_file
result = count_rglob_in_file(file_path)
```

```python
# Using should_exclude_path
result = should_exclude_path(file_path)
```

```python
# Using scan_for_rglob_usage
result = scan_for_rglob_usage(root_dir)
```



---
**Generated**: 2026-03-26T09:39:02.786569
**Type**: api_reference
**Quality**: comprehensive
