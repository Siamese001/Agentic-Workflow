# API Documentation: lifecycle_policy_applier

**Target Audience**: developers, api_users

# lifecycle_policy_applier API Documentation

**File**: `lifecycle_policy_applier.py`
**Classes**: 1
**Functions**: 21

## Classes

- **StateLifecycleContext**

## Functions

- **lifecycle_policy_applied** -> None
- **lifecycle_transition_recorded** -> None
- **state_active** -> None
- **state_archived** -> None
- **state_deleted** -> None
- **apply_state_lifecycle_policy** -> StateLifecycleRecord
- **_classify_namespace** -> RetentionClass
- **_resolve_lifecycle_policy** -> Any | None
- **_create_default_policy** -> Any
- **_determine_status_transition** -> str
- **_emit_lifecycle_decision** -> None
- **record_lifecycle_transition** -> StateLifecycleRecord
- **record_state_archival** -> StateLifecycleRecord
- **record_state_deletion** -> StateLifecycleRecord
- **query_state_lifecycle** -> list[StateLifecycleRecord]
- **apply_simple_lifecycle_policy** -> StateLifecycleRecord
- **create** -> StateLifecycleContext
- **lifecycle_policy_applied** -> None
- **lifecycle_transition_recorded** -> None
- **state_archived** -> None
- **state_deleted** -> None


## Class: StateLifecycleContext

**Description**: Context for state lifecycle policy application.

### Methods

#### create
**Parameters**: cls, state_namespace, state_version, access_type, actor_id, trace_id
**Returns**: StateLifecycleContext



## Function: lifecycle_policy_applied

**Parameters**: namespace, policy_id, status, retention
**Returns**: None
**Description**: ADG edge emitter for lifecycle_policy_applied.



## Function: lifecycle_transition_recorded

**Parameters**: namespace, from_status, to_status, reason
**Returns**: None
**Description**: ADG edge emitter for lifecycle_transition_recorded.



## Function: state_active

**Parameters**: namespace, location, actor
**Returns**: None
**Description**: ADG edge emitter for state_active.



## Function: state_archived

**Parameters**: namespace, location, actor
**Returns**: None
**Description**: ADG edge emitter for state_archived.



## Function: state_deleted

**Parameters**: namespace, method, actor
**Returns**: None
**Description**: ADG edge emitter for state_deleted.



## Function: apply_state_lifecycle_policy

**Parameters**: state_namespace, state_version, lifecycle_context
**Returns**: StateLifecycleRecord
**Description**: Mandatory entrypoint for state lifecycle policy application — P3/L4 spec §3.

    Steps (in order, all mandatory):
      1. classify state by namespace
      2. resolve lifecycle policy
      3. determine retention / expiration / archival requirement
      4. emit lifecycle decision
      5. persist lifecycle metadata

    Args:
        state_namespace: State namespace identifier
        state_version: State version identifier
        lifecycle_context: Context for lifecycle application
        registry: StateLifecycleRegistry to use (uses global if None)

    Returns:
        StateLifecycleRecord — the created and persisted lifecycle record

    Raises:
        StateLifecycleError: If lifecycle policy is required but missing (Gate A)
    



## Function: _classify_namespace

**Parameters**: state_namespace
**Returns**: RetentionClass
**Description**: Classify state namespace to determine retention class.



## Function: _resolve_lifecycle_policy

**Parameters**: state_namespace, retention_class, registry
**Returns**: Any | None
**Description**: Resolve lifecycle policy for namespace.



## Function: _create_default_policy

**Parameters**: policy_id, retention_class, expiration_seconds, archival_seconds, deletion_seconds
**Returns**: Any
**Description**: Create default lifecycle policy.



## Function: _determine_status_transition

**Parameters**: record, policy, current_time
**Returns**: str
**Description**: Determine if status should transition based on policy.



## Function: _emit_lifecycle_decision

**Parameters**: record, context
**Returns**: None
**Description**: Emit lifecycle decision for observability.



## Function: record_lifecycle_transition

**Parameters**: state_namespace, from_status, to_status, reason, trace_id
**Returns**: StateLifecycleRecord
**Description**: Record a lifecycle transition with proper metadata.



## Function: record_state_archival

**Parameters**: state_namespace, archive_location, actor_id, trace_id
**Returns**: StateLifecycleRecord
**Description**: Record state archival with proper metadata.



## Function: record_state_deletion

**Parameters**: state_namespace, deletion_method, actor_id, trace_id
**Returns**: StateLifecycleRecord
**Description**: Record state deletion with proper metadata.



## Function: query_state_lifecycle

**Parameters**: state_namespace, status, policy_id
**Returns**: list[StateLifecycleRecord]
**Description**: Query state lifecycle records.



## Function: apply_simple_lifecycle_policy

**Parameters**: state_namespace, access_type, actor_id
**Returns**: StateLifecycleRecord
**Description**: Convenience wrapper for simple lifecycle policy application.



## Function: create

**Parameters**: cls, state_namespace, state_version, access_type, actor_id, trace_id
**Returns**: StateLifecycleContext


## Function: lifecycle_policy_applied

**Parameters**: namespace, policy_id, status, retention
**Returns**: None
**Description**: ADG edge emitter for lifecycle_policy_applied.



## Function: lifecycle_transition_recorded

**Parameters**: namespace, from_status, to_status, reason
**Returns**: None
**Description**: ADG edge emitter for lifecycle_transition_recorded.



## Function: state_archived

**Parameters**: namespace, location, actor
**Returns**: None
**Description**: ADG edge emitter for state_archived.



## Function: state_deleted

**Parameters**: namespace, method, actor
**Returns**: None
**Description**: ADG edge emitter for state_deleted.



## Usage Examples

### Class Usage

```python
# Using StateLifecycleContext
statelifecyclecontext = StateLifecycleContext()
statelifecyclecontext.create()
```

### Function Usage

```python
# Using lifecycle_policy_applied
result = lifecycle_policy_applied(namespace, policy_id)
```

```python
# Using lifecycle_transition_recorded
result = lifecycle_transition_recorded(namespace, from_status)
```

```python
# Using state_active
result = state_active(namespace, location)
```



---
**Generated**: 2026-03-26T09:39:04.547812
**Type**: api_reference
**Quality**: comprehensive
