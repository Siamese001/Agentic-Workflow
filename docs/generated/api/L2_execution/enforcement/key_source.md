# API Documentation: key_source

**Target Audience**: developers, api_users

# key_source API Documentation

**File**: `key_source.py`
**Classes**: 3
**Functions**: 18

## Classes

- **KeySource** (inherits from ABC)
- **TestKeySource** (inherits from KeySource)
- **EnvKeySource** (inherits from KeySource)

## Functions

- **inject_key_source** -> None
- **get_key_source** -> KeySource
- **get_current_secret** -> bytes
- **get_secret** -> bytes
- **assert_key_scope** -> None
- **reject_expired_key** -> None
- **__init__**
- **get_secret** -> bytes
- **assert_key_scope** -> None
- **reject_expired_key** -> None
- **set_key_scope**
- **set_expiry_time**
- **__init__**
- **get_secret** -> bytes
- **assert_key_scope** -> None
- **reject_expired_key** -> None
- **set_key_scope**
- **set_ttl**


## Class: KeySource

**Description**: Abstract base for key sources - must be injected, never ambient.

**Inherits from**: ABC

### Methods

#### get_secret
**Parameters**: self
**Returns**: bytes
**Description**: Return the secret key for signing/verification.

#### assert_key_scope
**Parameters**: self, artifact_type
**Returns**: None
**Description**: Assert that the key is scoped for the given artifact type.

#### reject_expired_key
**Parameters**: self
**Returns**: None
**Description**: Reject if the key has expired.



## Class: TestKeySource

**Description**: Deterministic test key source for unit tests.

**Inherits from**: KeySource

### Methods

#### __init__
**Parameters**: self

#### get_secret
**Parameters**: self
**Returns**: bytes

#### assert_key_scope
**Parameters**: self, artifact_type
**Returns**: None
**Description**: Assert that the key is scoped for the given artifact type.

#### reject_expired_key
**Parameters**: self
**Returns**: None
**Description**: Reject if the key has expired.

#### set_key_scope
**Parameters**: self, artifact_type, allowed
**Description**: Set key scope for testing.

#### set_expiry_time
**Parameters**: self, expiry_time
**Description**: Set expiry time for testing.



## Class: EnvKeySource

**Description**: Environment-based key source for production (edge only).

**Inherits from**: KeySource

### Methods

#### __init__
**Parameters**: self, env_var

#### get_secret
**Parameters**: self
**Returns**: bytes

#### assert_key_scope
**Parameters**: self, artifact_type
**Returns**: None
**Description**: Assert that the key is scoped for the given artifact type.

#### reject_expired_key
**Parameters**: self
**Returns**: None
**Description**: Reject if the key has expired.

#### set_key_scope
**Parameters**: self, artifact_type, allowed
**Description**: Set key scope (for configuration).

#### set_ttl
**Parameters**: self, ttl_seconds
**Description**: Set time-to-live for key.



## Function: inject_key_source

**Parameters**: source
**Returns**: None
**Description**: Inject a key source - must be called at application edge.



## Function: get_key_source

**Returns**: KeySource
**Description**: Get the injected key source - fails if not injected.



## Function: get_current_secret

**Returns**: bytes
**Description**: Convenience helper to get current secret.



## Function: get_secret

**Parameters**: self
**Returns**: bytes
**Description**: Return the secret key for signing/verification.



## Function: assert_key_scope

**Parameters**: self, artifact_type
**Returns**: None
**Description**: Assert that the key is scoped for the given artifact type.



## Function: reject_expired_key

**Parameters**: self
**Returns**: None
**Description**: Reject if the key has expired.



## Function: __init__

**Parameters**: self


## Function: get_secret

**Parameters**: self
**Returns**: bytes


## Function: assert_key_scope

**Parameters**: self, artifact_type
**Returns**: None
**Description**: Assert that the key is scoped for the given artifact type.



## Function: reject_expired_key

**Parameters**: self
**Returns**: None
**Description**: Reject if the key has expired.



## Function: set_key_scope

**Parameters**: self, artifact_type, allowed
**Description**: Set key scope for testing.



## Function: set_expiry_time

**Parameters**: self, expiry_time
**Description**: Set expiry time for testing.



## Function: __init__

**Parameters**: self, env_var


## Function: get_secret

**Parameters**: self
**Returns**: bytes


## Function: assert_key_scope

**Parameters**: self, artifact_type
**Returns**: None
**Description**: Assert that the key is scoped for the given artifact type.



## Function: reject_expired_key

**Parameters**: self
**Returns**: None
**Description**: Reject if the key has expired.



## Function: set_key_scope

**Parameters**: self, artifact_type, allowed
**Description**: Set key scope (for configuration).



## Function: set_ttl

**Parameters**: self, ttl_seconds
**Description**: Set time-to-live for key.



## Usage Examples

### Class Usage

```python
# Using KeySource
keysource = KeySource()
keysource.get_secret()
keysource.assert_key_scope()
```

```python
# Using TestKeySource
testkeysource = TestKeySource()
testkeysource.get_secret()
testkeysource.assert_key_scope()
```

```python
# Using EnvKeySource
envkeysource = EnvKeySource()
envkeysource.get_secret()
envkeysource.assert_key_scope()
```

### Function Usage

```python
# Using inject_key_source
result = inject_key_source(source)
```

```python
# Using get_key_source
result = get_key_source()
```

```python
# Using get_current_secret
result = get_current_secret()
```



---
**Generated**: 2026-03-26T09:39:03.712374
**Type**: api_reference
**Quality**: comprehensive
