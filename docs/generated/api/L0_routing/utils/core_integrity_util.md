# API Documentation: core_integrity_util

**Target Audience**: developers, api_users

# core_integrity_util API Documentation

**File**: `core_integrity_util.py`
**Classes**: 3
**Functions**: 7

## Classes

- **ConfigurationError** (inherits from Exception)
- **CoreIntegrityVerifier**
- **SovereignLockError** (inherits from ConfigurationError)

## Functions

- **_get_configuration_error**
- **emergency_shutdown** -> None
- **verify_core_integrity** -> bool
- **_calculate_merkle_root** -> str
- **_calculate_file_hash** -> str
- **update_golden_seal** -> str
- **force_verify** -> bool


## Class: ConfigurationError

**Description**: Module-level fallback; replaced at runtime by healer_exceptions.ConfigurationError.

**Inherits from**: Exception



## Class: CoreIntegrityVerifier

**Description**: 
    Guards the Sovereign Core against mutation.

    Calculates SHA-256 Merkle root of the base_agents directory.
    If files have been modified without a version bump, raises FatalError.

    The "Golden Seal" - In production, this would be signed/encrypted.
    For now, it dynamically calculates self-consistency.
    

### Methods

#### verify_core_integrity
**Parameters**: cls
**Returns**: bool
**Description**: 
        Calculate Merkle Hash of the base_agents directory.
        If files have been modified without a version bump, raise FatalError.

        Returns:
            True if integrity is verified

        Raises:
            ConfigurationError: If core integrity is compromised
        

#### _calculate_merkle_root
**Parameters**: cls
**Returns**: str
**Description**: 
        Calculate SHA-256 Merkle root of all Python files in base_agents.

        Returns:
            Merkle root hash as hex string
        

#### _calculate_file_hash
**Parameters**: path
**Returns**: str
**Description**: 
        SHA-256 hash of a DNA file.

        Args:
            path: Path to the file

        Returns:
            SHA-256 hash as hex string
        

#### update_golden_seal
**Parameters**: cls
**Returns**: str
**Description**: 
        Update the golden seal with current hash.

        Returns:
            New golden seal hash
        

#### force_verify
**Parameters**: cls
**Returns**: bool
**Description**: 
        Force verification without golden seal check.

        Returns:
            True if basic integrity checks pass
        



## Class: SovereignLockError

**Description**: Raised when the Sovereign Lock detects integrity violations.

**Inherits from**: ConfigurationError



## Function: _get_configuration_error



## Function: emergency_shutdown

**Parameters**: message
**Returns**: None
**Description**: 
    Emergency shutdown when core integrity is compromised.

    Args:
        message: Error message to display
    



## Function: verify_core_integrity

**Parameters**: cls
**Returns**: bool
**Description**: 
        Calculate Merkle Hash of the base_agents directory.
        If files have been modified without a version bump, raise FatalError.

        Returns:
            True if integrity is verified

        Raises:
            ConfigurationError: If core integrity is compromised
        



## Function: _calculate_merkle_root

**Parameters**: cls
**Returns**: str
**Description**: 
        Calculate SHA-256 Merkle root of all Python files in base_agents.

        Returns:
            Merkle root hash as hex string
        



## Function: _calculate_file_hash

**Parameters**: path
**Returns**: str
**Description**: 
        SHA-256 hash of a DNA file.

        Args:
            path: Path to the file

        Returns:
            SHA-256 hash as hex string
        



## Function: update_golden_seal

**Parameters**: cls
**Returns**: str
**Description**: 
        Update the golden seal with current hash.

        Returns:
            New golden seal hash
        



## Function: force_verify

**Parameters**: cls
**Returns**: bool
**Description**: 
        Force verification without golden seal check.

        Returns:
            True if basic integrity checks pass
        



## Usage Examples

### Class Usage

```python
# Using ConfigurationError
configurationerror = ConfigurationError()
```

```python
# Using CoreIntegrityVerifier
coreintegrityverifier = CoreIntegrityVerifier()
coreintegrityverifier.verify_core_integrity()
coreintegrityverifier.update_golden_seal()
```

```python
# Using SovereignLockError
sovereignlockerror = SovereignLockError()
```

### Function Usage

```python
# Using _get_configuration_error
result = _get_configuration_error()
```

```python
# Using emergency_shutdown
result = emergency_shutdown(message)
```

```python
# Using verify_core_integrity
result = verify_core_integrity(cls)
```



---
**Generated**: 2026-03-26T09:39:03.513803
**Type**: api_reference
**Quality**: comprehensive
