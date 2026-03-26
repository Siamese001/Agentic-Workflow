# API Documentation: extract_unique_content_util

**Target Audience**: developers, api_users

# extract_unique_content_util API Documentation

**File**: `extract_unique_content_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **build_codebase_index** -> tuple[set[str], set[str]]
- **analyze_archive_file** -> dict
- **main**


## Function: build_codebase_index

**Parameters**: dirs
**Returns**: tuple[set[str], set[str]]
**Description**: Build index of all class and function names in current codebase.



## Function: analyze_archive_file

**Parameters**: file_path, existing_classes, existing_functions
**Returns**: dict
**Description**: Analyze an archived file and identify unique content.



## Function: main



## Usage Examples

### Function Usage

```python
# Using build_codebase_index
result = build_codebase_index(dirs)
```

```python
# Using analyze_archive_file
result = analyze_archive_file(file_path, existing_classes)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:03.101159
**Type**: api_reference
**Quality**: comprehensive
