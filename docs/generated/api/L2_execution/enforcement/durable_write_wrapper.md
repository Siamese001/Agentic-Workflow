# API Documentation: durable_write_wrapper

**Target Audience**: developers, api_users

# durable_write_wrapper API Documentation

**File**: `durable_write_wrapper.py`
**Classes**: 0
**Functions**: 5


## Functions

- **durable_write** -> Any
- **reset_mutation_counter** -> None
- **get_mutation_count** -> int
- **set_phase** -> None
- **get_current_phase** -> str


## Function: durable_write

**Parameters**: operation
**Returns**: Any
**Description**: 
    Wrapper for all durable write operations.

    Args:
        operation: The actual write operation to perform
        *args: Arguments to pass to the operation
        **kwargs: Keyword arguments to pass to the operation

    Returns:
        Result of the operation

    Raises:
        AssertionError: If not in L2.2 phase
    



## Function: reset_mutation_counter

**Returns**: None
**Description**: Reset mutation counter (for testing only).



## Function: get_mutation_count

**Returns**: int
**Description**: Get current mutation count.



## Function: set_phase

**Parameters**: phase
**Returns**: None
**Description**: Set current execution phase.



## Function: get_current_phase

**Returns**: str
**Description**: Get current execution phase.



## Usage Examples

### Function Usage

```python
# Using durable_write
result = durable_write(operation)
```

```python
# Using reset_mutation_counter
result = reset_mutation_counter()
```

```python
# Using get_mutation_count
result = get_mutation_count()
```



---
**Generated**: 2026-03-26T09:39:03.690642
**Type**: api_reference
**Quality**: comprehensive
