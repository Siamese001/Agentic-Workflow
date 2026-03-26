# API Documentation: key_derivation

**Target Audience**: developers, api_users

# key_derivation API Documentation

**File**: `key_derivation.py`
**Classes**: 0
**Functions**: 4


## Functions

- **derive_hmac_key** -> tuple[bytes, str, str]
- **get_key_version** -> str
- **verify_key_version** -> bool
- **get_kdf_salt_hash** -> str


## Function: derive_hmac_key

**Parameters**: master_secret
**Returns**: tuple[bytes, str, str]
**Description**: Derive an HMAC key using HKDF with version tracking.

    Args:
        master_secret: Raw master secret obtained from KeySource.

    Returns:
        Tuple of (derived_key_bytes, key_version_str, kdf_salt_hash_hex).
    



## Function: get_key_version

**Returns**: str
**Description**: Return current authority key version string.



## Function: verify_key_version

**Parameters**: packet_key_version
**Returns**: bool
**Description**: Return True if *packet_key_version* matches the current version.



## Function: get_kdf_salt_hash

**Returns**: str
**Description**: Return hex digest of the KDF salt (for embedding in packets).



## Usage Examples

### Function Usage

```python
# Using derive_hmac_key
result = derive_hmac_key(master_secret)
```

```python
# Using get_key_version
result = get_key_version()
```

```python
# Using verify_key_version
result = verify_key_version(packet_key_version)
```



---
**Generated**: 2026-03-26T09:39:03.708743
**Type**: api_reference
**Quality**: comprehensive
