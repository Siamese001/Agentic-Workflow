# API Documentation: monotonic_reentrancy_enforcer

**Target Audience**: developers, api_users

# monotonic_reentrancy_enforcer API Documentation

**File**: `monotonic_reentrancy_enforcer.py`
**Classes**: 2
**Functions**: 3

## Classes

- **NonMonotonicRetryViolation** (inherits from Exception)
- **MonotonicReentrancyEnforcer**

## Functions

- **__init__**
- **get_and_increment_retry_count** -> int
- **validate_monotonicity** -> None


## Class: NonMonotonicRetryViolation

**Description**: Raised when a retry count is not incremented monotonically.

**Inherits from**: Exception



## Class: MonotonicReentrancyEnforcer

**Description**: 
    Ensures that the healing retry_count is strictly monotonic and persistent.

    This enforcer enforces Guarantee #19 by managing the retry count in L4 state,
    making it immune to agent manipulation or system restarts. The `_tier_escalate`
    function, which calls this, must be a pure function with no side-effects other
    than returning the next healing tier.
    

### Methods

#### __init__
**Parameters**: self

#### get_and_increment_retry_count
**Parameters**: self, trace_id
**Returns**: int
**Description**: 
        Retrieves the current retry count for a trace and increments it atomically.

        This is the only way to get a valid retry count. The count is persisted
        in L4, ensuring it survives agent restarts or other interruptions.

        Args:
            trace_id: The unique identifier for the failure trace.

        Returns:
            The new, incremented retry count.
        

#### validate_monotonicity
**Parameters**: self, trace_id, proposed_count
**Returns**: None
**Description**: 
        Validates that a proposed retry count is monotonically correct.

        This would be used by the tier escalation logic to assert that the count
        it received is the one it expected, preventing state desynchronization.

        Args:
            trace_id: The unique identifier for the failure trace.
            proposed_count: The retry count being used in the current operation.

        Raises:
            NonMonotonicRetryViolation: If the proposed count is not exactly one
                                        greater than the persisted count.
        



## Function: __init__

**Parameters**: self


## Function: get_and_increment_retry_count

**Parameters**: self, trace_id
**Returns**: int
**Description**: 
        Retrieves the current retry count for a trace and increments it atomically.

        This is the only way to get a valid retry count. The count is persisted
        in L4, ensuring it survives agent restarts or other interruptions.

        Args:
            trace_id: The unique identifier for the failure trace.

        Returns:
            The new, incremented retry count.
        



## Function: validate_monotonicity

**Parameters**: self, trace_id, proposed_count
**Returns**: None
**Description**: 
        Validates that a proposed retry count is monotonically correct.

        This would be used by the tier escalation logic to assert that the count
        it received is the one it expected, preventing state desynchronization.

        Args:
            trace_id: The unique identifier for the failure trace.
            proposed_count: The retry count being used in the current operation.

        Raises:
            NonMonotonicRetryViolation: If the proposed count is not exactly one
                                        greater than the persisted count.
        



## Usage Examples

### Class Usage

```python
# Using NonMonotonicRetryViolation
nonmonotonicretryviolation = NonMonotonicRetryViolation()
```

```python
# Using MonotonicReentrancyEnforcer
monotonicreentrancyenforcer = MonotonicReentrancyEnforcer()
monotonicreentrancyenforcer.get_and_increment_retry_count()
monotonicreentrancyenforcer.validate_monotonicity()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using get_and_increment_retry_count
result = get_and_increment_retry_count(trace_id)
```

```python
# Using validate_monotonicity
result = validate_monotonicity(trace_id, proposed_count)
```



---
**Generated**: 2026-03-26T09:39:03.832188
**Type**: api_reference
**Quality**: comprehensive
