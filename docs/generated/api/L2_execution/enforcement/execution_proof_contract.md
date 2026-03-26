# API Documentation: execution_proof_contract

**Target Audience**: developers, api_users

# execution_proof_contract API Documentation

**File**: `execution_proof_contract.py`
**Classes**: 2
**Functions**: 9

## Classes

- **DeterminismViolation** (inherits from RuntimeError)
- **ExecutionProofRecord**

## Functions

- **_hash_any** -> str
- **_target_hash** -> str
- **_compute_replay_key** -> str
- **_compute_determinism_digest** -> str
- **_sign_execution_trace** -> str
- **emit_execution_proof** -> ExecutionProofRecord
- **_emit_compares_proof** -> None
- **__init__** -> None
- **validate_replay** -> bool


## Class: DeterminismViolation

**Description**: Raised when replay recomputation does not match the original proof.

    ADG edge: compares_proof (via validate_replay)
    

**Inherits from**: RuntimeError



## Class: ExecutionProofRecord

**Description**: Container holding an emitted ExecutionProof.

    Wraps the frozen ExecutionProof with replay validation support.
    

### Methods

#### __init__
**Parameters**: self, proof
**Returns**: None

#### validate_replay
**Parameters**: self, replay_callable, replay_input
**Returns**: bool
**Description**: Validate replay: recompute key + digest and compare to original.

        Emits ``compares_proof`` ADG edge.

        Raises:
            DeterminismViolation: if replay key or digest do not match.
        



## Function: _hash_any

**Parameters**: obj
**Returns**: str


## Function: _target_hash

**Parameters**: target_callable
**Returns**: str


## Function: _compute_replay_key

**Parameters**: trace_id, run_id, input_hash, target_hash, policy_hash
**Returns**: str
**Description**: Deterministic replay key binding all execution inputs.

    Emits ``emits_replay_key`` ADG edge.
    



## Function: _compute_determinism_digest

**Parameters**: replay_key, output_hash, elapsed_ms
**Returns**: str
**Description**: Determinism digest covering replay key + output + timing.

    Emits ``emits_determinism_digest`` ADG edge.
    



## Function: _sign_execution_trace

**Parameters**: proof_id, replay_key, digest, policy_hash, output_hash
**Returns**: str
**Description**: Sign the execution proof over all deterministic fields.

    Emits ``signs_execution_trace`` ADG edge.
    



## Function: emit_execution_proof

**Parameters**: execution_context, execution_result, policy_context, trace_context
**Returns**: ExecutionProofRecord
**Description**: Mandatory post-execution proof emission.

    Args:
        execution_context:  ExecutionContext (or any object with run_id, trace_id).
        execution_result:   The output produced by the execution.
        policy_context:     Policy context object carrying policy_hash.
        trace_context:      Trace context (or active trace object).
        target_callable:    The callable that was executed (for target_hash).
        elapsed_ms:         Elapsed execution time in milliseconds.

    Returns:
        ExecutionProofRecord — immutable, signed, replay-valid.

    Raises:
        RuntimeError: if proof cannot be constructed (fail-closed).
    



## Function: _emit_compares_proof

**Parameters**: proof_id, matched
**Returns**: None
**Description**: ADG edge: compares_proof — emitted during replay validation.



## Function: __init__

**Parameters**: self, proof
**Returns**: None


## Function: validate_replay

**Parameters**: self, replay_callable, replay_input
**Returns**: bool
**Description**: Validate replay: recompute key + digest and compare to original.

        Emits ``compares_proof`` ADG edge.

        Raises:
            DeterminismViolation: if replay key or digest do not match.
        



## Usage Examples

### Class Usage

```python
# Using DeterminismViolation
determinismviolation = DeterminismViolation()
```

```python
# Using ExecutionProofRecord
executionproofrecord = ExecutionProofRecord()
executionproofrecord.validate_replay()
```

### Function Usage

```python
# Using _hash_any
result = _hash_any(obj)
```

```python
# Using _target_hash
result = _target_hash(target_callable)
```

```python
# Using _compute_replay_key
result = _compute_replay_key(trace_id, run_id)
```



---
**Generated**: 2026-03-26T09:39:03.697941
**Type**: api_reference
**Quality**: comprehensive
