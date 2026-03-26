# API Documentation: docs_structure_guard

**Target Audience**: developers, api_users

# docs_structure_guard API Documentation

**File**: `docs_structure_guard.py`
**Classes**: 0
**Functions**: 5


## Functions

- **is_valid_extension** -> bool
- **has_backup_suffix** -> bool
- **has_h1_heading** -> bool
- **scan_docs_directory** -> dict[str, Any]
- **main**


## Function: is_valid_extension

**Parameters**: file_path
**Returns**: bool
**Description**: Check if file has a valid documentation extension.



## Function: has_backup_suffix

**Parameters**: filename
**Returns**: bool
**Description**: Check if filename has backup suffix.



## Function: has_h1_heading

**Parameters**: file_path
**Returns**: bool
**Description**: Check if markdown file contains at least one H1 heading.



## Function: scan_docs_directory

**Parameters**: docs_path
**Returns**: dict[str, Any]
**Description**: Scan docs directory for structural violations.



## Function: main

**Description**: Main scanner execution.



## Usage Examples

### Function Usage

```python
# Using is_valid_extension
result = is_valid_extension(file_path)
```

```python
# Using has_backup_suffix
result = has_backup_suffix(filename)
```

```python
# Using has_h1_heading
result = has_h1_heading(file_path)
```



---
**Generated**: 2026-03-26T09:39:06.002404
**Type**: api_reference
**Quality**: comprehensive
