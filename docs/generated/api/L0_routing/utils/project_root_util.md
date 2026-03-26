# API Documentation: project_root_util

**Target Audience**: developers, api_users

# project_root_util API Documentation

**File**: `project_root_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **get_project_root** -> Path
- **clear_project_root_cache** -> None
- **get_validated_project_root** -> Path


## Function: get_project_root

**Parameters**: start_path
**Returns**: Path
**Description**: 
    Detect the project root directory by searching upward for markers.

    Args:
        start_path: The path to start searching from. Defaults to CWD.

    Returns:
        Path: The absolute path to the project root.

    Raises:
        RuntimeError: If the project root cannot be found after searching 10 levels up.
    



## Function: clear_project_root_cache

**Returns**: None
**Description**: Clear the cached project root. Useful for testing.



## Function: get_validated_project_root

**Returns**: Path
**Description**: Get the validated project root by searching upward from this file.

    Compatibility alias — delegates to get_project_root().
    



## Usage Examples

### Function Usage

```python
# Using get_project_root
result = get_project_root(start_path)
```

```python
# Using clear_project_root_cache
result = clear_project_root_cache()
```

```python
# Using get_validated_project_root
result = get_validated_project_root()
```



---
**Generated**: 2026-03-26T09:39:03.537828
**Type**: api_reference
**Quality**: comprehensive
