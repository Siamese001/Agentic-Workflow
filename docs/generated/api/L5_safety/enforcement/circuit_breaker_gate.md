# API Documentation: circuit_breaker_gate

**Target Audience**: developers, api_users

# circuit_breaker_gate API Documentation

**File**: `circuit_breaker_gate.py`
**Classes**: 6
**Functions**: 22

## Classes

- **CircuitState** (inherits from Enum)
- **CircuitBreakerConfig**
- **CircuitBreakerMetrics**
- **CircuitBreakerOpenError** (inherits from Exception)
- **CircuitBreakerTimeoutError** (inherits from Exception)
- **CircuitBreaker**

## Functions

- **get_breaker** -> 'CircuitBreaker'
- **get_all_breakers** -> dict[str, 'CircuitBreaker']
- **reset_registry** -> None
- **__init__**
- **__init__**
- **__init__**
- **state** -> CircuitState
- **is_closed** -> bool
- **is_open** -> bool
- **is_half_open** -> bool
- **allow_request** -> bool
- **record_success** -> None
- **record_failure** -> None
- **_should_attempt_reset** -> bool
- **_apply_exponential_backoff** -> None
- **_transition_to_open** -> None
- **_transition_to_half_open** -> None
- **_transition_to_closed** -> None
- **get_time_until_retry** -> float
- **protect** -> Callable
- **wrapper**
- **target**


## Class: CircuitState

**Description**: Circuit breaker states per V10 specification.

**Inherits from**: Enum



## Class: CircuitBreakerConfig

**Description**: Configuration for circuit breaker behavior.



## Class: CircuitBreakerMetrics

**Description**: Metrics for observability dashboard.



## Class: CircuitBreakerOpenError

**Description**: Raised when circuit is open and rejecting calls.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, breaker_name, time_until_retry



## Class: CircuitBreakerTimeoutError

**Description**: Raised when execution exceeds the configured timeout.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, breaker_name, timeout



## Class: CircuitBreaker

**Description**: V10-Compliant Circuit Breaker with Non-Blocking Execution Timeout.

### Methods

#### __init__
**Parameters**: self, name, config

#### state
**Parameters**: self
**Returns**: CircuitState
**Description**: Get current circuit state.

#### is_closed
**Parameters**: self
**Returns**: bool
**Description**: Check if circuit is closed (normal operation).

#### is_open
**Parameters**: self
**Returns**: bool
**Description**: Check if circuit is open (rejecting calls).

#### is_half_open
**Parameters**: self
**Returns**: bool
**Description**: Check if circuit is half-open (testing recovery).

#### allow_request
**Parameters**: self
**Returns**: bool
**Description**: 
        Check if a request should be allowed through.

        Returns:
            True if request is allowed, False if circuit is open

        Raises:
            CircuitBreakerOpenError if circuit is open (optional, for detailed info)
        

#### record_success
**Parameters**: self
**Returns**: None
**Description**: Record a successful call.

#### record_failure
**Parameters**: self, error
**Returns**: None
**Description**: Record a failed call.

#### _should_attempt_reset
**Parameters**: self
**Returns**: bool
**Description**: Check if enough time has passed to attempt reset.

#### _apply_exponential_backoff
**Parameters**: self
**Returns**: None
**Description**: Increase timeout exponentially.

#### _transition_to_open
**Parameters**: self
**Returns**: None
**Description**: Transition to OPEN state.

#### _transition_to_half_open
**Parameters**: self
**Returns**: None
**Description**: Transition to HALF_OPEN state.

#### _transition_to_closed
**Parameters**: self
**Returns**: None
**Description**: Transition to CLOSED state.

#### get_time_until_retry
**Parameters**: self
**Returns**: float
**Description**: Get seconds until retry is allowed (for OPEN state).

#### protect
**Parameters**: self, func
**Returns**: Callable
**Description**: Decorator with non-blocking execution timeout.



## Function: get_breaker

**Parameters**: name
**Returns**: 'CircuitBreaker'
**Description**: Get or create a circuit breaker by name using deadlock-free pattern.



## Function: get_all_breakers

**Returns**: dict[str, 'CircuitBreaker']
**Description**: Get all registered circuit breakers for dashboard.



## Function: reset_registry

**Returns**: None
**Description**: Reset the circuit breaker registry - for testing only.



## Function: __init__

**Parameters**: self, breaker_name, time_until_retry


## Function: __init__

**Parameters**: self, breaker_name, timeout


## Function: __init__

**Parameters**: self, name, config


## Function: state

**Parameters**: self
**Returns**: CircuitState
**Description**: Get current circuit state.



## Function: is_closed

**Parameters**: self
**Returns**: bool
**Description**: Check if circuit is closed (normal operation).



## Function: is_open

**Parameters**: self
**Returns**: bool
**Description**: Check if circuit is open (rejecting calls).



## Function: is_half_open

**Parameters**: self
**Returns**: bool
**Description**: Check if circuit is half-open (testing recovery).



## Function: allow_request

**Parameters**: self
**Returns**: bool
**Description**: 
        Check if a request should be allowed through.

        Returns:
            True if request is allowed, False if circuit is open

        Raises:
            CircuitBreakerOpenError if circuit is open (optional, for detailed info)
        



## Function: record_success

**Parameters**: self
**Returns**: None
**Description**: Record a successful call.



## Function: record_failure

**Parameters**: self, error
**Returns**: None
**Description**: Record a failed call.



## Function: _should_attempt_reset

**Parameters**: self
**Returns**: bool
**Description**: Check if enough time has passed to attempt reset.



## Function: _apply_exponential_backoff

**Parameters**: self
**Returns**: None
**Description**: Increase timeout exponentially.



## Function: _transition_to_open

**Parameters**: self
**Returns**: None
**Description**: Transition to OPEN state.



## Function: _transition_to_half_open

**Parameters**: self
**Returns**: None
**Description**: Transition to HALF_OPEN state.



## Function: _transition_to_closed

**Parameters**: self
**Returns**: None
**Description**: Transition to CLOSED state.



## Function: get_time_until_retry

**Parameters**: self
**Returns**: float
**Description**: Get seconds until retry is allowed (for OPEN state).



## Function: protect

**Parameters**: self, func
**Returns**: Callable
**Description**: Decorator with non-blocking execution timeout.



## Function: wrapper



## Function: target



## Usage Examples

### Class Usage

```python
# Using CircuitState
circuitstate = CircuitState()
```

```python
# Using CircuitBreakerConfig
circuitbreakerconfig = CircuitBreakerConfig()
```

```python
# Using CircuitBreakerMetrics
circuitbreakermetrics = CircuitBreakerMetrics()
```

### Function Usage

```python
# Using get_breaker
result = get_breaker(name)
```

```python
# Using get_all_breakers
result = get_all_breakers()
```

```python
# Using reset_registry
result = reset_registry()
```



---
**Generated**: 2026-03-26T09:39:04.784918
**Type**: api_reference
**Quality**: comprehensive
