# API Documentation: clock_provider

**Target Audience**: developers, api_users

# clock_provider API Documentation

**File**: `clock_provider.py`
**Classes**: 1
**Functions**: 3

## Classes

- **ClockProvider**

## Functions

- **now** -> datetime
- **time** -> float
- **reset** -> None


## Class: ClockProvider

**Description**: Injectable clock for deterministic time access.

    Class-level methods delegate to ``datetime.now`` / ``time.time``
    by default.  Override ``_now_fn`` / ``_time_fn`` in tests to
    inject deterministic clocks.
    

### Methods

#### now
**Parameters**: cls, tz
**Returns**: datetime
**Description**: Return current datetime, optionally in *tz*.

#### time
**Parameters**: cls
**Returns**: float
**Description**: Return monotonic-ish epoch seconds (like ``time.time()``).

#### reset
**Parameters**: cls
**Returns**: None
**Description**: Restore real clock — call in test teardown.



## Function: now

**Parameters**: cls, tz
**Returns**: datetime
**Description**: Return current datetime, optionally in *tz*.



## Function: time

**Parameters**: cls
**Returns**: float
**Description**: Return monotonic-ish epoch seconds (like ``time.time()``).



## Function: reset

**Parameters**: cls
**Returns**: None
**Description**: Restore real clock — call in test teardown.



## Usage Examples

### Class Usage

```python
# Using ClockProvider
clockprovider = ClockProvider()
clockprovider.now()
clockprovider.time()
```

### Function Usage

```python
# Using now
result = now(cls, tz)
```

```python
# Using time
result = time(cls)
```

```python
# Using reset
result = reset(cls)
```



---
**Generated**: 2026-03-26T09:39:02.707177
**Type**: api_reference
**Quality**: comprehensive
