# API Documentation: reentry_loop

**Target Audience**: developers, api_users

# reentry_loop API Documentation

**File**: `reentry_loop.py`
**Classes**: 1
**Functions**: 6

## Classes

- **ReEntryLoop**

## Functions

- **__init__**
- **should_retry** -> bool
- **advance** -> ExecutionCycle
- **new_cycle** -> ExecutionCycle
- **get_cycle**
- **update_status**


## Class: ReEntryLoop

**Description**: 
    Bounded deterministic re-entry loop for execution cycles.

    Provides retry logic with maximum attempt limits.
    No infinite loops, no sleep/time usage.
    

### Methods

#### __init__
**Parameters**: self, max_attempts, cid_registry
**Description**: 
        Initialize ReEntryLoop with maximum attempts.

        Args:
            max_attempts: Maximum number of attempts allowed
            cid_registry: Optional CIDRegistry instance
        

#### should_retry
**Parameters**: self, cycle
**Returns**: bool
**Description**: 
        Determine if execution cycle should be retried.

        Args:
            cycle: Current execution cycle

        Returns:
            True if cycle.attempt < max_attempts
        

#### advance
**Parameters**: self, cycle
**Returns**: ExecutionCycle
**Description**: 
        Advance to next attempt cycle.

        Calls CIDRegistry.next_attempt.

        Args:
            cycle: Current execution cycle

        Returns:
            Next execution cycle with incremented attempt
        

#### new_cycle
**Parameters**: self, cid
**Returns**: ExecutionCycle
**Description**: 
        Create new execution cycle for given CID.

        Args:
            cid: Correlation ID for the cycle

        Returns:
            New ExecutionCycle with attempt=1
        

#### get_cycle
**Parameters**: self, cid
**Description**: 
        Get current cycle for given CID.

        Args:
            cid: Correlation ID to lookup

        Returns:
            Current ExecutionCycle or None if not found
        

#### update_status
**Parameters**: self, cid, status
**Description**: 
        Update status for given CID.

        Args:
            cid: Correlation ID to update
            status: New status value

        Returns:
            Updated ExecutionCycle or None if CID not found
        



## Function: __init__

**Parameters**: self, max_attempts, cid_registry
**Description**: 
        Initialize ReEntryLoop with maximum attempts.

        Args:
            max_attempts: Maximum number of attempts allowed
            cid_registry: Optional CIDRegistry instance
        



## Function: should_retry

**Parameters**: self, cycle
**Returns**: bool
**Description**: 
        Determine if execution cycle should be retried.

        Args:
            cycle: Current execution cycle

        Returns:
            True if cycle.attempt < max_attempts
        



## Function: advance

**Parameters**: self, cycle
**Returns**: ExecutionCycle
**Description**: 
        Advance to next attempt cycle.

        Calls CIDRegistry.next_attempt.

        Args:
            cycle: Current execution cycle

        Returns:
            Next execution cycle with incremented attempt
        



## Function: new_cycle

**Parameters**: self, cid
**Returns**: ExecutionCycle
**Description**: 
        Create new execution cycle for given CID.

        Args:
            cid: Correlation ID for the cycle

        Returns:
            New ExecutionCycle with attempt=1
        



## Function: get_cycle

**Parameters**: self, cid
**Description**: 
        Get current cycle for given CID.

        Args:
            cid: Correlation ID to lookup

        Returns:
            Current ExecutionCycle or None if not found
        



## Function: update_status

**Parameters**: self, cid, status
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
# Using ReEntryLoop
reentryloop = ReEntryLoop()
reentryloop.should_retry()
reentryloop.advance()
```

### Function Usage

```python
# Using __init__
result = __init__(max_attempts, cid_registry)
```

```python
# Using should_retry
result = should_retry(cycle)
```

```python
# Using advance
result = advance(cycle)
```



---
**Generated**: 2026-03-26T09:39:03.583885
**Type**: api_reference
**Quality**: comprehensive
