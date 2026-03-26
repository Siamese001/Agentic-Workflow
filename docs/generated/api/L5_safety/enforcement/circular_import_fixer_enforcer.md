# API Documentation: circular_import_fixer_enforcer

**Target Audience**: developers, api_users

# circular_import_fixer_enforcer API Documentation

**File**: `circular_import_fixer_enforcer.py`
**Classes**: 0
**Functions**: 3


## Functions

- **calculate_relative_import** -> str
- **fix_imports_in_file** -> tuple[int, list[str]]
- **main** -> Any


## Function: calculate_relative_import

**Parameters**: file_path, import_path, project_root
**Returns**: str
**Description**: 
    Calculate the correct relative import path.

    Args:
        file_path: Path to the file being modified
        import_path: The import path after 'agentic_core.' (e.g., 'L1_cognition.planning.types')
        project_root: Root of the agentic_core package

    Returns:
        Relative import path (e.g., '.planning.types' or '..L1_cognition.planning.types')
    



## Function: fix_imports_in_file

**Parameters**: file_path, agentic_core_root, dry_run
**Returns**: tuple[int, list[str]]
**Description**: 
    Fix imports in a single file.

    Returns:
        Tuple of (number of changes, list of changes made)
    



## Function: main

**Returns**: Any
**Description**: Main execution function.



## Usage Examples

### Function Usage

```python
# Using calculate_relative_import
result = calculate_relative_import(file_path, import_path)
```

```python
# Using fix_imports_in_file
result = fix_imports_in_file(file_path, agentic_core_root)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:04.787581
**Type**: api_reference
**Quality**: comprehensive
