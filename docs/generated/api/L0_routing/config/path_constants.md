# API Documentation: path_constants

**Target Audience**: developers, api_users

# path_constants API Documentation

**File**: `path_constants.py`
**Classes**: 0
**Functions**: 3


## Functions

- **get_validated_project_root** -> Path
- **get_apps_directories** -> list[str]
- **get_all_apps_paths** -> list[Path]


## Function: get_validated_project_root

**Returns**: Path
**Description**: Return the validated project root directory.

    Walks up from CWD looking for PROJECT_ROOT_MARKERS.
    Caches result for performance.
    



## Function: get_apps_directories

**Returns**: list[str]
**Description**: Dynamically discover all apps_* directories in the repository.
    
    Returns:
        List of directory names starting with 'apps_' that exist in the repo.
        Cached for performance.
    



## Function: get_all_apps_paths

**Returns**: list[Path]
**Description**: Get absolute paths for all apps_* directories.
    
    Returns:
        List of Path objects for all apps_* directories.
        Cached for performance.
    



## Usage Examples

### Function Usage

```python
# Using get_validated_project_root
result = get_validated_project_root()
```

```python
# Using get_apps_directories
result = get_apps_directories()
```

```python
# Using get_all_apps_paths
result = get_all_apps_paths()
```



---
**Generated**: 2026-03-26T09:39:02.587471
**Type**: api_reference
**Quality**: comprehensive
