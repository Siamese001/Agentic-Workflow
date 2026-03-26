# API Documentation: runtime_state_guard

**Target Audience**: developers, api_users

# runtime_state_guard API Documentation

**File**: `runtime_state_guard.py`
**Classes**: 1
**Functions**: 8

## Classes

- **RuntimeStateGuard**

## Functions

- **_get_write_gateway**
- **__init__**
- **__enter__**
- **__exit__**
- **_load_state**
- **get_metric** -> Any
- **increment_metric**
- **_atomic_persist**


## Class: RuntimeStateGuard

**Description**: 
    Atomic guardian for runtime_state.json.
    Implements Write-Replace pattern and automatic backup recovery.
    

### Methods

#### __init__
**Parameters**: self, project_root

#### __enter__
**Parameters**: self
**Description**: Enter batch mode: suspend disk writes.

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Exit batch mode: flush if at top level and dirty.

#### _load_state
**Parameters**: self
**Description**: Loads state with failover to backup if corruption is detected.

#### get_metric
**Parameters**: self, key, default
**Returns**: Any

#### increment_metric
**Parameters**: self, key, value
**Description**: 
        Updates metric.
        Persists immediately UNLESS inside a batch context.
        

#### _atomic_persist
**Parameters**: self
**Description**: 
        Writes to a temp file then renames to ensure atomicity.
        Prevents half-written files during crashes.
        



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: __init__

**Parameters**: self, project_root


## Function: __enter__

**Parameters**: self
**Description**: Enter batch mode: suspend disk writes.



## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Exit batch mode: flush if at top level and dirty.



## Function: _load_state

**Parameters**: self
**Description**: Loads state with failover to backup if corruption is detected.



## Function: get_metric

**Parameters**: self, key, default
**Returns**: Any


## Function: increment_metric

**Parameters**: self, key, value
**Description**: 
        Updates metric.
        Persists immediately UNLESS inside a batch context.
        



## Function: _atomic_persist

**Parameters**: self
**Description**: 
        Writes to a temp file then renames to ensure atomicity.
        Prevents half-written files during crashes.
        



## Usage Examples

### Class Usage

```python
# Using RuntimeStateGuard
runtimestateguard = RuntimeStateGuard()
runtimestateguard.get_metric()
runtimestateguard.increment_metric()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using __enter__
result = __enter__()
```



---
**Generated**: 2026-03-26T09:39:04.586538
**Type**: api_reference
**Quality**: comprehensive
