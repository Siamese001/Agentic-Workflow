# API Documentation: logs_guard

**Target Audience**: developers, api_users

# logs_guard API Documentation

**File**: `logs_guard.py`
**Classes**: 0
**Functions**: 8


## Functions

- **is_log_or_output_file** -> bool
- **is_log_or_output_directory** -> bool
- **is_excluded_directory** -> bool
- **is_in_excluded_directory** -> bool
- **is_allowed_location** -> bool
- **scan_sensitive_content** -> list[str]
- **scan_logs_and_outputs** -> dict[str, Any]
- **main**


## Function: is_log_or_output_file

**Parameters**: file_path
**Returns**: bool
**Description**: Check if file is a log or output file based on extension.



## Function: is_log_or_output_directory

**Parameters**: dir_path
**Returns**: bool
**Description**: Check if directory is a log or output directory.



## Function: is_excluded_directory

**Parameters**: dir_path
**Returns**: bool
**Description**: Check if directory should be excluded from scanning.



## Function: is_in_excluded_directory

**Parameters**: file_path
**Returns**: bool
**Description**: Check if file is in any excluded directory.



## Function: is_allowed_location

**Parameters**: file_path, root_path
**Returns**: bool
**Description**: Check if file is in an allowed location.



## Function: scan_sensitive_content

**Parameters**: file_path
**Returns**: list[str]
**Description**: Scan file for sensitive content patterns.



## Function: scan_logs_and_outputs

**Parameters**: root_path
**Returns**: dict[str, Any]
**Description**: Scan repository for log and output files.



## Function: main

**Description**: Main scanner execution.



## Usage Examples

### Function Usage

```python
# Using is_log_or_output_file
result = is_log_or_output_file(file_path)
```

```python
# Using is_log_or_output_directory
result = is_log_or_output_directory(dir_path)
```

```python
# Using is_excluded_directory
result = is_excluded_directory(dir_path)
```



---
**Generated**: 2026-03-26T09:39:06.006395
**Type**: api_reference
**Quality**: comprehensive
