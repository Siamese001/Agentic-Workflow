# API Documentation: state_transition_registry

**Target Audience**: developers, api_users

# state_transition_registry API Documentation

**File**: `state_transition_registry.py`
**Classes**: 12
**Functions**: 19

## Classes

- **StateVersionMissingError** (inherits from LookupError)
- **StateSnapshotMissingError** (inherits from LookupError)
- **StateConflictError** (inherits from RuntimeError)
- **StateNamespaceError** (inherits from ValueError)
- **UnversionedStateError** (inherits from RuntimeError)
- **SnapshotLineageError** (inherits from RuntimeError)
- **SnapshotPolicy** (inherits from str, Enum)
- **StateTransitionRecord**
- **StateVersionedRead**
- **StateVersionRegistry**
- **StateContext**
- **ActorContext**

## Functions

- **get_state_version_registry** -> StateVersionRegistry
- **reset_state_version_registry** -> None
- **create** -> StateTransitionRecord
- **create** -> StateVersionedRead
- **__init__** -> None
- **validate_namespace** -> None
- **get_version** -> int
- **load_previous_version** -> int
- **assign_new_version** -> int
- **versioned_read** -> StateVersionedRead
- **write_versioned** -> None
- **detect_conflict** -> bool
- **persist_transition** -> None
- **get_transitions** -> list[StateTransitionRecord]
- **record_snapshot** -> None
- **verify_snapshot_lineage** -> bool
- **should_snapshot** -> bool
- **create** -> StateContext
- **create** -> ActorContext


## Class: StateVersionMissingError

**Description**: Raised when a previous version is required but missing (Gate A).

**Inherits from**: LookupError



## Class: StateSnapshotMissingError

**Description**: Raised when a snapshot is required but missing (Gate B).

**Inherits from**: LookupError



## Class: StateConflictError

**Description**: Raised when concurrent writes conflict (Gate D).

**Inherits from**: RuntimeError



## Class: StateNamespaceError

**Description**: Raised when namespace validation fails (Gate A).

**Inherits from**: ValueError



## Class: UnversionedStateError

**Description**: Raised when a read returns raw state without version (Gate C).

**Inherits from**: RuntimeError



## Class: SnapshotLineageError

**Description**: Raised when a snapshot exists without transition lineage (Gate E).

**Inherits from**: RuntimeError



## Class: SnapshotPolicy

**Description**: When a snapshot is required for a state transition.

**Inherits from**: str, Enum



## Class: StateTransitionRecord

**Description**: Immutable record of a versioned state transition.

    Spec §2 fields (10 required):
        state_transition_id, run_id, trace_id, state_namespace,
        previous_version, new_version, mutation_hash,
        actor_id, cause_hash, snapshot_required_flag
    

### Methods

#### create
**Parameters**: cls
**Returns**: StateTransitionRecord



## Class: StateVersionedRead

**Description**: Result of a versioned state read.

    Spec §5: every state read must return versioned state.
    

### Methods

#### create
**Parameters**: cls
**Returns**: StateVersionedRead



## Class: StateVersionRegistry

**Description**: Thread-safe registry for versioned state with conflict detection.

    Maintains:
    - Versions per namespace/key
    - Transition history
    - Conflict detection
    - Snapshot lineage
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### validate_namespace
**Parameters**: self, state_namespace
**Returns**: None
**Description**: Validate namespace format (Gate A step 1).

#### get_version
**Parameters**: self, state_namespace, key
**Returns**: int
**Description**: Return current version for namespace/key (0 if never written).

#### load_previous_version
**Parameters**: self, state_namespace, key
**Returns**: int
**Description**: Load previous version, raising if missing (Gate A step 2).

#### assign_new_version
**Parameters**: self, state_namespace, key
**Returns**: int
**Description**: Assign and return new version (Gate A step 4).

#### versioned_read
**Parameters**: self, state_namespace, key, run_id, trace_id, default
**Returns**: StateVersionedRead
**Description**: Read state with version binding (spec §5).

#### write_versioned
**Parameters**: self, state_namespace, key, value, new_version
**Returns**: None
**Description**: Write value with assigned version (internal use).

#### detect_conflict
**Parameters**: self, state_namespace, key, expected_version
**Returns**: bool
**Description**: Detect lost update or stale write (Gate D).

#### persist_transition
**Parameters**: self, transition
**Returns**: None
**Description**: Persist a state transition (Gate A step 5).

#### get_transitions
**Parameters**: self, run_id, state_namespace
**Returns**: list[StateTransitionRecord]
**Description**: Query transition history.

#### record_snapshot
**Parameters**: self, snapshot_id, metadata
**Returns**: None
**Description**: Record snapshot metadata for lineage tracking.

#### verify_snapshot_lineage
**Parameters**: self, snapshot_id
**Returns**: bool
**Description**: Verify snapshot has transition lineage (Gate E).

#### should_snapshot
**Parameters**: self, transition, policy, run_completed, irreversible_mutation, stage_completion, policy_critical
**Returns**: bool
**Description**: Determine if snapshot is required (Gate A step 6).



## Class: StateContext

**Description**: Context for a state transition request.

### Methods

#### create
**Parameters**: cls, state_namespace, key, run_id, trace_id, policy_hash
**Returns**: StateContext



## Class: ActorContext

**Description**: Context for the actor performing a state transition.

### Methods

#### create
**Parameters**: cls, actor_id, cause_hash
**Returns**: ActorContext



## Function: get_state_version_registry

**Returns**: StateVersionRegistry
**Description**: Return the process-level StateVersionRegistry singleton.



## Function: reset_state_version_registry

**Returns**: None
**Description**: Reset global registry (for testing).



## Function: create

**Parameters**: cls
**Returns**: StateTransitionRecord


## Function: create

**Parameters**: cls
**Returns**: StateVersionedRead


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: validate_namespace

**Parameters**: self, state_namespace
**Returns**: None
**Description**: Validate namespace format (Gate A step 1).



## Function: get_version

**Parameters**: self, state_namespace, key
**Returns**: int
**Description**: Return current version for namespace/key (0 if never written).



## Function: load_previous_version

**Parameters**: self, state_namespace, key
**Returns**: int
**Description**: Load previous version, raising if missing (Gate A step 2).



## Function: assign_new_version

**Parameters**: self, state_namespace, key
**Returns**: int
**Description**: Assign and return new version (Gate A step 4).



## Function: versioned_read

**Parameters**: self, state_namespace, key, run_id, trace_id, default
**Returns**: StateVersionedRead
**Description**: Read state with version binding (spec §5).



## Function: write_versioned

**Parameters**: self, state_namespace, key, value, new_version
**Returns**: None
**Description**: Write value with assigned version (internal use).



## Function: detect_conflict

**Parameters**: self, state_namespace, key, expected_version
**Returns**: bool
**Description**: Detect lost update or stale write (Gate D).



## Function: persist_transition

**Parameters**: self, transition
**Returns**: None
**Description**: Persist a state transition (Gate A step 5).



## Function: get_transitions

**Parameters**: self, run_id, state_namespace
**Returns**: list[StateTransitionRecord]
**Description**: Query transition history.



## Function: record_snapshot

**Parameters**: self, snapshot_id, metadata
**Returns**: None
**Description**: Record snapshot metadata for lineage tracking.



## Function: verify_snapshot_lineage

**Parameters**: self, snapshot_id
**Returns**: bool
**Description**: Verify snapshot has transition lineage (Gate E).



## Function: should_snapshot

**Parameters**: self, transition, policy, run_completed, irreversible_mutation, stage_completion, policy_critical
**Returns**: bool
**Description**: Determine if snapshot is required (Gate A step 6).



## Function: create

**Parameters**: cls, state_namespace, key, run_id, trace_id, policy_hash
**Returns**: StateContext


## Function: create

**Parameters**: cls, actor_id, cause_hash
**Returns**: ActorContext


## Usage Examples

### Class Usage

```python
# Using StateVersionMissingError
stateversionmissingerror = StateVersionMissingError()
```

```python
# Using StateSnapshotMissingError
statesnapshotmissingerror = StateSnapshotMissingError()
```

```python
# Using StateConflictError
stateconflicterror = StateConflictError()
```

### Function Usage

```python
# Using get_state_version_registry
result = get_state_version_registry()
```

```python
# Using reset_state_version_registry
result = reset_state_version_registry()
```

```python
# Using create
result = create(cls)
```



---
**Generated**: 2026-03-26T09:39:04.689443
**Type**: api_reference
**Quality**: comprehensive
