# API Documentation: detection_signal_store_types

**Target Audience**: developers, api_users

# detection_signal_store_types API Documentation

**File**: `detection_signal_store_types.py`
**Classes**: 2
**Functions**: 8

## Classes

- **_StoredEntry**
- **DetectionSignalStore**

## Functions

- **_get_detection_signal_class**
- **get_signal_store** -> DetectionSignalStore
- **store_detection_signal** -> str
- **fetch_latest_detection_signal** -> object | None
- **get_prior_detection_signal** -> object | None
- **store** -> str
- **fetch_latest** -> object | None
- **count** -> int


## Class: _StoredEntry

**Description**: Internal record: signal + the commit_tick at which it was stored.



## Class: DetectionSignalStore

**Description**: 
    L4 in-process store for DetectionSignals.

    Commit ticks are monotonically increasing integers supplied by the caller
    (typically the SemanticClock step_id or a simple counter).

    Same-cycle enforcement:
        fetch_latest(before_tick=T) returns the most recent signal whose
        commit_tick is STRICTLY LESS THAN T.  A signal stored at tick T
        is invisible to a fetch at boundary T — no same-cycle readback.
    

### Methods

#### store
**Parameters**: self, signal, commit_tick
**Returns**: str
**Description**: 
        Persist a DetectionSignal at the given commit_tick.

        Returns signal_hash for caller confirmation.
        Raises ValueError if commit_tick is not strictly greater than the
        last stored tick (monotonicity enforcement).
        

#### fetch_latest
**Parameters**: self, before_tick
**Returns**: object | None
**Description**: 
        Return the most recent signal with commit_tick STRICTLY < before_tick.

        Returns None if no qualifying signal exists.
        This is the no-same-cycle guarantee: a signal stored at before_tick
        is NOT returned.
        

#### count
**Parameters**: self
**Returns**: int



## Function: _get_detection_signal_class



## Function: get_signal_store

**Returns**: DetectionSignalStore
**Description**: Return the module-level L4 DetectionSignal store singleton.



## Function: store_detection_signal

**Parameters**: signal, commit_tick
**Returns**: str
**Description**: Store a signal in the L4 SSOT store. Returns signal_hash.



## Function: fetch_latest_detection_signal

**Parameters**: before_tick
**Returns**: object | None
**Description**: 
    Fetch the most recent signal committed before before_tick.

    Enforces no-same-cycle semantics: signals at before_tick are excluded.
    



## Function: get_prior_detection_signal

**Parameters**: execution_start_tick
**Returns**: object | None
**Description**: 
    Guaranteed prior-only accessor for routing decisions.

    Returns the most recent signal committed strictly before
    execution_start_tick. Signals emitted during the current execution
    cycle (at or after execution_start_tick) are invisible.
    



## Function: store

**Parameters**: self, signal, commit_tick
**Returns**: str
**Description**: 
        Persist a DetectionSignal at the given commit_tick.

        Returns signal_hash for caller confirmation.
        Raises ValueError if commit_tick is not strictly greater than the
        last stored tick (monotonicity enforcement).
        



## Function: fetch_latest

**Parameters**: self, before_tick
**Returns**: object | None
**Description**: 
        Return the most recent signal with commit_tick STRICTLY < before_tick.

        Returns None if no qualifying signal exists.
        This is the no-same-cycle guarantee: a signal stored at before_tick
        is NOT returned.
        



## Function: count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using _StoredEntry
_storedentry = _StoredEntry()
```

```python
# Using DetectionSignalStore
detectionsignalstore = DetectionSignalStore()
detectionsignalstore.store()
detectionsignalstore.fetch_latest()
```

### Function Usage

```python
# Using _get_detection_signal_class
result = _get_detection_signal_class()
```

```python
# Using get_signal_store
result = get_signal_store()
```

```python
# Using store_detection_signal
result = store_detection_signal(signal, commit_tick)
```



---
**Generated**: 2026-03-26T09:39:04.635018
**Type**: api_reference
**Quality**: comprehensive
