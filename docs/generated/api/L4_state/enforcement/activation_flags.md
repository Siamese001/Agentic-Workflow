# API Documentation: activation_flags

**Target Audience**: developers, api_users

# activation_flags API Documentation

**File**: `activation_flags.py`
**Classes**: 4
**Functions**: 23

## Classes

- **ActivationFlags**
- **ActivationProof**
- **ActivationFlagsStore**
- **ActivationGate**

## Functions

- **get_activation_flags** -> ActivationFlags | None
- **update_activation_flags** -> ActivationProof
- **is_meta_learning_allowed** -> bool
- **assert_meta_learning_allowed** -> None
- **verify_activation_chain** -> bool
- **verify_replay_binding** -> bool
- **reset_activation_flags** -> None
- **__init__**
- **_load_flags** -> None
- **_save_flags** -> None
- **_compute_flags_hash** -> str
- **update_flags** -> ActivationProof
- **get_current_flags** -> ActivationFlags | None
- **get_activation_proof** -> ActivationProof | None
- **verify_activation_chain** -> bool
- **verify_replay_binding** -> bool
- **reset_to_defaults** -> None
- **__init__**
- **check_p0_ready** -> bool
- **check_p1_ready** -> bool
- **check_p2_ready** -> bool
- **check_meta_learning_allowed** -> bool
- **assert_meta_learning_allowed** -> None


## Class: ActivationFlags

**Description**: L4-persisted, signed, replay-bound activation flags for Wave 16.



## Class: ActivationProof

**Description**: Cryptographic proof of activation state.



## Class: ActivationFlagsStore

**Description**: Manages L4-persisted activation flags with cryptographic binding.

### Methods

#### __init__
**Parameters**: self, storage_path

#### _load_flags
**Parameters**: self
**Returns**: None
**Description**: Load activation flags from L4 storage.

#### _save_flags
**Parameters**: self
**Returns**: None
**Description**: Save activation flags to L4 storage.

#### _compute_flags_hash
**Parameters**: self, flags
**Returns**: str
**Description**: Compute cryptographic hash of activation flags.

        Args:
            flags: Flags to hash

        Returns:
            SHA256 hash of flags
        

#### update_flags
**Parameters**: self, flags, guardian_signature, activated_by
**Returns**: ActivationProof
**Description**: Update activation flags with cryptographic proof.

        Args:
            flags: New activation flags
            guardian_signature: Guardian signature for the update
            activated_by: Entity performing the activation

        Returns:
            ActivationProof for the update

        Raises:
            RuntimeError: If signature verification fails
        

#### get_current_flags
**Parameters**: self
**Returns**: ActivationFlags | None
**Description**: Get current activation flags.

        Returns:
            Current ActivationFlags or None if not initialized
        

#### get_activation_proof
**Parameters**: self
**Returns**: ActivationProof | None
**Description**: Get current activation proof.

        Returns:
            Current ActivationProof or None if not available
        

#### verify_activation_chain
**Parameters**: self
**Returns**: bool
**Description**: Verify the chain of custody for activation flags.

        Returns:
            True if chain is valid
        

#### verify_replay_binding
**Parameters**: self, expected_digest
**Returns**: bool
**Description**: Verify that flags are bound to a specific replay digest.

        Args:
            expected_digest: Expected replay digest hash

        Returns:
            True if binding is valid
        

#### reset_to_defaults
**Parameters**: self
**Returns**: None
**Description**: Reset activation flags to default state.



## Class: ActivationGate

**Description**: Enforces activation gate logic based on flags.

### Methods

#### __init__
**Parameters**: self, store

#### check_p0_ready
**Parameters**: self
**Returns**: bool
**Description**: Check if P0 execution boundary is ready.

        Returns:
            True if P0 requirements are met
        

#### check_p1_ready
**Parameters**: self
**Returns**: bool
**Description**: Check if P1 freeze authority is ready.

        Returns:
            True if P1 requirements are met
        

#### check_p2_ready
**Parameters**: self
**Returns**: bool
**Description**: Check if P2 meta-learning is prepared.

        Returns:
            True if P2 requirements are met
        

#### check_meta_learning_allowed
**Parameters**: self
**Returns**: bool
**Description**: Check if meta-learning activation is allowed.

        Returns:
            True if all prerequisites are met and meta-learning is enabled

        Raises:
            RuntimeError: If verification fails
        

#### assert_meta_learning_allowed
**Parameters**: self
**Returns**: None
**Description**: Assert that meta-learning is allowed, raising if not.

        Raises:
            RuntimeError: If meta-learning is not allowed
        



## Function: get_activation_flags

**Returns**: ActivationFlags | None
**Description**: Exported function to get current activation flags.



## Function: update_activation_flags

**Parameters**: flags, signature, activated_by
**Returns**: ActivationProof
**Description**: Exported function to update activation flags.



## Function: is_meta_learning_allowed

**Returns**: bool
**Description**: Exported function to check if meta-learning is allowed.



## Function: assert_meta_learning_allowed

**Returns**: None
**Description**: Exported function to assert meta-learning is allowed.



## Function: verify_activation_chain

**Returns**: bool
**Description**: Exported function to verify activation chain.



## Function: verify_replay_binding

**Parameters**: expected_digest
**Returns**: bool
**Description**: Exported function to verify replay binding.



## Function: reset_activation_flags

**Returns**: None
**Description**: Exported function to reset activation flags.



## Function: __init__

**Parameters**: self, storage_path


## Function: _load_flags

**Parameters**: self
**Returns**: None
**Description**: Load activation flags from L4 storage.



## Function: _save_flags

**Parameters**: self
**Returns**: None
**Description**: Save activation flags to L4 storage.



## Function: _compute_flags_hash

**Parameters**: self, flags
**Returns**: str
**Description**: Compute cryptographic hash of activation flags.

        Args:
            flags: Flags to hash

        Returns:
            SHA256 hash of flags
        



## Function: update_flags

**Parameters**: self, flags, guardian_signature, activated_by
**Returns**: ActivationProof
**Description**: Update activation flags with cryptographic proof.

        Args:
            flags: New activation flags
            guardian_signature: Guardian signature for the update
            activated_by: Entity performing the activation

        Returns:
            ActivationProof for the update

        Raises:
            RuntimeError: If signature verification fails
        



## Function: get_current_flags

**Parameters**: self
**Returns**: ActivationFlags | None
**Description**: Get current activation flags.

        Returns:
            Current ActivationFlags or None if not initialized
        



## Function: get_activation_proof

**Parameters**: self
**Returns**: ActivationProof | None
**Description**: Get current activation proof.

        Returns:
            Current ActivationProof or None if not available
        



## Function: verify_activation_chain

**Parameters**: self
**Returns**: bool
**Description**: Verify the chain of custody for activation flags.

        Returns:
            True if chain is valid
        



## Function: verify_replay_binding

**Parameters**: self, expected_digest
**Returns**: bool
**Description**: Verify that flags are bound to a specific replay digest.

        Args:
            expected_digest: Expected replay digest hash

        Returns:
            True if binding is valid
        



## Function: reset_to_defaults

**Parameters**: self
**Returns**: None
**Description**: Reset activation flags to default state.



## Function: __init__

**Parameters**: self, store


## Function: check_p0_ready

**Parameters**: self
**Returns**: bool
**Description**: Check if P0 execution boundary is ready.

        Returns:
            True if P0 requirements are met
        



## Function: check_p1_ready

**Parameters**: self
**Returns**: bool
**Description**: Check if P1 freeze authority is ready.

        Returns:
            True if P1 requirements are met
        



## Function: check_p2_ready

**Parameters**: self
**Returns**: bool
**Description**: Check if P2 meta-learning is prepared.

        Returns:
            True if P2 requirements are met
        



## Function: check_meta_learning_allowed

**Parameters**: self
**Returns**: bool
**Description**: Check if meta-learning activation is allowed.

        Returns:
            True if all prerequisites are met and meta-learning is enabled

        Raises:
            RuntimeError: If verification fails
        



## Function: assert_meta_learning_allowed

**Parameters**: self
**Returns**: None
**Description**: Assert that meta-learning is allowed, raising if not.

        Raises:
            RuntimeError: If meta-learning is not allowed
        



## Usage Examples

### Class Usage

```python
# Using ActivationFlags
activationflags = ActivationFlags()
```

```python
# Using ActivationProof
activationproof = ActivationProof()
```

```python
# Using ActivationFlagsStore
activationflagsstore = ActivationFlagsStore()
activationflagsstore.update_flags()
activationflagsstore.get_current_flags()
```

### Function Usage

```python
# Using get_activation_flags
result = get_activation_flags()
```

```python
# Using update_activation_flags
result = update_activation_flags(flags, signature)
```

```python
# Using is_meta_learning_allowed
result = is_meta_learning_allowed()
```



---
**Generated**: 2026-03-26T09:39:04.481808
**Type**: api_reference
**Quality**: comprehensive
