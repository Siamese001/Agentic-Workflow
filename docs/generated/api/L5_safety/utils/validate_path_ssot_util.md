# API Documentation: validate_path_ssot_util

**Target Audience**: developers, api_users

# validate_path_ssot_util API Documentation

**File**: `validate_path_ssot_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **should_exclude_path** -> bool
- **validate_file** -> list[tuple[int, str, str]]
- **validate_repository** -> tuple[bool, dict]
- **main**


## Function: should_exclude_path

**Parameters**: path
**Returns**: bool
**Description**: Check if path should be excluded from validation.



## Function: validate_file

**Parameters**: file_path
**Returns**: list[tuple[int, str, str]]
**Description**: Validate a single file for hardcoded paths.

    Returns:
        List of (line_number, violation_description, line_content)
    



## Function: validate_repository

**Returns**: tuple[bool, dict]
**Description**: Validate entire repository.

    Returns:
        (is_compliant, violations_dict)
    



## Function: main



## Usage Examples

### Function Usage

```python
# Using should_exclude_path
result = should_exclude_path(path)
```

```python
# Using validate_file
result = validate_file(file_path)
```

```python
# Using validate_repository
result = validate_repository()
```



---
**Generated**: 2026-03-26T09:39:05.710152
**Type**: api_reference
**Quality**: comprehensive
