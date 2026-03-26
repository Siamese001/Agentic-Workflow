# API Documentation: execution_trace_types

**Target Audience**: developers, api_users

# execution_trace_types API Documentation

**File**: `execution_trace_types.py`
**Classes**: 1
**Functions**: 5

## Classes

- **ExecutionTrace**

## Functions

- **canonical_json** -> str
- **create_execution_trace_skeleton** -> ExecutionTrace
- **compute_plan_hash** -> str
- **compute_replay_key** -> str
- **to_dict** -> dict[str, Any]


## Class: ExecutionTrace

**Description**: Execution trace for L3 orchestration audit trail.

### Methods

#### compute_replay_key
**Parameters**: self, transcript_hash
**Returns**: str
**Description**: 
        Compute replay key: SHA256(trace_id + plan_hash + transcript_hash).

        Args:
            transcript_hash: Hash of the execution transcript

        Returns:
            Replay key for deterministic replay verification
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: canonical_json

**Parameters**: data
**Returns**: str
**Description**: 
    Convert dictionary to canonical JSON string.

    Alphabetical key sort, UTF-8, no whitespace variance.
    



## Function: create_execution_trace_skeleton

**Parameters**: trace_id, plan_hash, governed_payload, actor, target
**Returns**: ExecutionTrace
**Description**: 
    Create ExecutionTrace skeleton for L3 orchestration.

    Args:
        trace_id: Unique trace identifier
        plan_hash: Hash of the canonical plan
        governed_payload: The governed payload being processed
        actor: Actor performing the orchestration
        target: Target of the orchestration (optional)

    Returns:
        ExecutionTrace with populated skeleton
    



## Function: compute_plan_hash

**Parameters**: plan
**Returns**: str
**Description**: 
    Compute SHA256 hash of canonical plan JSON.

    Args:
        plan: Plan dictionary to hash

    Returns:
        SHA256 hash of canonical plan JSON
    



## Function: compute_replay_key

**Parameters**: self, transcript_hash
**Returns**: str
**Description**: 
        Compute replay key: SHA256(trace_id + plan_hash + transcript_hash).

        Args:
            transcript_hash: Hash of the execution transcript

        Returns:
            Replay key for deterministic replay verification
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Usage Examples

### Class Usage

```python
# Using ExecutionTrace
executiontrace = ExecutionTrace()
executiontrace.compute_replay_key()
executiontrace.to_dict()
```

### Function Usage

```python
# Using canonical_json
result = canonical_json(data)
```

```python
# Using create_execution_trace_skeleton
result = create_execution_trace_skeleton(trace_id, plan_hash)
```

```python
# Using compute_plan_hash
result = compute_plan_hash(plan)
```



---
**Generated**: 2026-03-26T09:39:04.373064
**Type**: api_reference
**Quality**: comprehensive
