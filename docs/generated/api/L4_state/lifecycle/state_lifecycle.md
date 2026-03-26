# API Documentation: state_lifecycle

**Target Audience**: developers, api_users

# state_lifecycle API Documentation

**File**: `state_lifecycle.py`
**Classes**: 6
**Functions**: 26

## Classes

- **LifecycleStatus** (inherits from Enum)
- **RetentionClass** (inherits from Enum)
- **StateLifecycleError** (inherits from Exception)
- **StateLifecycleRecord**
- **LifecyclePolicy**
- **StateLifecycleRegistry**

## Functions

- **get_state_lifecycle_registry** -> StateLifecycleRegistry
- **reset_state_lifecycle_registry** -> None
- **create** -> StateLifecycleRecord
- **has_lifecycle_policy** -> bool
- **is_active** -> bool
- **is_expired** -> bool
- **has_lifecycle_transition** -> bool
- **is_stale_growth** -> bool
- **has_destructive_cleanup_approval** -> bool
- **create** -> LifecyclePolicy
- **should_expire** -> bool
- **should_archive** -> bool
- **should_delete** -> bool
- **__init__** -> None
- **get_instance** -> StateLifecycleRegistry
- **persist_record** -> None
- **register_policy** -> None
- **update_access_time** -> None
- **update_mutation_time** -> None
- **query_by_namespace** -> StateLifecycleRecord | None
- **query_by_status** -> list[StateLifecycleRecord]
- **query_by_policy** -> list[StateLifecycleRecord]
- **get_policy** -> LifecyclePolicy | None
- **get_record_count** -> int
- **verify_namespace_has_policy** -> bool
- **verify_expired_not_active** -> bool


## Class: LifecycleStatus

**Description**: Status of state lifecycle operations.

**Inherits from**: Enum



## Class: RetentionClass

**Description**: Retention classification for state objects.

**Inherits from**: Enum



## Class: StateLifecycleError

**Description**: Raised when state namespace exists without lifecycle policy (Gate A).

**Inherits from**: Exception



## Class: StateLifecycleRecord

**Description**: Immutable state lifecycle record for operational governance (10 required fields).

### Methods

#### create
**Parameters**: cls, state_namespace, lifecycle_policy_id, retention_class, expiration_rule, archival_rule, deletion_rule, created_at_tick, last_accessed_tick, last_mutated_tick, lifecycle_status
**Returns**: StateLifecycleRecord
**Description**: Factory to create StateLifecycleRecord with computed fields.

#### has_lifecycle_policy
**Parameters**: self
**Returns**: bool
**Description**: Check if record has lifecycle policy (Gate A).

#### is_active
**Parameters**: self
**Returns**: bool
**Description**: Check if state is in active status.

#### is_expired
**Parameters**: self
**Returns**: bool
**Description**: Check if state is expired (Gate B).

#### has_lifecycle_transition
**Parameters**: self
**Returns**: bool
**Description**: Check if lifecycle transition is recorded (Gate C).

#### is_stale_growth
**Parameters**: self
**Returns**: bool
**Description**: Check if stale state growth is occurring (Gate D).

#### has_destructive_cleanup_approval
**Parameters**: self
**Returns**: bool
**Description**: Check if destructive cleanup has policy and trace approval (Gate E).



## Class: LifecyclePolicy

**Description**: Explicit lifecycle policy for state objects.

### Methods

#### create
**Parameters**: cls, policy_id, retention_class, expiration_duration_seconds, archival_duration_seconds, deletion_duration_seconds, requires_approval_for_deletion, trace_linkage_required, destructive_action_classification
**Returns**: LifecyclePolicy

#### should_expire
**Parameters**: self, created_at_tick, current_tick
**Returns**: bool
**Description**: Check if state should expire based on policy.

#### should_archive
**Parameters**: self, created_at_tick, current_tick
**Returns**: bool
**Description**: Check if state should be archived based on policy.

#### should_delete
**Parameters**: self, created_at_tick, current_tick
**Returns**: bool
**Description**: Check if state should be deleted based on policy.



## Class: StateLifecycleRegistry

**Description**: Thread-safe registry for state lifecycle records and policies.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: StateLifecycleRegistry
**Description**: Singleton accessor.

#### persist_record
**Parameters**: self, record
**Returns**: None
**Description**: Persist a state lifecycle record.

#### register_policy
**Parameters**: self, policy
**Returns**: None
**Description**: Register a lifecycle policy.

#### update_access_time
**Parameters**: self, state_namespace
**Returns**: None
**Description**: Update last accessed time for a state namespace.

#### update_mutation_time
**Parameters**: self, state_namespace
**Returns**: None
**Description**: Update last mutated time for a state namespace.

#### query_by_namespace
**Parameters**: self, state_namespace
**Returns**: StateLifecycleRecord | None
**Description**: Query state lifecycle record by namespace.

#### query_by_status
**Parameters**: self, status
**Returns**: list[StateLifecycleRecord]
**Description**: Query state lifecycle records by status.

#### query_by_policy
**Parameters**: self, policy_id
**Returns**: list[StateLifecycleRecord]
**Description**: Query state lifecycle records by policy.

#### get_policy
**Parameters**: self, policy_id
**Returns**: LifecyclePolicy | None
**Description**: Get lifecycle policy by ID.

#### get_record_count
**Parameters**: self, status
**Returns**: int
**Description**: Get count of state lifecycle records, optionally filtered by status.

#### verify_namespace_has_policy
**Parameters**: self, state_namespace
**Returns**: bool
**Description**: Verify state namespace has lifecycle policy (Gate A).

#### verify_expired_not_active
**Parameters**: self, state_namespace
**Returns**: bool
**Description**: Verify expired state is not active (Gate B).



## Function: get_state_lifecycle_registry

**Returns**: StateLifecycleRegistry
**Description**: Get the singleton StateLifecycleRegistry instance.



## Function: reset_state_lifecycle_registry

**Returns**: None
**Description**: Reset the singleton StateLifecycleRegistry (for testing).



## Function: create

**Parameters**: cls, state_namespace, lifecycle_policy_id, retention_class, expiration_rule, archival_rule, deletion_rule, created_at_tick, last_accessed_tick, last_mutated_tick, lifecycle_status
**Returns**: StateLifecycleRecord
**Description**: Factory to create StateLifecycleRecord with computed fields.



## Function: has_lifecycle_policy

**Parameters**: self
**Returns**: bool
**Description**: Check if record has lifecycle policy (Gate A).



## Function: is_active

**Parameters**: self
**Returns**: bool
**Description**: Check if state is in active status.



## Function: is_expired

**Parameters**: self
**Returns**: bool
**Description**: Check if state is expired (Gate B).



## Function: has_lifecycle_transition

**Parameters**: self
**Returns**: bool
**Description**: Check if lifecycle transition is recorded (Gate C).



## Function: is_stale_growth

**Parameters**: self
**Returns**: bool
**Description**: Check if stale state growth is occurring (Gate D).



## Function: has_destructive_cleanup_approval

**Parameters**: self
**Returns**: bool
**Description**: Check if destructive cleanup has policy and trace approval (Gate E).



## Function: create

**Parameters**: cls, policy_id, retention_class, expiration_duration_seconds, archival_duration_seconds, deletion_duration_seconds, requires_approval_for_deletion, trace_linkage_required, destructive_action_classification
**Returns**: LifecyclePolicy


## Function: should_expire

**Parameters**: self, created_at_tick, current_tick
**Returns**: bool
**Description**: Check if state should expire based on policy.



## Function: should_archive

**Parameters**: self, created_at_tick, current_tick
**Returns**: bool
**Description**: Check if state should be archived based on policy.



## Function: should_delete

**Parameters**: self, created_at_tick, current_tick
**Returns**: bool
**Description**: Check if state should be deleted based on policy.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: StateLifecycleRegistry
**Description**: Singleton accessor.



## Function: persist_record

**Parameters**: self, record
**Returns**: None
**Description**: Persist a state lifecycle record.



## Function: register_policy

**Parameters**: self, policy
**Returns**: None
**Description**: Register a lifecycle policy.



## Function: update_access_time

**Parameters**: self, state_namespace
**Returns**: None
**Description**: Update last accessed time for a state namespace.



## Function: update_mutation_time

**Parameters**: self, state_namespace
**Returns**: None
**Description**: Update last mutated time for a state namespace.



## Function: query_by_namespace

**Parameters**: self, state_namespace
**Returns**: StateLifecycleRecord | None
**Description**: Query state lifecycle record by namespace.



## Function: query_by_status

**Parameters**: self, status
**Returns**: list[StateLifecycleRecord]
**Description**: Query state lifecycle records by status.



## Function: query_by_policy

**Parameters**: self, policy_id
**Returns**: list[StateLifecycleRecord]
**Description**: Query state lifecycle records by policy.



## Function: get_policy

**Parameters**: self, policy_id
**Returns**: LifecyclePolicy | None
**Description**: Get lifecycle policy by ID.



## Function: get_record_count

**Parameters**: self, status
**Returns**: int
**Description**: Get count of state lifecycle records, optionally filtered by status.



## Function: verify_namespace_has_policy

**Parameters**: self, state_namespace
**Returns**: bool
**Description**: Verify state namespace has lifecycle policy (Gate A).



## Function: verify_expired_not_active

**Parameters**: self, state_namespace
**Returns**: bool
**Description**: Verify expired state is not active (Gate B).



## Usage Examples

### Class Usage

```python
# Using LifecycleStatus
lifecyclestatus = LifecycleStatus()
```

```python
# Using RetentionClass
retentionclass = RetentionClass()
```

```python
# Using StateLifecycleError
statelifecycleerror = StateLifecycleError()
```

### Function Usage

```python
# Using get_state_lifecycle_registry
result = get_state_lifecycle_registry()
```

```python
# Using reset_state_lifecycle_registry
result = reset_state_lifecycle_registry()
```

```python
# Using create
result = create(cls, state_namespace)
```



---
**Generated**: 2026-03-26T09:39:04.552181
**Type**: api_reference
**Quality**: comprehensive
