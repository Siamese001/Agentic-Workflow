# API Documentation: qwen_circuit_breaker

**Target Audience**: developers, api_users

# qwen_circuit_breaker API Documentation

**File**: `qwen_circuit_breaker.py`
**Classes**: 1
**Functions**: 4

## Classes

- **QwenCircuitBreaker**

## Functions

- **__init__**
- **record_failure** -> bool
- **is_circuit_open** -> bool
- **get_status** -> dict[str, Any]


## Class: QwenCircuitBreaker

**Description**: Deterministic circuit breaker with replay safety.

### Methods

#### __init__
**Parameters**: self, replay_mode

#### record_failure
**Parameters**: self, timestamp
**Returns**: bool
**Description**: Record failure with deterministic replay behavior.

#### is_circuit_open
**Parameters**: self, timestamp
**Returns**: bool
**Description**: Check circuit state with deterministic replay behavior.

#### get_status
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current circuit breaker status for health endpoint.



## Function: __init__

**Parameters**: self, replay_mode


## Function: record_failure

**Parameters**: self, timestamp
**Returns**: bool
**Description**: Record failure with deterministic replay behavior.



## Function: is_circuit_open

**Parameters**: self, timestamp
**Returns**: bool
**Description**: Check circuit state with deterministic replay behavior.



## Function: get_status

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current circuit breaker status for health endpoint.



## Usage Examples

### Class Usage

```python
# Using QwenCircuitBreaker
qwencircuitbreaker = QwenCircuitBreaker()
qwencircuitbreaker.record_failure()
qwencircuitbreaker.is_circuit_open()
```

### Function Usage

```python
# Using __init__
result = __init__(replay_mode)
```

```python
# Using record_failure
result = record_failure(timestamp)
```

```python
# Using is_circuit_open
result = is_circuit_open(timestamp)
```



---
**Generated**: 2026-03-26T09:39:03.834257
**Type**: api_reference
**Quality**: comprehensive
