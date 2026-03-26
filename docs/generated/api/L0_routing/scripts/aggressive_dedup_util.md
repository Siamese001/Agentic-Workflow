# API Documentation: aggressive_dedup_util

**Target Audience**: developers, api_users

# aggressive_dedup_util API Documentation

**File**: `aggressive_dedup_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **get_all_classes_in_codebase** -> dict[str, list[str]]
- **find_redundant_files** -> list[str]
- **find_similar_named_files** -> list[tuple[str, str]]
- **find_low_value_files** -> list[str]
- **main**


## Function: get_all_classes_in_codebase

**Parameters**: dirs
**Returns**: dict[str, list[str]]
**Description**: Get all classes and which files they appear in.



## Function: find_redundant_files

**Parameters**: dirs, class_files
**Returns**: list[str]
**Description**: Find files where ALL classes exist in other files.



## Function: find_similar_named_files

**Parameters**: dirs
**Returns**: list[tuple[str, str]]
**Description**: Find files with similar names that might be duplicates.



## Function: find_low_value_files

**Parameters**: dirs
**Returns**: list[str]
**Description**: Find files that are likely low value (small, no docstrings, test-like).



## Function: main



## Usage Examples

### Function Usage

```python
# Using get_all_classes_in_codebase
result = get_all_classes_in_codebase(dirs)
```

```python
# Using find_redundant_files
result = find_redundant_files(dirs, class_files)
```

```python
# Using find_similar_named_files
result = find_similar_named_files(dirs)
```



---
**Generated**: 2026-03-26T09:39:02.750129
**Type**: api_reference
**Quality**: comprehensive
