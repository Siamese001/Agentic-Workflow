# API Documentation: sealed_interface_check_enforcer

**Target Audience**: developers, api_users

# sealed_interface_check_enforcer API Documentation

**File**: `sealed_interface_check_enforcer.py`
**Classes**: 0
**Functions**: 4


## Functions

- **_get_import_modules** -> list[str]
- **check_file** -> list[str]
- **run_check** -> list[str]
- **main** -> int


## Function: _get_import_modules

**Parameters**: tree
**Returns**: list[str]


## Function: check_file

**Parameters**: path
**Returns**: list[str]
**Description**: Return list of violation strings for a single file.



## Function: run_check

**Parameters**: apps_roots
**Returns**: list[str]
**Description**: Scan all apps_* Python files and return all violations.



## Function: main

**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _get_import_modules
result = _get_import_modules(tree)
```

```python
# Using check_file
result = check_file(path)
```

```python
# Using run_check
result = run_check(apps_roots)
```



---
**Generated**: 2026-03-26T09:39:04.928608
**Type**: api_reference
**Quality**: comprehensive
