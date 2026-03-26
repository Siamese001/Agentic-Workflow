# API Documentation: meta_learning_bus

**Target Audience**: developers, api_users

# meta_learning_bus API Documentation

**File**: `meta_learning_bus.py`
**Classes**: 2
**Functions**: 7

## Classes

- **MetaLearningChangePackage**
- **MetaLearningBus**

## Functions

- **get_process_bus** -> MetaLearningBus
- **create** -> 'MetaLearningChangePackage'
- **__init__**
- **enqueue** -> None
- **dequeue** -> MetaLearningChangePackage | None
- **size** -> int
- **apply_next** -> tuple[MetaLearningChangePackage, Any] | None


## Class: MetaLearningChangePackage

**Description**: Immutable change package for meta-learning operations.

### Methods

#### create
**Parameters**: cls, trace_id, kind, payload
**Returns**: 'MetaLearningChangePackage'
**Description**: 
        Create a new MetaLearningChangePackage with deterministic hash.

        Args:
            trace_id: Unique trace identifier
            kind: Change package kind
            payload: Package payload data

        Returns:
            New MetaLearningChangePackage with computed hash
        



## Class: MetaLearningBus

**Description**: 
    Queue-backed meta-learning bus for deterministic change processing.

    Provides FIFO queue behavior with injected apply functions.
    No wall-clock usage, no direct L4 mutation.
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize MetaLearningBus with in-memory FIFO queue.

#### enqueue
**Parameters**: self, pkg
**Returns**: None
**Description**: 
        Add a package to the queue.

        Args:
            pkg: Package to enqueue
        

#### dequeue
**Parameters**: self
**Returns**: MetaLearningChangePackage | None
**Description**: 
        Remove and return the next package from queue.

        Returns:
            Next package or None if queue is empty
        

#### size
**Parameters**: self
**Returns**: int
**Description**: 
        Get current queue size.

        Returns:
            Number of packages in queue
        

#### apply_next
**Parameters**: self
**Returns**: tuple[MetaLearningChangePackage, Any] | None
**Description**: 
        Apply the next package using injected function.

        Pops one package, calls apply_fn(pkg), returns result.
        Bus has no knowledge of L4; apply_fn is injected.

        Args:
            apply_fn: Function to apply the package

        Returns:
            (package, result) tuple or None if queue empty
        



## Function: get_process_bus

**Returns**: MetaLearningBus
**Description**: Return the process-level singleton MetaLearningBus.

    All components that publish real-time healing outcomes via
    DefaultMetaOutcomeBusHook should share this instance so that
    drain_and_apply() in _fire_meta_learning_intake can flush them.
    



## Function: create

**Parameters**: cls, trace_id, kind, payload
**Returns**: 'MetaLearningChangePackage'
**Description**: 
        Create a new MetaLearningChangePackage with deterministic hash.

        Args:
            trace_id: Unique trace identifier
            kind: Change package kind
            payload: Package payload data

        Returns:
            New MetaLearningChangePackage with computed hash
        



## Function: __init__

**Parameters**: self
**Description**: Initialize MetaLearningBus with in-memory FIFO queue.



## Function: enqueue

**Parameters**: self, pkg
**Returns**: None
**Description**: 
        Add a package to the queue.

        Args:
            pkg: Package to enqueue
        



## Function: dequeue

**Parameters**: self
**Returns**: MetaLearningChangePackage | None
**Description**: 
        Remove and return the next package from queue.

        Returns:
            Next package or None if queue is empty
        



## Function: size

**Parameters**: self
**Returns**: int
**Description**: 
        Get current queue size.

        Returns:
            Number of packages in queue
        



## Function: apply_next

**Parameters**: self
**Returns**: tuple[MetaLearningChangePackage, Any] | None
**Description**: 
        Apply the next package using injected function.

        Pops one package, calls apply_fn(pkg), returns result.
        Bus has no knowledge of L4; apply_fn is injected.

        Args:
            apply_fn: Function to apply the package

        Returns:
            (package, result) tuple or None if queue empty
        



## Usage Examples

### Class Usage

```python
# Using MetaLearningChangePackage
metalearningchangepackage = MetaLearningChangePackage()
metalearningchangepackage.create()
```

```python
# Using MetaLearningBus
metalearningbus = MetaLearningBus()
metalearningbus.enqueue()
metalearningbus.dequeue()
```

### Function Usage

```python
# Using get_process_bus
result = get_process_bus()
```

```python
# Using create
result = create(cls, trace_id)
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:02.689930
**Type**: api_reference
**Quality**: comprehensive
