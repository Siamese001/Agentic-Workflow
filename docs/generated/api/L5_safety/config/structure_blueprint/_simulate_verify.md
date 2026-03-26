# API Documentation: _simulate_verify

**Target Audience**: developers, api_users

# _simulate_verify API Documentation

**File**: `_simulate_verify.py`
**Classes**: 0
**Functions**: 6


## Functions

- **_repo_root** -> str
- **_read_bytes** -> bytes | None
- **_run_verify** -> tuple[int, str]
- **main** -> int
- **_restore** -> None
- **_find_invoke_lines** -> list[str]


## Function: _repo_root

**Returns**: str


## Function: _read_bytes

**Parameters**: path
**Returns**: bytes | None
**Description**: Read file as bytes, return None if missing.



## Function: _run_verify

**Returns**: tuple[int, str]
**Description**: Run the verifier as a subprocess, return (exit_code, combined_output).



## Function: main

**Returns**: int


## Function: _restore

**Returns**: None
**Description**: Restore original lock files from backup.



## Function: _find_invoke_lines

**Parameters**: text
**Returns**: list[str]
**Description**: Same logic as CI guard: exact module path, line-level.



## Usage Examples

### Function Usage

```python
# Using _repo_root
result = _repo_root()
```

```python
# Using _read_bytes
result = _read_bytes(path)
```

```python
# Using _run_verify
result = _run_verify()
```



---
**Generated**: 2026-03-26T09:39:05.963681
**Type**: api_reference
**Quality**: comprehensive
