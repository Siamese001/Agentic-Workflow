# API Documentation: path_util

**Target Audience**: developers, api_users

# path_util API Documentation

**File**: `path_util.py`
**Classes**: 0
**Functions**: 7


## Functions

- **get_validated_project_root** -> Path
- **validate_path_within_project** -> bool
- **safe_path_join** -> Path
- **safe_prefixed_filename** -> str
- **validate_no_duplicate_prefix** -> bool
- **get_python_files** -> Iterator[Path]
- **is_path_allowed** -> bool


## Function: get_validated_project_root

**Returns**: Path
**Description**: Get the validated project root by searching upward from CWD.



## Function: validate_path_within_project

**Parameters**: path, project_root
**Returns**: bool
**Description**: Validate that a path is within the project root.



## Function: safe_path_join

**Parameters**: project_root
**Returns**: Path
**Description**: Safely join path parts and validate result is within project root.



## Function: safe_prefixed_filename

**Parameters**: filename, prefix
**Returns**: str
**Description**: Generate a safe prefixed filename.



## Function: validate_no_duplicate_prefix

**Parameters**: filename, prefix
**Returns**: bool
**Description**: Validate that a filename doesn't have duplicate prefixes.



## Function: get_python_files

**Parameters**: directory
**Returns**: Iterator[Path]
**Description**: Yield all Python files in a directory, excluding specified directories.



## Function: is_path_allowed

**Parameters**: path, allowed_dirs
**Returns**: bool
**Description**: Check if a path is within one of the allowed directories.



## Usage Examples

### Function Usage

```python
# Using get_validated_project_root
result = get_validated_project_root()
```

```python
# Using validate_path_within_project
result = validate_path_within_project(path, project_root)
```

```python
# Using safe_path_join
result = safe_path_join(project_root)
```



---
**Generated**: 2026-03-26T09:39:03.537828
**Type**: api_reference
**Quality**: comprehensive
