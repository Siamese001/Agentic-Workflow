# API Documentation: blob_storage_provider

**Target Audience**: developers, api_users

# blob_storage_provider API Documentation

**File**: `blob_storage_provider.py`
**Classes**: 7
**Functions**: 10

## Classes

- **IBlobStorageProviderProtocol** (inherits from Protocol)
- **LocalDiskAdapter**
- **S3Adapter**
- **_TombstonedRedisDistributedLock**
- **_TombstonedRedisHotCache**
- **SignalLedger**
- **_TombstonedHotBrainCache**

## Functions

- **_get_write_gateway**
- **create_storage_adapter** -> IBlobStorageProviderProtocol
- **_run_self_tests** -> dict
- **__init__** -> None
- **_get_path** -> Path
- **__init__** -> None
- **__init__**
- **__init__**
- **__init__**
- **__init__**


## Class: IBlobStorageProviderProtocol

**Description**: 
    Protocol defining atomic storage operations.
    Standardizes 'open', 'write', 'read' across Local FS and Cloud.
    

**Inherits from**: Protocol



## Class: LocalDiskAdapter

**Description**: 
    Mimics cloud storage on local disk.
    Uses atomic 'write-to-temp-then-move' logic to prevent corruption.

    This adapter is perfect for development and ensures that your code
    works identically whether running locally or in production on S3.
    

### Methods

#### __init__
**Parameters**: self, base_path
**Returns**: None
**Description**: 
        Initialize local disk storage.

        Args:
            base_path: Base directory for storage
        

#### _get_path
**Parameters**: self, key
**Returns**: Path
**Description**: 
        Convert storage key to filesystem path.

        Args:
            key: Storage key

        Returns:
            Safe path within base directory
        



## Class: S3Adapter

**Description**: 
    Production adapter for AWS S3.

    Requires: pip install boto3
    

### Methods

#### __init__
**Parameters**: self, bucket_name, region
**Returns**: None
**Description**: 
        Initialize S3 storage adapter.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
        



## Class: _TombstonedRedisDistributedLock

**Description**: Tombstoned — see module comment above.

### Methods

#### __init__
**Parameters**: self



## Class: _TombstonedRedisHotCache

**Description**: Tombstoned — see module comment above.

### Methods

#### __init__
**Parameters**: self



## Class: SignalLedger

**Description**: 
    Simple ledger that logs ExecutionResults to a permanent log file.
    

### Methods

#### __init__
**Parameters**: self, storage_adapter, session_id
**Description**: 
        Initialize the signal ledger.

        Args:
            storage_adapter: Storage adapter for persistence
            session_id: Session identifier for this ledger
        



## Class: _TombstonedHotBrainCache

**Description**: Tombstoned — see module comment above.

### Methods

#### __init__
**Parameters**: self



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: create_storage_adapter

**Parameters**: adapter_type
**Returns**: IBlobStorageProviderProtocol
**Description**: 
    Factory function to create storage adapters.

    Args:
        adapter_type: "local" or "s3"
        **kwargs: Adapter-specific arguments

    Returns:
        Storage adapter instance
    



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: __init__

**Parameters**: self, base_path
**Returns**: None
**Description**: 
        Initialize local disk storage.

        Args:
            base_path: Base directory for storage
        



## Function: _get_path

**Parameters**: self, key
**Returns**: Path
**Description**: 
        Convert storage key to filesystem path.

        Args:
            key: Storage key

        Returns:
            Safe path within base directory
        



## Function: __init__

**Parameters**: self, bucket_name, region
**Returns**: None
**Description**: 
        Initialize S3 storage adapter.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
        



## Function: __init__

**Parameters**: self


## Function: __init__

**Parameters**: self


## Function: __init__

**Parameters**: self, storage_adapter, session_id
**Description**: 
        Initialize the signal ledger.

        Args:
            storage_adapter: Storage adapter for persistence
            session_id: Session identifier for this ledger
        



## Function: __init__

**Parameters**: self


## Usage Examples

### Class Usage

```python
# Using IBlobStorageProviderProtocol
iblobstorageproviderprotocol = IBlobStorageProviderProtocol()
```

```python
# Using LocalDiskAdapter
localdiskadapter = LocalDiskAdapter()
```

```python
# Using S3Adapter
s3adapter = S3Adapter()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using create_storage_adapter
result = create_storage_adapter(adapter_type)
```

```python
# Using _run_self_tests
result = _run_self_tests()
```



---
**Generated**: 2026-03-26T09:39:04.560260
**Type**: api_reference
**Quality**: comprehensive
