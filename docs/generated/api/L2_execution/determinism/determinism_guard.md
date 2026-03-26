# API Documentation: determinism_guard

**Target Audience**: developers, api_users

# determinism_guard API Documentation

**File**: `determinism_guard.py`
**Classes**: 0
**Functions**: 7


## Functions

- **assert_no_uuid4** -> Generator[None, None, None]
- **assert_no_wallclock** -> Generator[None, None, None]
- **assert_deterministic_context** -> Generator[None, None, None]
- **tracking_uuid4** -> uuid.UUID
- **tracking_time** -> float
- **tracking_sleep** -> None
- **tracking_monotonic** -> float


## Function: assert_no_uuid4

**Returns**: Generator[None, None, None]
**Description**: Context manager to assert no uuid4 is used within the context.

    Raises:
        RuntimeError: If uuid.uuid4() is called within the context.
    



## Function: assert_no_wallclock

**Returns**: Generator[None, None, None]
**Description**: Context manager to assert no wall-clock is used within the context.

    Note: Cannot patch datetime.now directly as it's immutable, so we track
    time module functions which are the most common wall-clock sources.

    Raises:
        RuntimeError: If time.time(), time.sleep(), or similar wall-clock functions are called.
    



## Function: assert_deterministic_context

**Returns**: Generator[None, None, None]
**Description**: Combined context manager asserting both no uuid4 and no wall-clock.

    This is a convenience wrapper that enables both guards simultaneously.
    



## Function: tracking_uuid4

**Returns**: uuid.UUID


## Function: tracking_time

**Returns**: float


## Function: tracking_sleep

**Parameters**: seconds
**Returns**: None


## Function: tracking_monotonic

**Returns**: float


## Usage Examples

### Function Usage

```python
# Using assert_no_uuid4
result = assert_no_uuid4()
```

```python
# Using assert_no_wallclock
result = assert_no_wallclock()
```

```python
# Using assert_deterministic_context
result = assert_deterministic_context()
```



---
**Generated**: 2026-03-26T09:39:03.663722
**Type**: api_reference
**Quality**: comprehensive
