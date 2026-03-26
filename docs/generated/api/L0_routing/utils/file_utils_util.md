# API Documentation: file_utils_util

**Target Audience**: developers, api_users

# file_utils_util API Documentation

**File**: `file_utils_util.py`
**Classes**: 0
**Functions**: 9


## Functions

- **ensure_directory** -> bool
- **safe_read_file** -> str | None
- **safe_write_file** -> bool
- **safe_append_file** -> bool
- **safe_delete_file** -> bool
- **safe_move_file** -> bool
- **get_file_size** -> int
- **is_file_empty** -> bool
- **create_temp_file** -> Path


## Function: ensure_directory

**Parameters**: path
**Returns**: bool
**Description**: 
    Ensure a directory exists, creating it if necessary.

    Args:
        path: The directory path to ensure exists.

    Returns:
        True if directory exists or was created successfully, False otherwise.
    



## Function: safe_read_file

**Parameters**: path, encoding, default, errors
**Returns**: str | None
**Description**: 
    Safely read a file with proper error handling.

    Args:
        path: Path to the file to read.
        encoding: File encoding (default: utf-8).
        default: Default value to return if file cannot be read.
        errors: Error handling strategy (default: replace).

    Returns:
        File contents as string, or default value if read fails.
    



## Function: safe_write_file

**Parameters**: path, content, encoding, backup
**Returns**: bool
**Description**: 
    Safely write a file using atomic write pattern.

    Args:
        path: Path to the file to write.
        content: Content to write to the file.
        encoding: File encoding (default: utf-8).
        backup: Whether to create backup of existing file.

    Returns:
        True if write was successful, False otherwise.
    



## Function: safe_append_file

**Parameters**: path, content, encoding
**Returns**: bool
**Description**: 
    Safely append content to a file.

    Args:
        path: Path to the file to append to.
        content: Content to append.
        encoding: File encoding (default: utf-8).

    Returns:
        True if append was successful, False otherwise.
    



## Function: safe_delete_file

**Parameters**: path, backup
**Returns**: bool
**Description**: 
    Safely delete a file with optional backup.

    Args:
        path: Path to the file to delete.
        backup: Whether to create backup before deletion.

    Returns:
        True if deletion was successful, False otherwise.
    



## Function: safe_move_file

**Parameters**: src, dst, backup
**Returns**: bool
**Description**: 
    Safely move a file with optional backup of destination.

    Args:
        src: Source file path.
        dst: Destination file path.
        backup: Whether to backup existing destination file.

    Returns:
        True if move was successful, False otherwise.
    



## Function: get_file_size

**Parameters**: path
**Returns**: int
**Description**: 
    Get file size in bytes.

    Args:
        path: Path to the file.

    Returns:
        File size in bytes, or -1 if file doesn't exist.
    



## Function: is_file_empty

**Parameters**: path
**Returns**: bool
**Description**: 
    Check if file is empty.

    Args:
        path: Path to the file.

    Returns:
        True if file is empty or doesn't exist, False otherwise.
    



## Function: create_temp_file

**Parameters**: prefix, suffix, dir
**Returns**: Path
**Description**: 
    Create a temporary file.

    Args:
        prefix: File name prefix.
        suffix: File name suffix.
        dir: Directory for temporary file (default: system temp).

    Returns:
        Path to the created temporary file.
    



## Usage Examples

### Function Usage

```python
# Using ensure_directory
result = ensure_directory(path)
```

```python
# Using safe_read_file
result = safe_read_file(path, encoding)
```

```python
# Using safe_write_file
result = safe_write_file(path, content)
```



---
**Generated**: 2026-03-26T09:39:03.516352
**Type**: api_reference
**Quality**: comprehensive
