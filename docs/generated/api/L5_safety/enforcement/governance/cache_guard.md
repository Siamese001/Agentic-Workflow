# API Documentation: cache_guard

**Target Audience**: developers, api_users

# cache_guard API Documentation

**File**: `cache_guard.py`
**Classes**: 0
**Functions**: 7


## Functions

- **is_cache_directory** -> bool
- **is_excluded_directory** -> bool
- **estimate_directory_size** -> int
- **has_tracked_files** -> bool
- **is_forbidden_location** -> bool
- **scan_cache_directories** -> dict[str, Any]
- **main**


## Function: is_cache_directory

**Parameters**: dir_path
**Returns**: bool
**Description**: Check if directory is a cache directory.



## Function: is_excluded_directory

**Parameters**: dir_path
**Returns**: bool
**Description**: Check if directory should be excluded from scanning.



## Function: estimate_directory_size

**Parameters**: dir_path
**Returns**: int
**Description**: Estimate directory size, capped at 200MB scan.



## Function: has_tracked_files

**Parameters**: dir_path, root_path
**Returns**: bool
**Description**: Check if cache directory has any tracked files under it.



## Function: is_forbidden_location

**Parameters**: dir_path, root_path
**Returns**: bool
**Description**: Check if cache directory is in forbidden location.



## Function: scan_cache_directories

**Parameters**: root_path
**Returns**: dict[str, Any]
**Description**: Scan repository for cache directories.



## Function: main

**Description**: Main scanner execution.



## Usage Examples

### Function Usage

```python
# Using is_cache_directory
result = is_cache_directory(dir_path)
```

```python
# Using is_excluded_directory
result = is_excluded_directory(dir_path)
```

```python
# Using estimate_directory_size
result = estimate_directory_size(dir_path)
```



---
**Generated**: 2026-03-26T09:39:05.999345
**Type**: api_reference
**Quality**: comprehensive
