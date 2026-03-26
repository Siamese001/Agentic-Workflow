# API Documentation: cid_registry

**Target Audience**: developers, api_users

# cid_registry API Documentation

**File**: `cid_registry.py`
**Classes**: 2
**Functions**: 5

## Classes

- **ExecutionCycle**
- **CIDRegistry**

## Functions

- **__init__**
- **new_cycle** -> ExecutionCycle
- **next_attempt** -> ExecutionCycle
- **get_cycle** -> ExecutionCycle | None
- **update_status** -> ExecutionCycle | None


## Class: ExecutionCycle

**Description**: Immutable execution cycle record.



## Class: CIDRegistry

**Description**: 
    Deterministic CID Registry for execution cycle tracking.

    Manages correlation IDs with immutable cycle records.
    No wall-clock usage, no randomness.
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize CID Registry with empty cycle tracking.

#### new_cycle
**Parameters**: self, cid
**Returns**: ExecutionCycle
**Description**: 
        Create a new execution cycle for given CID.

        Args:
            cid: Correlation ID for the cycle

        Returns:
            New ExecutionCycle with attempt=1 and status="new"
        

#### next_attempt
**Parameters**: self, cycle
**Returns**: ExecutionCycle
**Description**: 
        Create next attempt cycle from existing cycle.

        Deterministic increment only; no randomness.

        Args:
            cycle: Existing execution cycle

        Returns:
            New ExecutionCycle with incremented attempt
        

#### get_cycle
**Parameters**: self, cid
**Returns**: ExecutionCycle | None
**Description**: 
        Get current cycle for given CID.

        Args:
            cid: Correlation ID to lookup

        Returns:
            Current ExecutionCycle or None if not found
        

#### update_status
**Parameters**: self, cid, status
**Returns**: ExecutionCycle | None
**Description**: 
        Update status for given CID.

        Args:
            cid: Correlation ID to update
            status: New status value

        Returns:
            Updated ExecutionCycle or None if CID not found
        



## Function: __init__

**Parameters**: self
**Description**: Initialize CID Registry with empty cycle tracking.



## Function: new_cycle

**Parameters**: self, cid
**Returns**: ExecutionCycle
**Description**: 
        Create a new execution cycle for given CID.

        Args:
            cid: Correlation ID for the cycle

        Returns:
            New ExecutionCycle with attempt=1 and status="new"
        



## Function: next_attempt

**Parameters**: self, cycle
**Returns**: ExecutionCycle
**Description**: 
        Create next attempt cycle from existing cycle.

        Deterministic increment only; no randomness.

        Args:
            cycle: Existing execution cycle

        Returns:
            New ExecutionCycle with incremented attempt
        



## Function: get_cycle

**Parameters**: self, cid
**Returns**: ExecutionCycle | None
**Description**: 
        Get current cycle for given CID.

        Args:
            cid: Correlation ID to lookup

        Returns:
            Current ExecutionCycle or None if not found
        



## Function: update_status

**Parameters**: self, cid, status
**Returns**: ExecutionCycle | None
**Description**: 
        Update status for given CID.

        Args:
            cid: Correlation ID to update
            status: New status value

        Returns:
            Updated ExecutionCycle or None if CID not found
        



## Usage Examples

### Class Usage

```python
# Using ExecutionCycle
executioncycle = ExecutionCycle()
```

```python
# Using CIDRegistry
cidregistry = CIDRegistry()
cidregistry.new_cycle()
cidregistry.next_attempt()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using new_cycle
result = new_cycle(cid)
```

```python
# Using next_attempt
result = next_attempt(cycle)
```



---
**Generated**: 2026-03-26T09:39:03.567049
**Type**: api_reference
**Quality**: comprehensive
