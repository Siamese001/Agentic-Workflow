# API Documentation: execute_ssot_entrypoint

**Target Audience**: developers, api_users

# execute_ssot_entrypoint API Documentation

**File**: `execute_ssot_entrypoint.py`
**Classes**: 0
**Functions**: 2


## Functions

- **_resolve_repo_root** -> Path
- **main** -> int


## Function: _resolve_repo_root

**Returns**: Path
**Description**: Walk upward from this file until repo markers are found.



## Function: main

**Returns**: int
**Description**: V15-native entrypoint — single parser, deterministic, fail-closed.



## Usage Examples

### Function Usage

```python
# Using _resolve_repo_root
result = _resolve_repo_root()
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:03.084168
**Type**: api_reference
**Quality**: comprehensive
