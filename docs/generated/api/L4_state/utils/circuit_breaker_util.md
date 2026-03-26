# API Documentation: circuit_breaker_util

**Target Audience**: developers, api_users

# circuit_breaker_util API Documentation

**File**: `circuit_breaker_util.py`
**Classes**: 3
**Functions**: 6

## Classes

- **CircuitBreakerState** (inherits from Enum)
- **CircuitBreakerOpenError** (inherits from Exception)
- **CircuitBreaker**

## Functions

- **get_breaker** -> CircuitBreaker
- **reset_all_breakers** -> None
- **__init__**
- **can_execute** -> bool
- **record_success** -> None
- **record_failure** -> None


## Class: CircuitBreakerState

**Inherits from**: Enum



## Class: CircuitBreakerOpenError

**Description**: Raised when circuit breaker is open and rejects requests.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, message, breaker_name



## Class: CircuitBreaker

**Description**: Minimal circuit breaker with CLOSED / OPEN / HALF_OPEN states.

    This is intentionally simple and process-local; higher-level
    orchestration (e.g. batch runner) is responsible for coordinating
    breakers across workers if needed.

    Attributes:
        name: Unique identifier for this circuit breaker
        failure_threshold: Number of failures before opening circuit
        reset_after_s: Seconds to wait before attempting recovery
        half_open_max_calls: Successful calls needed to close circuit
        state: Current state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Current count of consecutive failures
        success_count: Current count of consecutive successes
        opened_at: Timestamp when circuit was opened
    

### Methods

#### can_execute
**Parameters**: self
**Returns**: bool
**Description**: Check if execution is allowed based on current state.

        Returns:
            True if execution is allowed, False if circuit is open
        

#### record_success
**Parameters**: self
**Returns**: None
**Description**: Record a successful execution.

#### record_failure
**Parameters**: self
**Returns**: None
**Description**: Record a failed execution.



## Function: get_breaker

**Parameters**: name, failure_threshold, reset_after_s, half_open_max_calls
**Returns**: CircuitBreaker
**Description**: Get or create a circuit breaker by name.

    Args:
        name: Unique identifier for the breaker
        failure_threshold: Number of failures before opening
        reset_after_s: Seconds before attempting recovery
        half_open_max_calls: Successes needed to close

    Returns:
        CircuitBreaker instance
    



## Function: reset_all_breakers

**Returns**: None
**Description**: Reset all circuit breakers (primarily for testing).



## Function: __init__

**Parameters**: self, message, breaker_name


## Function: can_execute

**Parameters**: self
**Returns**: bool
**Description**: Check if execution is allowed based on current state.

        Returns:
            True if execution is allowed, False if circuit is open
        



## Function: record_success

**Parameters**: self
**Returns**: None
**Description**: Record a successful execution.



## Function: record_failure

**Parameters**: self
**Returns**: None
**Description**: Record a failed execution.



## Usage Examples

### Class Usage

```python
# Using CircuitBreakerState
circuitbreakerstate = CircuitBreakerState()
```

```python
# Using CircuitBreakerOpenError
circuitbreakeropenerror = CircuitBreakerOpenError()
```

```python
# Using CircuitBreaker
circuitbreaker = CircuitBreaker()
circuitbreaker.can_execute()
circuitbreaker.record_success()
```

### Function Usage

```python
# Using get_breaker
result = get_breaker(name, failure_threshold)
```

```python
# Using reset_all_breakers
result = reset_all_breakers()
```

```python
# Using __init__
result = __init__(message, breaker_name)
```



---
**Generated**: 2026-03-26T09:39:04.658500
**Type**: api_reference
**Quality**: comprehensive
