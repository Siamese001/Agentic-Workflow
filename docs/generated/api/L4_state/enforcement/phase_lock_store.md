# API Documentation: phase_lock_store

**Target Audience**: developers, api_users

# phase_lock_store API Documentation

**File**: `phase_lock_store.py`
**Classes**: 3
**Functions**: 22

## Classes

- **PhaseLockRecord**
- **PhaseLockStore**
- **PhaseLockValidator**

## Functions

- **_next_sequence** -> float
- **lock_phase** -> PhaseLockRecord
- **unlock_phase** -> bool
- **is_phase_locked** -> bool
- **get_phase_lock** -> PhaseLockRecord | None
- **verify_phase_sequence** -> bool
- **verify_phase_dependencies** -> bool
- **get_all_locked_phases** -> dict[int, PhaseLockRecord]
- **__init__**
- **_load_locks** -> None
- **_save_locks** -> None
- **lock_phase** -> PhaseLockRecord
- **unlock_phase** -> bool
- **is_locked** -> bool
- **get_lock_record** -> PhaseLockRecord | None
- **verify_replay_integrity** -> bool
- **get_all_locked_phases** -> dict[int, PhaseLockRecord]
- **clear_all_locks** -> None
- **__init__**
- **validate_phase_sequence** -> bool
- **validate_dependencies** -> bool
- **validate_unlock_permissions** -> bool


## Class: PhaseLockRecord

**Description**: Immutable record of a phase lock.



## Class: PhaseLockStore

**Description**: Manages phase lock persistence in L4 storage.

### Methods

#### __init__
**Parameters**: self, storage_path

#### _load_locks
**Parameters**: self
**Returns**: None
**Description**: Load existing phase locks from storage.

#### _save_locks
**Parameters**: self
**Returns**: None
**Description**: Save phase locks to storage.

#### lock_phase
**Parameters**: self, phase, metadata, signature, guardian_key
**Returns**: PhaseLockRecord
**Description**: Lock a phase with optional signature and replay binding.

        Args:
            phase: Phase number to lock
            metadata: Optional metadata to store with lock
            signature: Guardian signature for the lock
            guardian_key: Optional guardian key for signing

        Returns:
            PhaseLockRecord for the new lock

        Raises:
            RuntimeError: If phase is already locked
        

#### unlock_phase
**Parameters**: self, phase, signature
**Returns**: bool
**Description**: Unlock a phase with signature verification.

        Args:
            phase: Phase number to unlock
            signature: Guardian signature for verification

        Returns:
            True if unlocked successfully

        Raises:
            RuntimeError: If signature verification fails
        

#### is_locked
**Parameters**: self, phase
**Returns**: bool
**Description**: Check if a phase is locked.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is locked
        

#### get_lock_record
**Parameters**: self, phase
**Returns**: PhaseLockRecord | None
**Description**: Get the lock record for a phase.

        Args:
            phase: Phase number

        Returns:
            PhaseLockRecord or None if not found
        

#### verify_replay_integrity
**Parameters**: self, phase
**Returns**: bool
**Description**: Verify replay integrity of a phase lock.

        Args:
            phase: Phase number to verify

        Returns:
            True if replay integrity is valid
        

#### get_all_locked_phases
**Parameters**: self
**Returns**: dict[int, PhaseLockRecord]
**Description**: Get all currently locked phases.

        Returns:
            Dictionary of phase -> PhaseLockRecord
        

#### clear_all_locks
**Parameters**: self
**Returns**: None
**Description**: Clear all phase locks (for testing/reset).



## Class: PhaseLockValidator

**Description**: Validates phase lock operations and constraints.

### Methods

#### __init__
**Parameters**: self, store

#### validate_phase_sequence
**Parameters**: self, current_phase
**Returns**: bool
**Description**: Validate that phases are locked in proper sequence.

        Args:
            current_phase: Phase to validate

        Returns:
            True if sequence is valid

        Raises:
            RuntimeError: If sequence is invalid
        

#### validate_dependencies
**Parameters**: self, phase, dependencies
**Returns**: bool
**Description**: Validate that all dependency phases are locked.

        Args:
            phase: Phase being validated
            dependencies: List of required phase dependencies

        Returns:
            True if dependencies are satisfied

        Raises:
            RuntimeError: If dependencies are not met
        

#### validate_unlock_permissions
**Parameters**: self, phase, signature
**Returns**: bool
**Description**: Validate permissions to unlock a phase.

        Args:
            phase: Phase to unlock
            signature: Guardian signature

        Returns:
            True if unlock is permitted

        Raises:
            RuntimeError: If unlock not permitted
        



## Function: _next_sequence

**Returns**: float
**Description**: Return next deterministic sequence value (no wall-clock).



## Function: lock_phase

**Parameters**: phase, metadata, signature
**Returns**: PhaseLockRecord
**Description**: Exported function to lock a phase.



## Function: unlock_phase

**Parameters**: phase, signature
**Returns**: bool
**Description**: Exported function to unlock a phase.



## Function: is_phase_locked

**Parameters**: phase
**Returns**: bool
**Description**: Exported function to check if phase is locked.



## Function: get_phase_lock

**Parameters**: phase
**Returns**: PhaseLockRecord | None
**Description**: Exported function to get phase lock record.



## Function: verify_phase_sequence

**Parameters**: current_phase
**Returns**: bool
**Description**: Exported function to validate phase sequence.



## Function: verify_phase_dependencies

**Parameters**: phase, dependencies
**Returns**: bool
**Description**: Exported function to validate phase dependencies.



## Function: get_all_locked_phases

**Returns**: dict[int, PhaseLockRecord]
**Description**: Exported function to get all locked phases.



## Function: __init__

**Parameters**: self, storage_path


## Function: _load_locks

**Parameters**: self
**Returns**: None
**Description**: Load existing phase locks from storage.



## Function: _save_locks

**Parameters**: self
**Returns**: None
**Description**: Save phase locks to storage.



## Function: lock_phase

**Parameters**: self, phase, metadata, signature, guardian_key
**Returns**: PhaseLockRecord
**Description**: Lock a phase with optional signature and replay binding.

        Args:
            phase: Phase number to lock
            metadata: Optional metadata to store with lock
            signature: Guardian signature for the lock
            guardian_key: Optional guardian key for signing

        Returns:
            PhaseLockRecord for the new lock

        Raises:
            RuntimeError: If phase is already locked
        



## Function: unlock_phase

**Parameters**: self, phase, signature
**Returns**: bool
**Description**: Unlock a phase with signature verification.

        Args:
            phase: Phase number to unlock
            signature: Guardian signature for verification

        Returns:
            True if unlocked successfully

        Raises:
            RuntimeError: If signature verification fails
        



## Function: is_locked

**Parameters**: self, phase
**Returns**: bool
**Description**: Check if a phase is locked.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is locked
        



## Function: get_lock_record

**Parameters**: self, phase
**Returns**: PhaseLockRecord | None
**Description**: Get the lock record for a phase.

        Args:
            phase: Phase number

        Returns:
            PhaseLockRecord or None if not found
        



## Function: verify_replay_integrity

**Parameters**: self, phase
**Returns**: bool
**Description**: Verify replay integrity of a phase lock.

        Args:
            phase: Phase number to verify

        Returns:
            True if replay integrity is valid
        



## Function: get_all_locked_phases

**Parameters**: self
**Returns**: dict[int, PhaseLockRecord]
**Description**: Get all currently locked phases.

        Returns:
            Dictionary of phase -> PhaseLockRecord
        



## Function: clear_all_locks

**Parameters**: self
**Returns**: None
**Description**: Clear all phase locks (for testing/reset).



## Function: __init__

**Parameters**: self, store


## Function: validate_phase_sequence

**Parameters**: self, current_phase
**Returns**: bool
**Description**: Validate that phases are locked in proper sequence.

        Args:
            current_phase: Phase to validate

        Returns:
            True if sequence is valid

        Raises:
            RuntimeError: If sequence is invalid
        



## Function: validate_dependencies

**Parameters**: self, phase, dependencies
**Returns**: bool
**Description**: Validate that all dependency phases are locked.

        Args:
            phase: Phase being validated
            dependencies: List of required phase dependencies

        Returns:
            True if dependencies are satisfied

        Raises:
            RuntimeError: If dependencies are not met
        



## Function: validate_unlock_permissions

**Parameters**: self, phase, signature
**Returns**: bool
**Description**: Validate permissions to unlock a phase.

        Args:
            phase: Phase to unlock
            signature: Guardian signature

        Returns:
            True if unlock is permitted

        Raises:
            RuntimeError: If unlock not permitted
        



## Usage Examples

### Class Usage

```python
# Using PhaseLockRecord
phaselockrecord = PhaseLockRecord()
```

```python
# Using PhaseLockStore
phaselockstore = PhaseLockStore()
phaselockstore.lock_phase()
phaselockstore.unlock_phase()
```

```python
# Using PhaseLockValidator
phaselockvalidator = PhaseLockValidator()
phaselockvalidator.validate_phase_sequence()
phaselockvalidator.validate_dependencies()
```

### Function Usage

```python
# Using _next_sequence
result = _next_sequence()
```

```python
# Using lock_phase
result = lock_phase(phase, metadata)
```

```python
# Using unlock_phase
result = unlock_phase(phase, signature)
```



---
**Generated**: 2026-03-26T09:39:04.513390
**Type**: api_reference
**Quality**: comprehensive
