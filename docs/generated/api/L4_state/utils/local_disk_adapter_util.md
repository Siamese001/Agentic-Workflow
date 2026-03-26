# API Documentation: local_disk_adapter_util

**Target Audience**: developers, api_users

# local_disk_adapter_util API Documentation

**File**: `local_disk_adapter_util.py`
**Classes**: 1
**Functions**: 2

## Classes

- **LocalDiskAdapter**

## Functions

- **_get_write_gateway**
- **__init__**


## Class: LocalDiskAdapter

**Description**: 
    L4 State: The Sovereign File System.
    Strictly controls I/O within the mission-approved data silos.

    V15 Note: This is a storage provider pattern, NOT the behavioral adapter
    pattern prohibited by V15 §8.1. Explicitly excepted per P0.2.
    

### Methods

#### __init__
**Parameters**: self, config



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: __init__

**Parameters**: self, config


## Usage Examples

### Class Usage

```python
# Using LocalDiskAdapter
localdiskadapter = LocalDiskAdapter()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using __init__
result = __init__(config)
```



---
**Generated**: 2026-03-26T09:39:04.672887
**Type**: api_reference
**Quality**: comprehensive
