# API Documentation: credential_guard

**Target Audience**: developers, api_users

# credential_guard API Documentation

**File**: `credential_guard.py`
**Classes**: 1
**Functions**: 11

## Classes

- **CredentialGuard**

## Functions

- **get_credential_guard**
- **is_text_file** -> bool
- **scan_file** -> list[dict[str, Any]]
- **scan_repository** -> dict[str, Any]
- **main**
- **__init__** -> None
- **get_instance**
- **check**
- **get_access_log** -> list[dict[str, Any]]
- **reset_rate_limits** -> None
- **reset**


## Class: CredentialGuard

**Description**: Runtime credential access guard.

    Modes:
        - ``warn``: log violations but allow execution (default)
        - ``enforce``: raise ``CredentialAccessDeniedError`` on violations
    

### Methods

#### __init__
**Parameters**: self, mode
**Returns**: None

#### get_instance
**Parameters**: cls

#### check
**Parameters**: self, operation, target
**Description**: Validate a credential access operation with rate limiting.

#### get_access_log
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Return the audit log of all checks.

#### reset_rate_limits
**Parameters**: self
**Returns**: None
**Description**: Clear rate limit counters.

#### reset
**Parameters**: cls



## Function: get_credential_guard

**Description**: Get the singleton CredentialGuard instance.



## Function: is_text_file

**Parameters**: file_path
**Returns**: bool
**Description**: Check if file is likely a text file based on extension and content.



## Function: scan_file

**Parameters**: file_path
**Returns**: list[dict[str, Any]]
**Description**: Scan a single file for credential patterns.



## Function: scan_repository

**Parameters**: root_path
**Returns**: dict[str, Any]
**Description**: Scan entire repository for credentials.



## Function: main

**Description**: Main scanner execution.



## Function: __init__

**Parameters**: self, mode
**Returns**: None


## Function: get_instance

**Parameters**: cls


## Function: check

**Parameters**: self, operation, target
**Description**: Validate a credential access operation with rate limiting.



## Function: get_access_log

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Return the audit log of all checks.



## Function: reset_rate_limits

**Parameters**: self
**Returns**: None
**Description**: Clear rate limit counters.



## Function: reset

**Parameters**: cls


## Usage Examples

### Class Usage

```python
# Using CredentialGuard
credentialguard = CredentialGuard()
credentialguard.get_instance()
credentialguard.check()
```

### Function Usage

```python
# Using get_credential_guard
result = get_credential_guard()
```

```python
# Using is_text_file
result = is_text_file(file_path)
```

```python
# Using scan_file
result = scan_file(file_path)
```



---
**Generated**: 2026-03-26T09:39:06.016893
**Type**: api_reference
**Quality**: comprehensive
