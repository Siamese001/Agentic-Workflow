# API Documentation: orchestration_plan_cache

**Target Audience**: developers, api_users

# orchestration_plan_cache API Documentation

**File**: `orchestration_plan_cache.py`
**Classes**: 1
**Functions**: 6

## Classes

- **OrchestrationPlanCache**

## Functions

- **get_orchestration_plan_cache** -> OrchestrationPlanCache
- **__init__** -> None
- **get** -> dict[str, Any] | None
- **set** -> None
- **get_or_fetch** -> dict[str, Any]
- **invalidate** -> None


## Class: OrchestrationPlanCache

**Description**: Memoises resolved orchestration plans for identical L3 inputs.

    The cached value is a dict representing the serialisable fields of the
    orchestration plan::

        {
            "step_dag":          [...],   # ordered list of plan steps
            "deduped_tool_calls": [...],  # canonical tool-call list
            "handshake_schedule": [...],  # agent handshake ordering
            "plan_hash":         "<hex>", # echoed back for verification
            "tool_budget_hash":  "<hex>",
        }

    Callers must verify that both ``plan_hash`` and ``tool_budget_hash`` in
    the returned dict match the values used to look it up.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    

### Methods

#### __init__
**Parameters**: self, ttl_seconds, cache
**Returns**: None

#### get
**Parameters**: self, trace_id, plan_hash, tool_budget_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached orchestration plan dict or ``None`` on miss/bypass.

#### set
**Parameters**: self, trace_id, plan_hash, tool_budget_hash, plan
**Returns**: None
**Description**: Store *plan* under the deterministic key.

        *plan* must include ``"plan_hash"`` and ``"tool_budget_hash"`` fields
        echoed back from the orchestrator so downstream callers can verify
        the plan was computed for the exact same inputs.
        

#### get_or_fetch
**Parameters**: self, trace_id, plan_hash, tool_budget_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached plan or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the resolved
        orchestration plan dict from L4.  Called only on a cache miss.

        This is the canonical wiring point for L3 orchestration engines.
        Engines should call this instead of calling ``get()`` and L4 directly.
        

#### invalidate
**Parameters**: self, trace_id, plan_hash, tool_budget_hash
**Returns**: None
**Description**: Explicitly evict a cached orchestration plan.



## Function: get_orchestration_plan_cache

**Returns**: OrchestrationPlanCache
**Description**: Return the process-global ``OrchestrationPlanCache`` instance.



## Function: __init__

**Parameters**: self, ttl_seconds, cache
**Returns**: None


## Function: get

**Parameters**: self, trace_id, plan_hash, tool_budget_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached orchestration plan dict or ``None`` on miss/bypass.



## Function: set

**Parameters**: self, trace_id, plan_hash, tool_budget_hash, plan
**Returns**: None
**Description**: Store *plan* under the deterministic key.

        *plan* must include ``"plan_hash"`` and ``"tool_budget_hash"`` fields
        echoed back from the orchestrator so downstream callers can verify
        the plan was computed for the exact same inputs.
        



## Function: get_or_fetch

**Parameters**: self, trace_id, plan_hash, tool_budget_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached plan or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the resolved
        orchestration plan dict from L4.  Called only on a cache miss.

        This is the canonical wiring point for L3 orchestration engines.
        Engines should call this instead of calling ``get()`` and L4 directly.
        



## Function: invalidate

**Parameters**: self, trace_id, plan_hash, tool_budget_hash
**Returns**: None
**Description**: Explicitly evict a cached orchestration plan.



## Usage Examples

### Class Usage

```python
# Using OrchestrationPlanCache
orchestrationplancache = OrchestrationPlanCache()
orchestrationplancache.get()
orchestrationplancache.set()
```

### Function Usage

```python
# Using get_orchestration_plan_cache
result = get_orchestration_plan_cache()
```

```python
# Using __init__
result = __init__(ttl_seconds, cache)
```

```python
# Using get
result = get(trace_id, plan_hash)
```



---
**Generated**: 2026-03-26T09:39:04.175631
**Type**: api_reference
**Quality**: comprehensive
