# API Documentation: vllm_gateway_integration_types

**Target Audience**: developers, api_users

# vllm_gateway_integration_types API Documentation

**File**: `vllm_gateway_integration_types.py`
**Classes**: 5
**Functions**: 17

## Classes

- **VLLMLocalRequest**
- **VLLMQueueController**
- **VLLMCircuitBreakerRegistry**
- **VLLMGatewayTelemetry**
- **VLLMGatewayCallResult**

## Functions

- **select_serving_profile** -> VLLMServingProfile
- **shape_local_request** -> VLLMLocalRequest
- **evaluate_gateway_call** -> VLLMGatewayCallResult
- **__init__** -> None
- **snapshot** -> VLLMQueueState
- **acquire** -> bool
- **release** -> None
- **depth** -> int
- **__init__** -> None
- **get** -> VLLMCircuitBreaker
- **record_failure** -> None
- **record_success** -> None
- **is_open** -> bool
- **reset** -> None
- **reset_all** -> None
- **as_dict** -> dict[str, Any]
- **__post_init__**


## Class: VLLMLocalRequest

**Description**: Shaped local vLLM request payload.

    Immutable. All fields are explicit — no None max_tokens.
    Determinism policy enforced: temperature=0, top_p=1.0, seed=42.
    



## Class: VLLMQueueController

**Description**: Threadsafe bounded queue counter for backpressure enforcement.

    Maintains an in-memory queue depth counter. Does not spawn threads.
    

### Methods

#### __init__
**Parameters**: self, max_depth, timeout_seconds
**Returns**: None

#### snapshot
**Parameters**: self, oldest_wait_seconds
**Returns**: VLLMQueueState
**Description**: Return an immutable snapshot of current queue state.

#### acquire
**Parameters**: self
**Returns**: bool
**Description**: Attempt to acquire a queue slot. Returns True if slot acquired.

#### release
**Parameters**: self
**Returns**: None
**Description**: Release a queue slot.

#### depth
**Parameters**: self
**Returns**: int



## Class: VLLMCircuitBreakerRegistry

**Description**: Registry of circuit breakers, one per tier.

    Threadsafe. Breakers are created on first access.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get
**Parameters**: self, tier
**Returns**: VLLMCircuitBreaker

#### record_failure
**Parameters**: self, tier
**Returns**: None

#### record_success
**Parameters**: self, tier
**Returns**: None

#### is_open
**Parameters**: self, tier
**Returns**: bool

#### reset
**Parameters**: self, tier
**Returns**: None

#### reset_all
**Parameters**: self
**Returns**: None



## Class: VLLMGatewayTelemetry

**Description**: Immutable telemetry payload for a single gateway call.

    All fields are deterministic; no timestamps. Stable key ordering via as_dict().
    PHASE 4: Extended with infrastructure fingerprint fields for replay sealing.
    

### Methods

#### as_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return stable-ordered dict representation.



## Class: VLLMGatewayCallResult

**Description**: Result of a gateway call-path evaluation.

    Contains routing decision, shaped request (if local), and telemetry.

    PHASE 5: Includes invariant_violations list for runtime enforcement.
    

### Methods

#### __post_init__
**Parameters**: self
**Description**: Initialize invariant_violations to empty list if None.



## Function: select_serving_profile

**Parameters**: severity
**Returns**: VLLMServingProfile
**Description**: Select serving profile based on severity.

    Routing invariant (mirrors Phase 1 tier selection):
        severity high  → LOCAL_STRONG_14B
        severity low/medium → LOCAL_FAST_7B

    Args:
        severity: Severity level string ("low", "medium", "high").

    Returns:
        VLLMServingProfile for the selected tier.
    



## Function: shape_local_request

**Parameters**: prompt, task_class, profile
**Returns**: VLLMLocalRequest
**Description**: Shape a local vLLM request with deterministic parameters.

    Args:
        prompt: Input prompt string.
        task_class: Task class string from TaskClass enum.
        profile: Selected serving profile.

    Returns:
        VLLMLocalRequest with explicit max_tokens and determinism policy.
    



## Function: evaluate_gateway_call

**Parameters**: prompt, task_class, severity, queue_controller, breaker_registry, oldest_wait_seconds, fingerprint
**Returns**: VLLMGatewayCallResult
**Description**: Evaluate a full gateway call path deterministically.

    Routing invariants (in priority order):
        1. Backpressure (circuit breaker open / queue full / timeout) → Gemini
        2. Token budget exceeded → Gemini
        3. Otherwise → local tier (7B or 14B based on severity)

    Args:
        prompt: Input prompt string.
        task_class: Task class string from TaskClass enum.
        severity: Severity level ("low", "medium", "high").
        queue_controller: In-gateway queue depth controller.
        breaker_registry: Circuit breaker registry.
        oldest_wait_seconds: Age of oldest queued request in seconds.
        fingerprint: Optional infrastructure fingerprint for Phase 4 replay sealing.

    Returns:
        VLLMGatewayCallResult with routing decision, shaped request, telemetry.
    



## Function: __init__

**Parameters**: self, max_depth, timeout_seconds
**Returns**: None


## Function: snapshot

**Parameters**: self, oldest_wait_seconds
**Returns**: VLLMQueueState
**Description**: Return an immutable snapshot of current queue state.



## Function: acquire

**Parameters**: self
**Returns**: bool
**Description**: Attempt to acquire a queue slot. Returns True if slot acquired.



## Function: release

**Parameters**: self
**Returns**: None
**Description**: Release a queue slot.



## Function: depth

**Parameters**: self
**Returns**: int


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get

**Parameters**: self, tier
**Returns**: VLLMCircuitBreaker


## Function: record_failure

**Parameters**: self, tier
**Returns**: None


## Function: record_success

**Parameters**: self, tier
**Returns**: None


## Function: is_open

**Parameters**: self, tier
**Returns**: bool


## Function: reset

**Parameters**: self, tier
**Returns**: None


## Function: reset_all

**Parameters**: self
**Returns**: None


## Function: as_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return stable-ordered dict representation.



## Function: __post_init__

**Parameters**: self
**Description**: Initialize invariant_violations to empty list if None.



## Usage Examples

### Class Usage

```python
# Using VLLMLocalRequest
vllmlocalrequest = VLLMLocalRequest()
```

```python
# Using VLLMQueueController
vllmqueuecontroller = VLLMQueueController()
vllmqueuecontroller.snapshot()
vllmqueuecontroller.acquire()
```

```python
# Using VLLMCircuitBreakerRegistry
vllmcircuitbreakerregistry = VLLMCircuitBreakerRegistry()
vllmcircuitbreakerregistry.get()
vllmcircuitbreakerregistry.record_failure()
```

### Function Usage

```python
# Using select_serving_profile
result = select_serving_profile(severity)
```

```python
# Using shape_local_request
result = shape_local_request(prompt, task_class)
```

```python
# Using evaluate_gateway_call
result = evaluate_gateway_call(prompt, task_class)
```



---
**Generated**: 2026-03-26T09:39:04.027929
**Type**: api_reference
**Quality**: comprehensive
