# API Documentation: verifiable_checkpoint_manager

**Target Audience**: developers, api_users

# verifiable_checkpoint_manager API Documentation

**File**: `verifiable_checkpoint_manager.py`
**Classes**: 1
**Functions**: 2

## Classes

- **VerifiableCheckpointManager**

## Functions

- **create_checkpoint_manager** -> VerifiableCheckpointManager
- **__init__**


## Class: VerifiableCheckpointManager

**Description**: 
    Manages agent checkpoints with cryptographic verification.

    This ensures that when an agent wakes up, its memory hasn't been corrupted.
    Uses SHA-256 checksums to verify data integrity.
    

### Methods

#### __init__
**Parameters**: self, storage_provider
**Description**: 
        Initialize Checkpoint manager.

        Args:
            storage_provider: Storage backend (LocalDisk or S3)
        



## Function: create_checkpoint_manager

**Parameters**: storage_type
**Returns**: VerifiableCheckpointManager
**Description**: 
    Factory function to create a Checkpoint manager.

    Args:
        storage_type: "local" or "s3"
        **storage_kwargs: Storage adapter arguments

    Returns:
        VerifiableCheckpointManager instance
    



## Function: __init__

**Parameters**: self, storage_provider
**Description**: 
        Initialize Checkpoint manager.

        Args:
            storage_provider: Storage backend (LocalDisk or S3)
        



## Usage Examples

### Class Usage

```python
# Using VerifiableCheckpointManager
verifiablecheckpointmanager = VerifiableCheckpointManager()
```

### Function Usage

```python
# Using create_checkpoint_manager
result = create_checkpoint_manager(storage_type)
```

```python
# Using __init__
result = __init__(storage_provider)
```



---
**Generated**: 2026-03-26T09:39:04.606199
**Type**: api_reference
**Quality**: comprehensive
