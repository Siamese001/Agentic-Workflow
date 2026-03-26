# API Documentation: write_set_enforcer

**Target Audience**: developers, api_users

# write_set_enforcer API Documentation

**File**: `write_set_enforcer.py`
**Classes**: 2
**Functions**: 5

## Classes

- **WriteSetViolation** (inherits from RuntimeError)
- **WriteSetEnforcer**

## Functions

- **record_write** -> None
- **actual_writes** -> frozenset[str]
- **is_complete** -> bool
- **is_aborted** -> bool
- **verify** -> bool


## Class: WriteSetViolation

**Description**: Raised when an undeclared write is attempted.

**Inherits from**: RuntimeError



## Class: WriteSetEnforcer

**Description**: Enforces that actual writes match the declared write set.

    Usage::

        enforcer = WriteSetEnforcer(
            declared_write_set={"key_a", "key_b"}
        )
        enforcer.record_write("key_a")   # ok
        enforcer.record_write("key_c")   # raises
    

### Methods

#### record_write
**Parameters**: self, key
**Returns**: None
**Description**: Record an actual write and enforce declaration.

        Raises WriteSetViolation if key is not in the
        declared write set.
        

#### actual_writes
**Parameters**: self
**Returns**: frozenset[str]
**Description**: Return the set of actual writes recorded.

#### is_complete
**Parameters**: self
**Returns**: bool
**Description**: True if all declared writes have been performed.

#### is_aborted
**Parameters**: self
**Returns**: bool

#### verify
**Parameters**: self
**Returns**: bool
**Description**: Verify no undeclared writes occurred.

        Returns True if actual_writes is a subset of
        declared_write_set and execution was not aborted.
        



## Function: record_write

**Parameters**: self, key
**Returns**: None
**Description**: Record an actual write and enforce declaration.

        Raises WriteSetViolation if key is not in the
        declared write set.
        



## Function: actual_writes

**Parameters**: self
**Returns**: frozenset[str]
**Description**: Return the set of actual writes recorded.



## Function: is_complete

**Parameters**: self
**Returns**: bool
**Description**: True if all declared writes have been performed.



## Function: is_aborted

**Parameters**: self
**Returns**: bool


## Function: verify

**Parameters**: self
**Returns**: bool
**Description**: Verify no undeclared writes occurred.

        Returns True if actual_writes is a subset of
        declared_write_set and execution was not aborted.
        



## Usage Examples

### Class Usage

```python
# Using WriteSetViolation
writesetviolation = WriteSetViolation()
```

```python
# Using WriteSetEnforcer
writesetenforcer = WriteSetEnforcer()
writesetenforcer.record_write()
writesetenforcer.actual_writes()
```

### Function Usage

```python
# Using record_write
result = record_write(key)
```

```python
# Using actual_writes
result = actual_writes()
```

```python
# Using is_complete
result = is_complete()
```



---
**Generated**: 2026-03-26T09:39:03.747791
**Type**: api_reference
**Quality**: comprehensive
