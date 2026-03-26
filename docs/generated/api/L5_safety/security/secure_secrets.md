# API Documentation: secure_secrets

**Target Audience**: developers, api_users

# secure_secrets API Documentation

**File**: `secure_secrets.py`
**Classes**: 0
**Functions**: 3


## Functions

- **_ensure_key** -> bytes
- **load_secrets** -> dict[str, str]
- **inject_into_env** -> None


## Function: _ensure_key

**Returns**: bytes
**Description**: Ensure encryption key exists, return key bytes.



## Function: load_secrets

**Returns**: dict[str, str]
**Description**: Load and decrypt secrets from encrypted store.

    Returns:
        Empty dict if files missing, otherwise decrypted secrets.
    



## Function: inject_into_env

**Returns**: None
**Description**: Inject loaded secrets into environment variables.

    Sets defaults without overwriting existing environment variables.
    No printing to avoid secret leakage.
    



## Usage Examples

### Function Usage

```python
# Using _ensure_key
result = _ensure_key()
```

```python
# Using load_secrets
result = load_secrets()
```

```python
# Using inject_into_env
result = inject_into_env()
```



---
**Generated**: 2026-03-26T09:39:05.466723
**Type**: api_reference
**Quality**: comprehensive
