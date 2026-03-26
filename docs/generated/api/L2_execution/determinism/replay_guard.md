# API Documentation: replay_guard

**Target Audience**: developers, api_users

# replay_guard API Documentation

**File**: `replay_guard.py`
**Classes**: 2
**Functions**: 17

## Classes

- **ReplayViolation** (inherits from RuntimeError)
- **ReplayGuard**

## Functions

- **__init__** -> None
- **__enter__** -> ReplayGuard
- **__exit__** -> None
- **_save** -> None
- **_restore** -> None
- **_patch_socket** -> None
- **_patch_subprocess** -> None
- **_patch_filesystem_writes** -> None
- **_patch_threading** -> None
- **_patch_random** -> None
- **_restore_all** -> None
- **_blocked_init** -> None
- **_blocked_run** -> Any
- **_blocked_popen** -> Any
- **_blocked_system** -> Any
- **_guarded_open** -> Any
- **_blocked_start** -> None


## Class: ReplayViolation

**Description**: Raised when a nondeterministic call is attempted during replay.

**Inherits from**: RuntimeError



## Class: ReplayGuard

**Description**: Context manager that intercepts all nondeterministic sources.

    Usage::

        with ReplayGuard(deterministic_seed=42):
            result = run_deterministic_execution(packet)

    Any attempt to call a patched nondeterministic function raises
    ReplayViolation immediately.
    

### Methods

#### __init__
**Parameters**: self, deterministic_seed
**Returns**: None

#### __enter__
**Parameters**: self
**Returns**: ReplayGuard

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: None

#### _save
**Parameters**: self, key, obj, attr
**Returns**: None

#### _restore
**Parameters**: self, key, obj, attr
**Returns**: None

#### _patch_socket
**Parameters**: self
**Returns**: None

#### _patch_subprocess
**Parameters**: self
**Returns**: None

#### _patch_filesystem_writes
**Parameters**: self
**Returns**: None

#### _patch_threading
**Parameters**: self
**Returns**: None

#### _patch_random
**Parameters**: self
**Returns**: None

#### _restore_all
**Parameters**: self
**Returns**: None



## Function: __init__

**Parameters**: self, deterministic_seed
**Returns**: None


## Function: __enter__

**Parameters**: self
**Returns**: ReplayGuard


## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: None


## Function: _save

**Parameters**: self, key, obj, attr
**Returns**: None


## Function: _restore

**Parameters**: self, key, obj, attr
**Returns**: None


## Function: _patch_socket

**Parameters**: self
**Returns**: None


## Function: _patch_subprocess

**Parameters**: self
**Returns**: None


## Function: _patch_filesystem_writes

**Parameters**: self
**Returns**: None


## Function: _patch_threading

**Parameters**: self
**Returns**: None


## Function: _patch_random

**Parameters**: self
**Returns**: None


## Function: _restore_all

**Parameters**: self
**Returns**: None


## Function: _blocked_init

**Parameters**: self_inner
**Returns**: None


## Function: _blocked_run

**Returns**: Any


## Function: _blocked_popen

**Returns**: Any


## Function: _blocked_system

**Returns**: Any


## Function: _guarded_open

**Parameters**: file, mode
**Returns**: Any


## Function: _blocked_start

**Parameters**: self_inner
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ReplayViolation
replayviolation = ReplayViolation()
```

```python
# Using ReplayGuard
replayguard = ReplayGuard()
```

### Function Usage

```python
# Using __init__
result = __init__(deterministic_seed)
```

```python
# Using __enter__
result = __enter__()
```

```python
# Using __exit__
result = __exit__(exc_type, exc_val)
```



---
**Generated**: 2026-03-26T09:39:03.674022
**Type**: api_reference
**Quality**: comprehensive
