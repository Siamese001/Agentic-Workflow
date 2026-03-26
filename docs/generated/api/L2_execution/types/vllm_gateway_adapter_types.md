# API Documentation: vllm_gateway_adapter_types

**Target Audience**: developers, api_users

# vllm_gateway_adapter_types API Documentation

**File**: `vllm_gateway_adapter_types.py`
**Classes**: 1
**Functions**: 7

## Classes

- **VLLMGatewayAdapter**

## Functions

- **_get_default_queue** -> VLLMQueueController
- **_get_default_registry** -> VLLMCircuitBreakerRegistry
- **reset_singletons** -> None
- **emit_seam_proof** -> str
- **evaluate** -> VLLMGatewayCallResult
- **record_local_failure** -> None
- **record_local_success** -> None


## Class: VLLMGatewayAdapter

**Description**: Thin seam: wraps evaluate_gateway_call with process-level state.

    SovereignLLMGateway instantiates this once (or uses the module-level
    singleton helpers) and calls .evaluate() before choosing a provider.

    Args:
        queue: Optional queue controller override (for testing).
        registry: Optional circuit breaker registry override (for testing).
    

### Methods

#### evaluate
**Parameters**: self, prompt, task_class, severity, oldest_wait_seconds, fingerprint
**Returns**: VLLMGatewayCallResult
**Description**: Evaluate the call path and return a routing decision.

        PHASE 5: Includes invariant verification at execution boundary.
        FAIL violations trigger Gemini fallback with violations in telemetry.

        Args:
            prompt: Input prompt string.
            task_class: Task class string from TaskClass enum.
            severity: Severity level ("low", "medium", "high").
            oldest_wait_seconds: Age of oldest queued request in seconds.
            fingerprint: Optional infrastructure fingerprint for Phase 4 replay sealing.

        Returns:
            VLLMGatewayCallResult with routing decision + telemetry + violations (if any).
        

#### record_local_failure
**Parameters**: self, severity
**Returns**: None
**Description**: Record a local vLLM failure for circuit breaker tracking.

#### record_local_success
**Parameters**: self, severity
**Returns**: None
**Description**: Record a local vLLM success for circuit breaker tracking.



## Function: _get_default_queue

**Returns**: VLLMQueueController


## Function: _get_default_registry

**Returns**: VLLMCircuitBreakerRegistry


## Function: reset_singletons

**Returns**: None
**Description**: Reset process-level singletons. For testing only.



## Function: emit_seam_proof

**Returns**: str
**Description**: Return the seam proof marker string. Used by evidence runner.



## Function: evaluate

**Parameters**: self, prompt, task_class, severity, oldest_wait_seconds, fingerprint
**Returns**: VLLMGatewayCallResult
**Description**: Evaluate the call path and return a routing decision.

        PHASE 5: Includes invariant verification at execution boundary.
        FAIL violations trigger Gemini fallback with violations in telemetry.

        Args:
            prompt: Input prompt string.
            task_class: Task class string from TaskClass enum.
            severity: Severity level ("low", "medium", "high").
            oldest_wait_seconds: Age of oldest queued request in seconds.
            fingerprint: Optional infrastructure fingerprint for Phase 4 replay sealing.

        Returns:
            VLLMGatewayCallResult with routing decision + telemetry + violations (if any).
        



## Function: record_local_failure

**Parameters**: self, severity
**Returns**: None
**Description**: Record a local vLLM failure for circuit breaker tracking.



## Function: record_local_success

**Parameters**: self, severity
**Returns**: None
**Description**: Record a local vLLM success for circuit breaker tracking.



## Usage Examples

### Class Usage

```python
# Using VLLMGatewayAdapter
vllmgatewayadapter = VLLMGatewayAdapter()
vllmgatewayadapter.evaluate()
vllmgatewayadapter.record_local_failure()
```

### Function Usage

```python
# Using _get_default_queue
result = _get_default_queue()
```

```python
# Using _get_default_registry
result = _get_default_registry()
```

```python
# Using reset_singletons
result = reset_singletons()
```



---
**Generated**: 2026-03-26T09:39:04.024493
**Type**: api_reference
**Quality**: comprehensive
