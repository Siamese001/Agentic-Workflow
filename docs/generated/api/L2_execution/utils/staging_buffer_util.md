# API Documentation: staging_buffer_util

**Target Audience**: developers, api_users

# staging_buffer_util API Documentation

**File**: `staging_buffer_util.py`
**Classes**: 2
**Functions**: 6

## Classes

- **StagingBufferError** (inherits from Exception)
- **ImmutableStagingBuffer**

## Functions

- **__init__** -> None
- **set** -> None
- **get** -> object | None
- **lock** -> None
- **is_locked** -> bool
- **data** -> dict[str, object]


## Class: StagingBufferError

**Description**: Custom exception for staging buffer operations.

**Inherits from**: Exception



## Class: ImmutableStagingBuffer

**Description**: HOP-4: Immutable staging buffer. Once locked, cannot be modified.

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the staging buffer.

#### set
**Parameters**: self, key, value
**Returns**: None
**Description**: Set value in buffer (only if not locked).

#### get
**Parameters**: self, key, default
**Returns**: object | None
**Description**: Get value from buffer.

#### lock
**Parameters**: self
**Returns**: None
**Description**: Lock the buffer (irreversible).

#### is_locked
**Parameters**: self
**Returns**: bool
**Description**: Check if buffer is locked.

#### data
**Parameters**: self
**Returns**: dict[str, object]
**Description**: Read-only access to data.



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the staging buffer.



## Function: set

**Parameters**: self, key, value
**Returns**: None
**Description**: Set value in buffer (only if not locked).



## Function: get

**Parameters**: self, key, default
**Returns**: object | None
**Description**: Get value from buffer.



## Function: lock

**Parameters**: self
**Returns**: None
**Description**: Lock the buffer (irreversible).



## Function: is_locked

**Parameters**: self
**Returns**: bool
**Description**: Check if buffer is locked.



## Function: data

**Parameters**: self
**Returns**: dict[str, object]
**Description**: Read-only access to data.



## Usage Examples

### Class Usage

```python
# Using StagingBufferError
stagingbuffererror = StagingBufferError()
```

```python
# Using ImmutableStagingBuffer
immutablestagingbuffer = ImmutableStagingBuffer()
immutablestagingbuffer.set()
immutablestagingbuffer.get()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using set
result = set(key, value)
```

```python
# Using get
result = get(key, default)
```



---
**Generated**: 2026-03-26T09:39:04.068403
**Type**: api_reference
**Quality**: comprehensive
