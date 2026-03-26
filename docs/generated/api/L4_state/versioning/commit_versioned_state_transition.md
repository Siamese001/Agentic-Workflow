# API Documentation: commit_versioned_state_transition

**Target Audience**: developers, api_users

# commit_versioned_state_transition API Documentation

**File**: `commit_versioned_state_transition.py`
**Classes**: 1
**Functions**: 6

## Classes

- **MutationPayload**

## Functions

- **state_transition_committed** -> None
- **conflict_detected** -> None
- **commit_versioned_state_transition** -> StateTransitionRecord
- **commit_simple_transition** -> StateTransitionRecord
- **read_versioned_state**
- **create** -> MutationPayload


## Class: MutationPayload

**Description**: Payload describing a state mutation.

### Methods

#### create
**Parameters**: cls, key, old_value, new_value, metadata
**Returns**: MutationPayload



## Function: state_transition_committed

**Parameters**: transition_id, namespace, key, version, run_id, trace_id, actor_id
**Returns**: None
**Description**: ADG edge emitter for state_transition_committed.



## Function: conflict_detected

**Parameters**: namespace, key, expected, actual
**Returns**: None
**Description**: ADG edge emitter for conflict_detected.



## Function: commit_versioned_state_transition

**Parameters**: state_context, mutation_payload, actor_context
**Returns**: StateTransitionRecord
**Description**: Mandatory entrypoint for all state mutations — P2/L4 spec §3.

    Steps (in order, all mandatory):
      1. validate namespace
      2. load previous version
      3. compute mutation hash
      4. assign new version
      5. persist state transition
      6. determine snapshot requirement
      7. bind to trace

    Args:
        state_context: StateContext with namespace, key, run_id, trace_id
        mutation_payload: MutationPayload with old_value, new_value, metadata
        actor_context: ActorContext with actor_id, cause_hash
        registry: StateVersionRegistry to use (uses global if None)
        snapshot_policy: When to create snapshots
        run_completed: Whether the run is completed
        irreversible_mutation: Whether this mutation is irreversible
        stage_completion: Whether this is a stage completion boundary
        policy_critical: Whether this is policy-critical
        expected_previous_version: Expected previous version for conflict detection

    Returns:
        StateTransitionRecord for the committed transition

    Raises:
        StateNamespaceError: If namespace validation fails (step 1)
        StateVersionMissingError: If previous version required but missing (step 2)
        StateConflictError: If concurrent write conflict detected (step 4)
    



## Function: commit_simple_transition

**Parameters**: state_namespace, key, old_value, new_value, actor_id, run_id, trace_id
**Returns**: StateTransitionRecord
**Description**: Convenience wrapper for simple state transitions.



## Function: read_versioned_state

**Parameters**: state_namespace, key, run_id, trace_id
**Description**: Read state with version binding (spec §5).



## Function: create

**Parameters**: cls, key, old_value, new_value, metadata
**Returns**: MutationPayload


## Usage Examples

### Class Usage

```python
# Using MutationPayload
mutationpayload = MutationPayload()
mutationpayload.create()
```

### Function Usage

```python
# Using state_transition_committed
result = state_transition_committed(transition_id, namespace)
```

```python
# Using conflict_detected
result = conflict_detected(namespace, key)
```

```python
# Using commit_versioned_state_transition
result = commit_versioned_state_transition(state_context, mutation_payload)
```



---
**Generated**: 2026-03-26T09:39:04.685313
**Type**: api_reference
**Quality**: comprehensive
