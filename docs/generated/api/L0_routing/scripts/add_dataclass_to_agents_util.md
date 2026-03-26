# API Documentation: add_dataclass_to_agents_util

**Target Audience**: developers, api_users

# add_dataclass_to_agents_util API Documentation

**File**: `add_dataclass_to_agents_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **has_dataclass_decorator** -> bool
- **has_dataclass_import** -> bool
- **add_dataclass_to_file** -> bool
- **main**


## Function: has_dataclass_decorator

**Parameters**: source
**Returns**: bool
**Description**: Check if source already has @dataclass decorator.



## Function: has_dataclass_import

**Parameters**: source
**Returns**: bool
**Description**: Check if source already imports dataclass.



## Function: add_dataclass_to_file

**Parameters**: file_path
**Returns**: bool
**Description**: Add @dataclass decorator to agent class in file.

    Returns True if changes were made.
    



## Function: main



## Usage Examples

### Function Usage

```python
# Using has_dataclass_decorator
result = has_dataclass_decorator(source)
```

```python
# Using has_dataclass_import
result = has_dataclass_import(source)
```

```python
# Using add_dataclass_to_file
result = add_dataclass_to_file(file_path)
```



---
**Generated**: 2026-03-26T09:39:02.728032
**Type**: api_reference
**Quality**: comprehensive
