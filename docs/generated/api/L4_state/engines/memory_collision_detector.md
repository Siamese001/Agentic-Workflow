# API Documentation: memory_collision_detector

**Target Audience**: developers, api_users

# memory_collision_detector API Documentation

**File**: `memory_collision_detector.py`
**Classes**: 4
**Functions**: 4

## Classes

- **MemoryDeadlockViolation** (inherits from Exception)
- **LockAcquisitionResult** (inherits from NamedTuple)
- **LockPolicy**
- **MemoryCollisionDetector**

## Functions

- **__init__**
- **acquire_locks** -> LockAcquisitionResult
- **_release_locks** -> None
- **release_locks** -> None


## Class: MemoryDeadlockViolation

**Description**: Raised when a deadlock is detected during lock acquisition.

**Inherits from**: Exception



## Class: LockAcquisitionResult

**Description**: The result of a lock acquisition attempt.

**Inherits from**: NamedTuple



## Class: LockPolicy

**Description**: Defines the policy for lock acquisition.



## Class: MemoryCollisionDetector

**Description**: 
    Manages concurrent access to shared memory with deterministic deadlock resolution.

    This detector enforces Guarantee #14 by implementing a strict lock acquisition
    hierarchy and a timeout policy. It prevents both race conditions and livelocks,
    ensuring that memory access is safe and deterministic under concurrency.
    

### Methods

#### __init__
**Parameters**: self, policy

#### acquire_locks
**Parameters**: self, trace_id, required_locks
**Returns**: LockAcquisitionResult
**Description**: 
        Acquires a set of locks in a deterministic, deadlock-free order.

        Args:
            trace_id: The unique identifier for the execution trace.
            required_locks: A sequence of lock names that need to be acquired.

        Returns:
            A LockAcquisitionResult indicating the outcome.
        

#### _release_locks
**Parameters**: self, locks_to_release
**Returns**: None
**Description**: Releases a list of locks, typically after a failed acquisition.

#### release_locks
**Parameters**: self, acquired_locks
**Returns**: None
**Description**: Public method to release locks after an operation is complete.



## Function: __init__

**Parameters**: self, policy


## Function: acquire_locks

**Parameters**: self, trace_id, required_locks
**Returns**: LockAcquisitionResult
**Description**: 
        Acquires a set of locks in a deterministic, deadlock-free order.

        Args:
            trace_id: The unique identifier for the execution trace.
            required_locks: A sequence of lock names that need to be acquired.

        Returns:
            A LockAcquisitionResult indicating the outcome.
        



## Function: _release_locks

**Parameters**: self, locks_to_release
**Returns**: None
**Description**: Releases a list of locks, typically after a failed acquisition.



## Function: release_locks

**Parameters**: self, acquired_locks
**Returns**: None
**Description**: Public method to release locks after an operation is complete.



## Usage Examples

### Class Usage

```python
# Using MemoryDeadlockViolation
memorydeadlockviolation = MemoryDeadlockViolation()
```

```python
# Using LockAcquisitionResult
lockacquisitionresult = LockAcquisitionResult()
```

```python
# Using LockPolicy
lockpolicy = LockPolicy()
```

### Function Usage

```python
# Using __init__
result = __init__(policy)
```

```python
# Using acquire_locks
result = acquire_locks(trace_id, required_locks)
```

```python
# Using _release_locks
result = _release_locks(locks_to_release)
```



---
**Generated**: 2026-03-26T09:39:04.538677
**Type**: api_reference
**Quality**: comprehensive
