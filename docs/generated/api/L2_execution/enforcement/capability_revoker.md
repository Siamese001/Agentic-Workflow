# API Documentation: capability_revoker

**Target Audience**: developers, api_users

# capability_revoker API Documentation

**File**: `capability_revoker.py`
**Classes**: 3
**Functions**: 10

## Classes

- **TokenRevocationError** (inherits from RuntimeError)
- **VersionInvalidError** (inherits from RuntimeError)
- **CapabilityRevoker**

## Functions

- **get_capability_revoker** -> CapabilityRevoker
- **reset_capability_revoker_for_testing** -> None
- **__init__** -> None
- **revoke_token** -> None
- **invalidate_version** -> None
- **is_token_revoked** -> bool
- **is_version_valid** -> bool
- **validate_token** -> None
- **revoked_count** -> int
- **invalid_version_count** -> int


## Class: TokenRevocationError

**Description**: Raised when a token is used after revocation.

**Inherits from**: RuntimeError



## Class: VersionInvalidError

**Description**: Raised when a token's authority version is no longer valid.

**Inherits from**: RuntimeError



## Class: CapabilityRevoker

**Description**: Thread-safe capability token revocation registry.

    Usage::

        revoker = get_capability_revoker()
        revoker.validate_token(token.trace_id, token.authority_secret_version)
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### revoke_token
**Parameters**: self, trace_id
**Returns**: None
**Description**: Revoke a specific token by its trace ID (immediate effect).

#### invalidate_version
**Parameters**: self, version
**Returns**: None
**Description**: Invalidate all tokens carrying a specific authority_secret_version.

#### is_token_revoked
**Parameters**: self, trace_id
**Returns**: bool

#### is_version_valid
**Parameters**: self, version
**Returns**: bool
**Description**: Return True iff *version* equals the current key version and is not invalidated.

#### validate_token
**Parameters**: self, trace_id, authority_secret_version
**Returns**: None
**Description**: Raise if token is revoked or version is invalid.

        Args:
            trace_id: The trace_id embedded in the capability token.
            authority_secret_version: The authority_secret_version embedded in the token.

        Raises:
            TokenRevocationError: token has been explicitly revoked.
            VersionInvalidError: token authority version is invalid or rotated away.
        

#### revoked_count
**Parameters**: self
**Returns**: int

#### invalid_version_count
**Parameters**: self
**Returns**: int



## Function: get_capability_revoker

**Returns**: CapabilityRevoker
**Description**: Return the process-wide CapabilityRevoker singleton.



## Function: reset_capability_revoker_for_testing

**Returns**: None
**Description**: Reset the singleton (test isolation only).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: revoke_token

**Parameters**: self, trace_id
**Returns**: None
**Description**: Revoke a specific token by its trace ID (immediate effect).



## Function: invalidate_version

**Parameters**: self, version
**Returns**: None
**Description**: Invalidate all tokens carrying a specific authority_secret_version.



## Function: is_token_revoked

**Parameters**: self, trace_id
**Returns**: bool


## Function: is_version_valid

**Parameters**: self, version
**Returns**: bool
**Description**: Return True iff *version* equals the current key version and is not invalidated.



## Function: validate_token

**Parameters**: self, trace_id, authority_secret_version
**Returns**: None
**Description**: Raise if token is revoked or version is invalid.

        Args:
            trace_id: The trace_id embedded in the capability token.
            authority_secret_version: The authority_secret_version embedded in the token.

        Raises:
            TokenRevocationError: token has been explicitly revoked.
            VersionInvalidError: token authority version is invalid or rotated away.
        



## Function: revoked_count

**Parameters**: self
**Returns**: int


## Function: invalid_version_count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using TokenRevocationError
tokenrevocationerror = TokenRevocationError()
```

```python
# Using VersionInvalidError
versioninvaliderror = VersionInvalidError()
```

```python
# Using CapabilityRevoker
capabilityrevoker = CapabilityRevoker()
capabilityrevoker.revoke_token()
capabilityrevoker.invalidate_version()
```

### Function Usage

```python
# Using get_capability_revoker
result = get_capability_revoker()
```

```python
# Using reset_capability_revoker_for_testing
result = reset_capability_revoker_for_testing()
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:03.685384
**Type**: api_reference
**Quality**: comprehensive
