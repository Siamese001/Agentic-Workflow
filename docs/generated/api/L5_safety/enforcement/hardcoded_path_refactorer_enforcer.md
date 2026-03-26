# API Documentation: hardcoded_path_refactorer_enforcer

**Target Audience**: developers, api_users

# hardcoded_path_refactorer_enforcer API Documentation

**File**: `hardcoded_path_refactorer_enforcer.py`
**Classes**: 0
**Functions**: 6


## Functions

- **should_exclude_path** -> bool
- **has_ssot_import** -> bool
- **add_ssot_import** -> str
- **refactor_file** -> tuple[bool, int]
- **refactor_repository** -> dict[str, int]
- **main**


## Function: should_exclude_path

**Parameters**: path
**Returns**: bool
**Description**: Check if path should be excluded.



## Function: has_ssot_import

**Parameters**: content
**Returns**: bool
**Description**: Check if file already imports from structure_blueprint.



## Function: add_ssot_import

**Parameters**: content
**Returns**: str
**Description**: Add SSOT import after last existing import.



## Function: refactor_file

**Parameters**: file_path, dry_run
**Returns**: tuple[bool, int]
**Description**: Refactor a single file to use SSOT constants.

    Returns:
        (was_modified, num_replacements)
    



## Function: refactor_repository

**Parameters**: dry_run
**Returns**: dict[str, int]
**Description**: Refactor entire repository.

    Returns:
        Statistics dict
    



## Function: main



## Usage Examples

### Function Usage

```python
# Using should_exclude_path
result = should_exclude_path(path)
```

```python
# Using has_ssot_import
result = has_ssot_import(content)
```

```python
# Using add_ssot_import
result = add_ssot_import(content)
```



---
**Generated**: 2026-03-26T09:39:04.828734
**Type**: api_reference
**Quality**: comprehensive
