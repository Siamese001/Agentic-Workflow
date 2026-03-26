# API Documentation: read_gateway

**Target Audience**: developers, api_users

# read_gateway API Documentation

**File**: `read_gateway.py`
**Classes**: 0
**Functions**: 6


## Functions

- **read_text** -> str
- **read_bytes** -> bytes
- **read_json** -> Any
- **list_directory** -> list[str]
- **file_exists** -> bool
- **get_file_info** -> dict[str, Any]


## Function: read_text

**Parameters**: path, encoding
**Returns**: str
**Description**: 
    Read text content from a file via MCP filesystem.
    Tool ID: ACT-020

    Args:
        path: File path to read.
        encoding: Text encoding (default: utf-8).

    Returns:
        str: File content, or raises OSError on failure.
    



## Function: read_bytes

**Parameters**: path
**Returns**: bytes
**Description**: 
    Read binary content from a file via MCP filesystem.
    Tool ID: ACT-021

    Args:
        path: File path to read.

    Returns:
        bytes: File content.
    



## Function: read_json

**Parameters**: path
**Returns**: Any
**Description**: 
    Read and parse a JSON file via MCP filesystem.
    Tool ID: ACT-022

    Args:
        path: File path to read.

    Returns:
        Parsed JSON object.
    



## Function: list_directory

**Parameters**: path
**Returns**: list[str]
**Description**: 
    List directory contents via MCP filesystem.
    Tool ID: ACT-023

    Args:
        path: Directory path to list.

    Returns:
        list[str]: List of file/directory names.
    



## Function: file_exists

**Parameters**: path
**Returns**: bool
**Description**: 
    Check if a file exists via MCP filesystem.
    Tool ID: ACT-024

    Args:
        path: File path to check.

    Returns:
        bool: True if file exists.
    



## Function: get_file_info

**Parameters**: path
**Returns**: dict[str, Any]
**Description**: 
    Get file metadata via MCP filesystem.
    Tool ID: ACT-025

    Args:
        path: File path to inspect.

    Returns:
        dict with size, modified, is_file, is_dir keys.
    



## Usage Examples

### Function Usage

```python
# Using read_text
result = read_text(path, encoding)
```

```python
# Using read_bytes
result = read_bytes(path)
```

```python
# Using read_json
result = read_json(path)
```



---
**Generated**: 2026-03-26T09:39:03.916182
**Type**: api_reference
**Quality**: comprehensive
