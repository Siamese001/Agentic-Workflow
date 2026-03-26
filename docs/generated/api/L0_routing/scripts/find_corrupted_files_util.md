# API Documentation: find_corrupted_files_util

**Target Audience**: developers, api_users

# find_corrupted_files_util API Documentation

**File**: `find_corrupted_files_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **find_corruption** -> int
- **is_valid_python** -> bool
- **main**


## Function: find_corruption

**Parameters**: content
**Returns**: int
**Description**: Find position of literal backslash-n corruption. Returns -1 if none.



## Function: is_valid_python

**Parameters**: content
**Returns**: bool
**Description**: Check if content is valid Python syntax.



## Function: main



## Usage Examples

### Function Usage

```python
# Using find_corruption
result = find_corruption(content)
```

```python
# Using is_valid_python
result = is_valid_python(content)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:03.113616
**Type**: api_reference
**Quality**: comprehensive
