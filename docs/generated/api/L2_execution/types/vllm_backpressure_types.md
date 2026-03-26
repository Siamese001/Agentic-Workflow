# API Documentation: vllm_backpressure_types

**Target Audience**: developers, api_users

# vllm_backpressure_types API Documentation

**File**: `vllm_backpressure_types.py`
**Classes**: 4
**Functions**: 7

## Classes

- **VLLMQueueState**
- **CircuitBreakerState** (inherits from str, Enum)
- **VLLMCircuitBreaker**
- **BackpressureDecision**

## Functions

- **evaluate_backpressure** -> BackpressureDecision
- **is_full** -> bool
- **is_timed_out** -> bool
- **record_failure** -> None
- **record_success** -> None
- **reset** -> None
- **is_open** -> bool


## Class: VLLMQueueState

**Description**: Immutable snapshot of the vLLM request queue state.

    Used for backpressure decisions. Produced before routing.
    

### Methods

#### is_full
**Parameters**: self
**Returns**: bool

#### is_timed_out
**Parameters**: self
**Returns**: bool



## Class: CircuitBreakerState

**Description**: Circuit breaker state for local vLLM tier.

**Inherits from**: str, Enum



## Class: VLLMCircuitBreaker

**Description**: Mutable circuit breaker for a single vLLM tier.

    Tracks consecutive failures and opens the circuit when threshold exceeded.
    

### Methods

#### record_failure
**Parameters**: self
**Returns**: None

#### record_success
**Parameters**: self
**Returns**: None

#### reset
**Parameters**: self
**Returns**: None

#### is_open
**Parameters**: self
**Returns**: bool



## Class: BackpressureDecision

**Description**: Immutable backpressure escalation decision.

    Produced when queue or circuit breaker state forces Gemini escalation.
    



## Function: evaluate_backpressure

**Parameters**: queue_state, circuit_breaker
**Returns**: BackpressureDecision
**Description**: Evaluate backpressure conditions and produce escalation decision.

    Invariants (in priority order):
        1. Circuit breaker open → Gemini-2.5-Pro immediately
        2. Queue full → Gemini-2.5-Pro immediately
        3. Queue wait timed out → Gemini-2.5-Pro immediately
        4. Otherwise → proceed to local tier

    Gemini-2.5-Pro is always reachable as escalation path.

    Args:
        queue_state: Current queue snapshot.
        circuit_breaker: Current circuit breaker state.

    Returns:
        BackpressureDecision with escalation flag and reason.
    



## Function: is_full

**Parameters**: self
**Returns**: bool


## Function: is_timed_out

**Parameters**: self
**Returns**: bool


## Function: record_failure

**Parameters**: self
**Returns**: None


## Function: record_success

**Parameters**: self
**Returns**: None


## Function: reset

**Parameters**: self
**Returns**: None


## Function: is_open

**Parameters**: self
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using VLLMQueueState
vllmqueuestate = VLLMQueueState()
vllmqueuestate.is_full()
vllmqueuestate.is_timed_out()
```

```python
# Using CircuitBreakerState
circuitbreakerstate = CircuitBreakerState()
```

```python
# Using VLLMCircuitBreaker
vllmcircuitbreaker = VLLMCircuitBreaker()
vllmcircuitbreaker.record_failure()
vllmcircuitbreaker.record_success()
```

### Function Usage

```python
# Using evaluate_backpressure
result = evaluate_backpressure(queue_state, circuit_breaker)
```

```python
# Using is_full
result = is_full()
```

```python
# Using is_timed_out
result = is_timed_out()
```



---
**Generated**: 2026-03-26T09:39:04.018944
**Type**: api_reference
**Quality**: comprehensive
