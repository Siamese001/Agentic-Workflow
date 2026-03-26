# API Documentation: artifacts_guard

**Target Audience**: developers, api_users

# artifacts_guard API Documentation

**File**: `artifacts_guard.py`
**Classes**: 0
**Functions**: 4


## Functions

- **is_forbidden_artifact_name** -> bool
- **scan_sensitive_content** -> list[str]
- **scan_artifacts_directory** -> dict[str, Any]
- **main**


## Function: is_forbidden_artifact_name

**Parameters**: file_path
**Returns**: bool
**Description**: Check if file has a forbidden artifact name.



## Function: scan_sensitive_content

**Parameters**: file_path
**Returns**: list[str]
**Description**: Scan file for sensitive content patterns.



## Function: scan_artifacts_directory

**Parameters**: artifacts_path
**Returns**: dict[str, Any]
**Description**: Scan artifacts directory for governance violations.



## Function: main

**Description**: Main scanner execution.



## Usage Examples

### Function Usage

```python
# Using is_forbidden_artifact_name
result = is_forbidden_artifact_name(file_path)
```

```python
# Using scan_sensitive_content
result = scan_sensitive_content(file_path)
```

```python
# Using scan_artifacts_directory
result = scan_artifacts_directory(artifacts_path)
```



---
**Generated**: 2026-03-26T09:39:05.996208
**Type**: api_reference
**Quality**: comprehensive
