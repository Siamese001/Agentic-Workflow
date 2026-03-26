# API Documentation: cache_admission_gate

**Target Audience**: developers, api_users

# cache_admission_gate API Documentation

**File**: `cache_admission_gate.py`
**Classes**: 2
**Functions**: 7

## Classes

- **CacheAdmissionDecision**
- **CacheAdmissionGate**

## Functions

- **_get_determinism_fns**
- **to_dict** -> dict[str, object]
- **to_json** -> str
- **stable_hash** -> str
- **__init__** -> None
- **evaluate** -> CacheAdmissionDecision
- **get_stats** -> dict[str, Any]


## Class: CacheAdmissionDecision

**Description**: Frozen record of a single cache admission gate evaluation.

    Attributes
    ----------
    artifact_type:
        Always ``CACHE_ADMISSION_DECISION``.
    query_hash:
        SHA-256 hexdigest of the query (u0_hash).
    policy_hash:
        SHA-256 hexdigest of the active policy.
    embedder_version:
        Embedder version tag used for this retrieval.
    admitted:
        True if all four gates passed.
    deny_reasons:
        Tuple of stable deny reason codes (empty when admitted).
    support_score:
        Support validation score supplied by the caller.
    completeness_score:
        Completeness score supplied by the caller.
    policy_conflict:
        True if a policy conflict was detected.
    replay_contaminated:
        True if replay-sensitive content was found in the result set.
    timestamp_utc:
        Unix timestamp provided by the caller.
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, object]

#### to_json
**Parameters**: self
**Returns**: str

#### stable_hash
**Parameters**: self
**Returns**: str



## Class: CacheAdmissionGate

**Description**: Evaluates four admission criteria before allowing a retrieval result
    into the semantic cache.

    Usage
    -----
    .. code-block:: python

        gate = CacheAdmissionGate(
            support_threshold=0.65,
            completeness_threshold=0.55,
        )

        decision = gate.evaluate(
            query_hash="a3f7b291..." * 2,   # 64-char SHA-256
            policy_hash="deadbeef..." * 2,
            embedder_version="bge-m3-v1",
            support_score=0.72,
            completeness_score=0.60,
            policy_conflict=False,
            replay_contaminated=False,
            timestamp_utc=1700000000,
        )

        if decision.admitted:
            redis_cache.set(admission_key, result_bytes, ttl_seconds=3600)
    

### Methods

#### __init__
**Parameters**: self, support_threshold, completeness_threshold
**Returns**: None

#### evaluate
**Parameters**: self
**Returns**: CacheAdmissionDecision
**Description**: Evaluate all four admission gates and return a decision record.

        Fail-closed: any unexpected error during evaluation produces a DENIED
        decision with ``INTERNAL_ERROR`` in deny_reasons.

        Parameters
        ----------
        query_hash:
            SHA-256 hexdigest of the query (u0_hash).
        policy_hash:
            SHA-256 hexdigest of the active policy.
        embedder_version:
            Embedder version tag (no colons).
        support_score:
            Float in [0, 1] — support validation score from the RAG evaluator.
        completeness_score:
            Float in [0, 1] — completeness score from the RAG evaluator.
        policy_conflict:
            True if the policy layer detected a conflict for this query.
        replay_contaminated:
            True if the result set contains replay-sensitive content.
        timestamp_utc:
            Unix timestamp provided by the caller.

        Returns
        -------
        CacheAdmissionDecision
            Frozen decision record.  ``admitted=True`` means all gates passed.
        

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return admission gate statistics.



## Function: _get_determinism_fns



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, object]


## Function: to_json

**Parameters**: self
**Returns**: str


## Function: stable_hash

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, support_threshold, completeness_threshold
**Returns**: None


## Function: evaluate

**Parameters**: self
**Returns**: CacheAdmissionDecision
**Description**: Evaluate all four admission gates and return a decision record.

        Fail-closed: any unexpected error during evaluation produces a DENIED
        decision with ``INTERNAL_ERROR`` in deny_reasons.

        Parameters
        ----------
        query_hash:
            SHA-256 hexdigest of the query (u0_hash).
        policy_hash:
            SHA-256 hexdigest of the active policy.
        embedder_version:
            Embedder version tag (no colons).
        support_score:
            Float in [0, 1] — support validation score from the RAG evaluator.
        completeness_score:
            Float in [0, 1] — completeness score from the RAG evaluator.
        policy_conflict:
            True if the policy layer detected a conflict for this query.
        replay_contaminated:
            True if the result set contains replay-sensitive content.
        timestamp_utc:
            Unix timestamp provided by the caller.

        Returns
        -------
        CacheAdmissionDecision
            Frozen decision record.  ``admitted=True`` means all gates passed.
        



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return admission gate statistics.



## Usage Examples

### Class Usage

```python
# Using CacheAdmissionDecision
cacheadmissiondecision = CacheAdmissionDecision()
cacheadmissiondecision.to_dict()
cacheadmissiondecision.to_json()
```

```python
# Using CacheAdmissionGate
cacheadmissiongate = CacheAdmissionGate()
cacheadmissiongate.evaluate()
cacheadmissiongate.get_stats()
```

### Function Usage

```python
# Using _get_determinism_fns
result = _get_determinism_fns()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_json
result = to_json()
```



---
**Generated**: 2026-03-26T09:39:04.564715
**Type**: api_reference
**Quality**: comprehensive
