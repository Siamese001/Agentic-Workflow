# API Documentation: violation_event_store

**Target Audience**: developers, api_users

# violation_event_store API Documentation

**File**: `violation_event_store.py`
**Classes**: 1
**Functions**: 6

## Classes

- **ViolationEventStore**

## Functions

- **__init__** -> None
- **store_violation_event** -> str
- **fetch_latest_violation** -> ViolationEvent | None
- **fetch_window** -> list[ViolationEvent]
- **count** -> int
- **clear** -> None


## Class: ViolationEventStore

**Description**: 
    In-process L4 store for ViolationEvent records.

    Thread-safety: not guaranteed (single-threaded agent model assumed).
    Idempotent: storing the same event_hash twice is a no-op.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### store_violation_event
**Parameters**: self, event
**Returns**: str
**Description**: 
        Persist a ViolationEvent. Returns event_hash.
        Idempotent: duplicate hashes are silently ignored.
        

#### fetch_latest_violation
**Parameters**: self, before_tick
**Returns**: ViolationEvent | None
**Description**: 
        Return the most recent ViolationEvent with commit_tick < before_tick.

        Same-cycle events (commit_tick == before_tick) are excluded.
        Returns None if no prior events exist.
        

#### fetch_window
**Parameters**: self, before_tick, window_ticks
**Returns**: list[ViolationEvent]
**Description**: 
        Return all ViolationEvents with commit_tick in
        [before_tick - window_ticks, before_tick).

        Sorted ascending by (commit_tick, event_hash) for determinism.
        Same-cycle events (commit_tick == before_tick) are excluded.
        

#### count
**Parameters**: self
**Returns**: int
**Description**: Return total number of stored events.

#### clear
**Parameters**: self
**Returns**: None
**Description**: Remove all stored events (test utility).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: store_violation_event

**Parameters**: self, event
**Returns**: str
**Description**: 
        Persist a ViolationEvent. Returns event_hash.
        Idempotent: duplicate hashes are silently ignored.
        



## Function: fetch_latest_violation

**Parameters**: self, before_tick
**Returns**: ViolationEvent | None
**Description**: 
        Return the most recent ViolationEvent with commit_tick < before_tick.

        Same-cycle events (commit_tick == before_tick) are excluded.
        Returns None if no prior events exist.
        



## Function: fetch_window

**Parameters**: self, before_tick, window_ticks
**Returns**: list[ViolationEvent]
**Description**: 
        Return all ViolationEvents with commit_tick in
        [before_tick - window_ticks, before_tick).

        Sorted ascending by (commit_tick, event_hash) for determinism.
        Same-cycle events (commit_tick == before_tick) are excluded.
        



## Function: count

**Parameters**: self
**Returns**: int
**Description**: Return total number of stored events.



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Remove all stored events (test utility).



## Usage Examples

### Class Usage

```python
# Using ViolationEventStore
violationeventstore = ViolationEventStore()
violationeventstore.store_violation_event()
violationeventstore.fetch_latest_violation()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using store_violation_event
result = store_violation_event(event)
```

```python
# Using fetch_latest_violation
result = fetch_latest_violation(before_tick)
```



---
**Generated**: 2026-03-26T09:39:04.528712
**Type**: api_reference
**Quality**: comprehensive
