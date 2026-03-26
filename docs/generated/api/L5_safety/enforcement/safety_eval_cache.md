# API Documentation: safety_eval_cache

**Target Audience**: developers, api_users

# safety_eval_cache API Documentation

**File**: `safety_eval_cache.py`
**Classes**: 1
**Functions**: 6

## Classes

- **SafetyEvalCache**

## Functions

- **get_safety_eval_cache** -> SafetyEvalCache
- **__init__** -> None
- **get** -> dict[str, Any] | None
- **set** -> None
- **get_or_fetch** -> dict[str, Any]
- **invalidate** -> None


## Class: SafetyEvalCache

**Description**: Memoises L5 safety-evaluation results for identical compiled artifacts.

    The cached value is a dict with at least these fields::

        {
            "decision":          "allow" | "block",
            "compliance_hash":   "<64-char hex>",
            "remediation_hints": [...],
        }

    Callers must verify that all three hash inputs still match the current
    execution context before accepting a cached result.

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
**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached evaluation dict or ``None`` on miss/bypass.

        Returns ``None`` (forcing a fresh L5 evaluation) when:
        - The key is not present.
        - Redis is unreachable and the fallback store has no entry.
        - ``replay_mode=True``.
        

#### set
**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash, eval_result
**Returns**: None
**Description**: Store *eval_result* under the deterministic key.

        *eval_result* must contain at minimum ``"decision"`` (``"allow"``
        or ``"block"``) and ``"compliance_hash"`` (a 64-hex SHA-256
        produced by the L5 evaluator).  ``"remediation_hints"`` is
        optional but recommended for observability.
        

#### get_or_fetch
**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash, fetch_from_l5
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached eval or call *fetch_from_l5*.

        *fetch_from_l5* is a zero-argument callable that runs the full L5
        safety evaluation and returns the result dict.  Called only on a
        cache miss.

        This is the canonical wiring point for L5 evaluator engines.  The
        evaluator should call this instead of running a live evaluation on
        every request.

        The returned dict must include at minimum ``"decision"`` and
        ``"compliance_hash"`` — the same contract as ``set()``.
        

#### invalidate
**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash
**Returns**: None
**Description**: Explicitly evict a safety-evaluation entry.



## Function: get_safety_eval_cache

**Returns**: SafetyEvalCache
**Description**: Return the process-global ``SafetyEvalCache`` instance.



## Function: __init__

**Parameters**: self, ttl_seconds, cache
**Returns**: None


## Function: get

**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached evaluation dict or ``None`` on miss/bypass.

        Returns ``None`` (forcing a fresh L5 evaluation) when:
        - The key is not present.
        - Redis is unreachable and the fallback store has no entry.
        - ``replay_mode=True``.
        



## Function: set

**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash, eval_result
**Returns**: None
**Description**: Store *eval_result* under the deterministic key.

        *eval_result* must contain at minimum ``"decision"`` (``"allow"``
        or ``"block"``) and ``"compliance_hash"`` (a 64-hex SHA-256
        produced by the L5 evaluator).  ``"remediation_hints"`` is
        optional but recommended for observability.
        



## Function: get_or_fetch

**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash, fetch_from_l5
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached eval or call *fetch_from_l5*.

        *fetch_from_l5* is a zero-argument callable that runs the full L5
        safety evaluation and returns the result dict.  Called only on a
        cache miss.

        This is the canonical wiring point for L5 evaluator engines.  The
        evaluator should call this instead of running a live evaluation on
        every request.

        The returned dict must include at minimum ``"decision"`` and
        ``"compliance_hash"`` — the same contract as ``set()``.
        



## Function: invalidate

**Parameters**: self, compiled_prompt_hash, policy_hash, toolset_hash
**Returns**: None
**Description**: Explicitly evict a safety-evaluation entry.



## Usage Examples

### Class Usage

```python
# Using SafetyEvalCache
safetyevalcache = SafetyEvalCache()
safetyevalcache.get()
safetyevalcache.set()
```

### Function Usage

```python
# Using get_safety_eval_cache
result = get_safety_eval_cache()
```

```python
# Using __init__
result = __init__(ttl_seconds, cache)
```

```python
# Using get
result = get(compiled_prompt_hash, policy_hash)
```



---
**Generated**: 2026-03-26T09:39:04.921201
**Type**: api_reference
**Quality**: comprehensive
