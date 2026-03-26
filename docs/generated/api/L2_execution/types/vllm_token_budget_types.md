# API Documentation: vllm_token_budget_types

**Target Audience**: developers, api_users

# vllm_token_budget_types API Documentation

**File**: `vllm_token_budget_types.py`
**Classes**: 5
**Functions**: 7

## Classes

- **TaskClass** (inherits from str, Enum)
- **VLLMOutputCapExceeded** (inherits from Exception)
- **VLLMFailureType** (inherits from str, Enum)
- **VLLMPreflightResult**
- **TieredRoutingDecision**

## Functions

- **get_output_cap** -> int | None
- **enforce_output_cap** -> int
- **estimate_tokens_qwen** -> int
- **run_preflight_budget_check** -> VLLMPreflightResult
- **select_local_tier** -> TieredRoutingDecision
- **__init__** -> None
- **__post_init__** -> None


## Class: TaskClass

**Description**: Authoritative task class taxonomy for vLLM output cap enforcement.

**Inherits from**: str, Enum



## Class: VLLMOutputCapExceeded

**Description**: Raised when a local vLLM request would exceed the output cap.

    Caller must route to Gemini-2.5-Pro.
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, task_class, requested, cap, reason
**Returns**: None



## Class: VLLMFailureType

**Description**: Failure classification for vLLM routing decisions.

**Inherits from**: str, Enum



## Class: VLLMPreflightResult

**Description**: Result of the preflight token budget gate.

    Produced before any local vLLM call. Immutable.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: TieredRoutingDecision

**Description**: Immutable routing decision for vLLM tiered routing.

    Produced after preflight check passes.
    



## Function: get_output_cap

**Parameters**: task_class
**Returns**: int | None
**Description**: Return the output token cap for a task class.

    Returns:
        int: Cap in tokens if task_class is known and local.
        None: If task_class is undefined — caller must route to Gemini-2.5-Pro.

    Raises:
        ValueError: If cap would exceed VLLM_MAX_TOKENS_ABSOLUTE.
    



## Function: enforce_output_cap

**Parameters**: requested_tokens, task_class
**Returns**: int
**Description**: Enforce hard ceiling on requested output tokens.

    Args:
        requested_tokens: Caller-requested max_tokens.
        task_class: Task class string from TaskClass enum.

    Returns:
        Enforced token count (never exceeds VLLM_MAX_TOKENS_ABSOLUTE).

    Raises:
        VLLMOutputCapExceeded: If requested_tokens > VLLM_MAX_TOKENS_ABSOLUTE
            and task_class is not in extended whitelist.
    



## Function: estimate_tokens_qwen

**Parameters**: text
**Returns**: int
**Description**: Deterministic token estimation for Qwen2.5 tokenizer family.

    Uses pinned chars-per-token ratio (_QWEN_CHARS_PER_TOKEN = 3).
    Deterministic: identical input → identical output across all runs.
    No external tokenizer library required (L2 purity preserved).

    Args:
        text: Input text to estimate.

    Returns:
        Estimated token count (minimum 1).
    



## Function: run_preflight_budget_check

**Parameters**: prompt, task_class, max_model_len
**Returns**: VLLMPreflightResult
**Description**: Execute preflight token budget gate.

    Algorithm (per spec):
        1. Estimate prompt_tokens
        2. Determine max_output_tokens via task-class cap
        3. Retrieve configured max_model_len
        4. required = prompt_tokens + max_output_tokens
        5. If required > max_model_len - SAFETY_MARGIN_TOKENS:
               route to Gemini-2.5-Pro, emit TOKEN_BUDGET_EXCEEDED
           Else:
               proceed to local tier selection

    Args:
        prompt: Input prompt string.
        task_class: Task class string from TaskClass enum.
        max_model_len: Configured maximum model context length.

    Returns:
        VLLMPreflightResult with all telemetry fields populated.
    



## Function: select_local_tier

**Parameters**: preflight, severity, circuit_breaker_open, queue_overflow, gpu_health_failed, schema_validation_failed, confidence_below_threshold
**Returns**: TieredRoutingDecision
**Description**: Select local execution tier per routing invariants.

    Routing invariants (in priority order):
        1. token budget fails → Gemini-2.5-Pro
        2. circuit breaker open → Gemini-2.5-Pro
        3. queue overflow → Gemini-2.5-Pro
        4. GPU health fails → Gemini-2.5-Pro
        5. schema/semantic validation fails → Gemini-2.5-Pro
        6. confidence < threshold → Gemini-2.5-Pro
        7. Otherwise:
              severity low/medium → 7B (local_fast)
              severity high (non-critical) → 14B (local_strong)

    Gemini-2.5-Pro is NEVER removed from gateway.
    It remains mandatory for all failure states.

    Args:
        preflight: Result of run_preflight_budget_check.
        severity: Severity level string ("low", "medium", "high").
        circuit_breaker_open: Whether circuit breaker is open.
        queue_overflow: Whether request queue is full.
        gpu_health_failed: Whether GPU health check failed.
        schema_validation_failed: Whether schema/semantic validation failed.
        confidence_below_threshold: Whether confidence is below threshold.

    Returns:
        TieredRoutingDecision with tier, model_id, and reason.
    



## Function: __init__

**Parameters**: self, task_class, requested, cap, reason
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using TaskClass
taskclass = TaskClass()
```

```python
# Using VLLMOutputCapExceeded
vllmoutputcapexceeded = VLLMOutputCapExceeded()
```

```python
# Using VLLMFailureType
vllmfailuretype = VLLMFailureType()
```

### Function Usage

```python
# Using get_output_cap
result = get_output_cap(task_class)
```

```python
# Using enforce_output_cap
result = enforce_output_cap(requested_tokens, task_class)
```

```python
# Using estimate_tokens_qwen
result = estimate_tokens_qwen(text)
```



---
**Generated**: 2026-03-26T09:39:04.042401
**Type**: api_reference
**Quality**: comprehensive
