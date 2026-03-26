# API Documentation: vllm_concurrency_types

**Target Audience**: developers, api_users

# vllm_concurrency_types API Documentation

**File**: `vllm_concurrency_types.py`
**Classes**: 3
**Functions**: 3

## Classes

- **VLLMStressRequest**
- **VLLMStressResult**
- **VLLMConcurrencyValidationResult**

## Functions

- **build_worst_case_prompt** -> str
- **run_stress_batch** -> list[VLLMStressResult]
- **validate_concurrency_headroom** -> VLLMConcurrencyValidationResult


## Class: VLLMStressRequest

**Description**: A single deterministic stress request near the budget ceiling.

    Immutable. Used to simulate worst-case prompt + max_output_tokens.
    



## Class: VLLMStressResult

**Description**: Result of a single stress request evaluation.

    Immutable. Records preflight outcome and truncation status.
    



## Class: VLLMConcurrencyValidationResult

**Description**: Aggregated result of a concurrency stress validation run.

    Immutable. Used for evidence reporting.
    



## Function: build_worst_case_prompt

**Parameters**: profile, task_class_cap
**Returns**: str
**Description**: Build a worst-case prompt that fills the budget ceiling.

    Constructs a prompt whose token estimate equals:
        max_model_len - SAFETY_MARGIN_TOKENS - task_class_cap - 1

    This is the largest prompt that should still pass preflight.

    Args:
        profile: Serving profile defining max_model_len.
        task_class_cap: Output cap for the task class.

    Returns:
        Deterministic prompt string at budget ceiling.
    



## Function: run_stress_batch

**Parameters**: profile, requests
**Returns**: list[VLLMStressResult]
**Description**: Execute a batch of stress requests against a serving profile.

    Evaluates each request via preflight check. Records:
    - Whether truncation would occur (total_tokens > max_model_len)
    - Whether unexpected fallback occurred (budget_ok=True but route_to_gemini=True)

    Args:
        profile: Serving profile to validate against.
        requests: List of stress requests to evaluate.

    Returns:
        List of VLLMStressResult, one per request.
    



## Function: validate_concurrency_headroom

**Parameters**: profile, requests
**Returns**: VLLMConcurrencyValidationResult
**Description**: Validate KV-cache headroom under concurrent request load.

    Asserts:
    1. No request exceeds VLLM_MAX_TOKENS_ABSOLUTE output tokens.
    2. No unexpected fallback when token_budget_ok=True.
    3. No truncation within max_model_len.

    Args:
        profile: Serving profile to validate.
        requests: Concurrent requests to simulate (len <= max_num_seqs).

    Returns:
        VLLMConcurrencyValidationResult with full telemetry.
    



## Usage Examples

### Class Usage

```python
# Using VLLMStressRequest
vllmstressrequest = VLLMStressRequest()
```

```python
# Using VLLMStressResult
vllmstressresult = VLLMStressResult()
```

```python
# Using VLLMConcurrencyValidationResult
vllmconcurrencyvalidationresult = VLLMConcurrencyValidationResult()
```

### Function Usage

```python
# Using build_worst_case_prompt
result = build_worst_case_prompt(profile, task_class_cap)
```

```python
# Using run_stress_batch
result = run_stress_batch(profile, requests)
```

```python
# Using validate_concurrency_headroom
result = validate_concurrency_headroom(profile, requests)
```



---
**Generated**: 2026-03-26T09:39:04.021900
**Type**: api_reference
**Quality**: comprehensive
