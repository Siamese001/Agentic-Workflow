# API Documentation: deterministic_providers

**Target Audience**: developers, api_users

# deterministic_providers API Documentation

**File**: `deterministic_providers.py`
**Classes**: 4
**Functions**: 17

## Classes

- **DeterministicPatchError** (inherits from Exception)
- **FixedTimeProvider**
- **DeterministicRandomSource**
- **DeterministicUUIDProvider**

## Functions

- **patch_deterministic** -> dict[str, Any]
- **unpatch_deterministic** -> None
- **is_patched** -> bool
- **get_active_trace_id** -> str | None
- **_get_active_providers** -> dict[str, Any]
- **__init__** -> None
- **time** -> float
- **sleep** -> None
- **advance** -> None
- **current_offset** -> float
- **__init__** -> None
- **random** -> float
- **randint** -> int
- **choice** -> Any
- **shuffle** -> list
- **__init__** -> None
- **uuid4** -> _uuid_module.UUID


## Class: DeterministicPatchError

**Description**: Raised when attempting to re-patch with a different trace_id.

**Inherits from**: Exception



## Class: FixedTimeProvider

**Description**: Deterministic time provider for replay mode.

    Derives a stable base timestamp from trace_id via SHA-256.
    Advances monotonically via sleep() and advance() calls.
    

### Methods

#### __init__
**Parameters**: self, trace_id
**Returns**: None

#### time
**Parameters**: self
**Returns**: float
**Description**: Return deterministic timestamp.

#### sleep
**Parameters**: self, seconds
**Returns**: None
**Description**: Advance virtual clock instead of blocking.

#### advance
**Parameters**: self, seconds
**Returns**: None
**Description**: Manually advance virtual clock.

#### current_offset
**Parameters**: self
**Returns**: float
**Description**: Return accumulated offset for inspection.



## Class: DeterministicRandomSource

**Description**: Deterministic random source for replay mode.

    Derives seed from trace_id via SHA-256, producing identical sequences
    for identical trace_ids across runs.
    

### Methods

#### __init__
**Parameters**: self, trace_id
**Returns**: None

#### random
**Parameters**: self
**Returns**: float
**Description**: Return deterministic float in [0.0, 1.0).

#### randint
**Parameters**: self, a, b
**Returns**: int
**Description**: Return deterministic integer in [a, b].

#### choice
**Parameters**: self, seq
**Returns**: Any
**Description**: Return deterministic choice from sequence.

#### shuffle
**Parameters**: self, seq
**Returns**: list
**Description**: Shuffle sequence deterministically in-place and return it.



## Class: DeterministicUUIDProvider

**Description**: Deterministic UUID4 provider for replay mode.

    Produces a monotonically incrementing sequence of UUIDs derived from
    trace_id, ensuring identical UUID sequences across replays.
    

### Methods

#### __init__
**Parameters**: self, trace_id
**Returns**: None

#### uuid4
**Parameters**: self
**Returns**: _uuid_module.UUID
**Description**: Return deterministic UUID.



## Function: patch_deterministic

**Parameters**: trace_id
**Returns**: dict[str, Any]
**Description**: Install deterministic providers for the given trace_id.

    Returns a dict of provider instances for direct use.

    Raises DeterministicPatchError if already patched with a different trace_id.
    



## Function: unpatch_deterministic

**Returns**: None
**Description**: Restore original nondeterministic modules.

    Safe to call even if not patched (no-op).
    Primarily used in tests.
    



## Function: is_patched

**Returns**: bool
**Description**: Return True if deterministic providers are currently active.



## Function: get_active_trace_id

**Returns**: str | None
**Description**: Return the trace_id of the active patch, or None.



## Function: _get_active_providers

**Returns**: dict[str, Any]
**Description**: Return dict of current provider instances (internal helper).



## Function: __init__

**Parameters**: self, trace_id
**Returns**: None


## Function: time

**Parameters**: self
**Returns**: float
**Description**: Return deterministic timestamp.



## Function: sleep

**Parameters**: self, seconds
**Returns**: None
**Description**: Advance virtual clock instead of blocking.



## Function: advance

**Parameters**: self, seconds
**Returns**: None
**Description**: Manually advance virtual clock.



## Function: current_offset

**Parameters**: self
**Returns**: float
**Description**: Return accumulated offset for inspection.



## Function: __init__

**Parameters**: self, trace_id
**Returns**: None


## Function: random

**Parameters**: self
**Returns**: float
**Description**: Return deterministic float in [0.0, 1.0).



## Function: randint

**Parameters**: self, a, b
**Returns**: int
**Description**: Return deterministic integer in [a, b].



## Function: choice

**Parameters**: self, seq
**Returns**: Any
**Description**: Return deterministic choice from sequence.



## Function: shuffle

**Parameters**: self, seq
**Returns**: list
**Description**: Shuffle sequence deterministically in-place and return it.



## Function: __init__

**Parameters**: self, trace_id
**Returns**: None


## Function: uuid4

**Parameters**: self
**Returns**: _uuid_module.UUID
**Description**: Return deterministic UUID.



## Usage Examples

### Class Usage

```python
# Using DeterministicPatchError
deterministicpatcherror = DeterministicPatchError()
```

```python
# Using FixedTimeProvider
fixedtimeprovider = FixedTimeProvider()
fixedtimeprovider.time()
fixedtimeprovider.sleep()
```

```python
# Using DeterministicRandomSource
deterministicrandomsource = DeterministicRandomSource()
deterministicrandomsource.random()
deterministicrandomsource.randint()
```

### Function Usage

```python
# Using patch_deterministic
result = patch_deterministic(trace_id)
```

```python
# Using unpatch_deterministic
result = unpatch_deterministic()
```

```python
# Using is_patched
result = is_patched()
```



---
**Generated**: 2026-03-26T09:39:03.573110
**Type**: api_reference
**Quality**: comprehensive
