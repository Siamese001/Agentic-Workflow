# API Documentation: healing_tier_dispatcher

**Target Audience**: developers, api_users

# healing_tier_dispatcher API Documentation

**File**: `healing_tier_dispatcher.py`
**Classes**: 3
**Functions**: 14

## Classes

- **InvocationRecord**
- **HealingProviderInvoker** (inherits from Protocol)
- **DefaultHealingProviderInvoker**

## Functions

- **_get_l4_prior_provider** -> Any
- **handle_qwen_oom_via_router** -> HealingDecision
- **dispatch_healing** -> tuple[HealingDecision, InvocationRecord]
- **_emit_outcome** -> None
- **_emit_resource_prediction** -> None
- **_emit_rollback_refinement** -> None
- **_emit_pattern_advice** -> None
- **invoke_qwen_with_oom_protection** -> InvocationRecord
- **invoke_local** -> InvocationRecord
- **invoke_qwen_vllm** -> InvocationRecord
- **invoke_gemini** -> InvocationRecord
- **invoke_local** -> InvocationRecord
- **invoke_qwen_vllm** -> InvocationRecord
- **invoke_gemini** -> InvocationRecord


## Class: InvocationRecord

**Description**: Immutable record of a single provider invocation.



## Class: HealingProviderInvoker

**Description**: Interface for healing provider invocation.

    Production implementations perform real LLM/provider calls.
    Test implementations record calls without network access.
    

**Inherits from**: Protocol

### Methods

#### invoke_local
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Ellipsis

#### invoke_qwen_vllm
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Ellipsis

#### invoke_gemini
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Ellipsis



## Class: DefaultHealingProviderInvoker

**Description**: Default production invoker.

    Each method returns an InvocationRecord documenting what was invoked.
    In production, the body of each method would call the real provider SDK.
    Currently stubs that record the invocation without network calls.
    

### Methods

#### invoke_local
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord

#### invoke_qwen_vllm
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord

#### invoke_gemini
**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord



## Function: _get_l4_prior_provider

**Returns**: Any
**Description**: Return a process-global L4MetaPriorProvider backed by HealingSuccessRateStore.

    Falls back to NeutralMetaPriorProvider if the adapter is unavailable (cold start).
    



## Function: handle_qwen_oom_via_router

**Parameters**: healing_input, config
**Returns**: HealingDecision
**Description**: Handle OOM by routing through single choke point.



## Function: dispatch_healing

**Parameters**: healing_input, config
**Returns**: tuple[HealingDecision, InvocationRecord]
**Description**: End-to-end: route tier, then invoke the matching provider.

    Args:
        healing_input: Structured failure context.
        config: Validated healing tier configuration.
        invoker: Injectable provider invoker (default: DefaultHealingProviderInvoker).
        agent_name: Name of the calling agent (for trace).
        outcome_sink: Optional sink for emitting a HealingOutcomeEvent.
            When None (the default), no emission occurs and behaviour is unchanged.
        timestamp_utc: Deterministic timestamp for the outcome event.
            Required when outcome_sink is provided; ignored otherwise.
        resource_predictor: Optional resource predictor for proposal-only predictions.
        rollback_refiner: Optional rollback refiner for proposal-only strategy selection.

    Returns:
        (HealingDecision, InvocationRecord) — the routing decision and invocation trace.
    



## Function: _emit_outcome

**Parameters**: sink
**Returns**: None
**Description**: Emit exactly one HealingOutcomeEvent to the sink.  Fire-and-forget.



## Function: _emit_resource_prediction

**Parameters**: resource_predictor, healing_input, agent_name, timestamp_utc
**Returns**: None
**Description**: Emit resource prediction as proposal-only artifact.



## Function: _emit_rollback_refinement

**Parameters**: rollback_refiner, healing_input, agent_name, timestamp_utc
**Returns**: None
**Description**: Emit rollback refinement as proposal-only artifact.



## Function: _emit_pattern_advice

**Parameters**: pattern_advice, healing_input, agent_name, timestamp_utc
**Returns**: None
**Description**: Emit pattern advice metadata (informational-only).



## Function: invoke_qwen_with_oom_protection

**Parameters**: healing_input, decision, config, invoker, agent_name
**Returns**: InvocationRecord
**Description**: Invoke Qwen with OOM protection and proper escalation.



## Function: invoke_local

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Ellipsis



## Function: invoke_qwen_vllm

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Ellipsis



## Function: invoke_gemini

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord
**Description**: Ellipsis



## Function: invoke_local

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord


## Function: invoke_qwen_vllm

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord


## Function: invoke_gemini

**Parameters**: self, healing_input, decision, config
**Returns**: InvocationRecord


## Usage Examples

### Class Usage

```python
# Using InvocationRecord
invocationrecord = InvocationRecord()
```

```python
# Using HealingProviderInvoker
healingproviderinvoker = HealingProviderInvoker()
healingproviderinvoker.invoke_local()
healingproviderinvoker.invoke_qwen_vllm()
```

```python
# Using DefaultHealingProviderInvoker
defaulthealingproviderinvoker = DefaultHealingProviderInvoker()
defaulthealingproviderinvoker.invoke_local()
defaulthealingproviderinvoker.invoke_qwen_vllm()
```

### Function Usage

```python
# Using _get_l4_prior_provider
result = _get_l4_prior_provider()
```

```python
# Using handle_qwen_oom_via_router
result = handle_qwen_oom_via_router(healing_input, config)
```

```python
# Using dispatch_healing
result = dispatch_healing(healing_input, config)
```



---
**Generated**: 2026-03-26T09:39:03.819668
**Type**: api_reference
**Quality**: comprehensive
