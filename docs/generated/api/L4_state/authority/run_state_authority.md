# API Documentation: run_state_authority

**Target Audience**: developers, api_users

# run_state_authority API Documentation

**File**: `run_state_authority.py`
**Classes**: 4
**Functions**: 23

## Classes

- **StateMutationRecord**
- **StateVersion**
- **StateSnapshot**
- **RunStateAuthority** (inherits from WriteGovernorMixin)

## Functions

- **get_run_state_authority** -> RunStateAuthority
- **reset_run_state_authority** -> None
- **create** -> StateMutationRecord
- **build** -> StateVersion
- **build** -> StateSnapshot
- **__init__** -> None
- **read** -> tuple[Any, int]
- **observe** -> None
- **observe_runtime_state** -> None
- **snapshot_runtime** -> StateSnapshot
- **snapshot_state** -> StateSnapshot
- **mutation_lineage_record** -> StateMutationRecord | None
- **commit** -> StateVersion
- **snapshot** -> StateSnapshot
- **get_version** -> int
- **detect_conflict** -> bool
- **ledger** -> list[StateVersion]
- **snapshots** -> list[StateSnapshot]
- **observation_history** -> list[dict[str, Any]]
- **mutation_records** -> list[StateMutationRecord]
- **get_stats** -> dict[str, Any]
- **_backend_read** -> Any
- **run_scope** -> Generator[RunStateAuthority, None, None]


## Class: StateMutationRecord

**Description**: Immutable record of a single governed state mutation (8 required fields).

### Methods

#### create
**Parameters**: cls, run_id, actor_id, previous_state_version, new_state_version, key, value, policy_hash, trace_id, reason_code
**Returns**: StateMutationRecord



## Class: StateVersion

**Description**: Versioned state value for conflict detection.

### Methods

#### build
**Parameters**: cls, key, value, version, run_id
**Returns**: StateVersion



## Class: StateSnapshot

**Description**: Point-in-time snapshot of all state managed by a RunStateAuthority.

### Methods

#### build
**Parameters**: cls, run_id, label, state, version_vectors
**Returns**: StateSnapshot



## Class: RunStateAuthority

**Description**: Unified runtime state authority — single ledger facade for L4 state.

    Thread-safe. All reads and writes are versioned and logged.
    Snapshots are append-only; state is mutable per commit.
    

**Inherits from**: WriteGovernorMixin

### Methods

#### __init__
**Parameters**: self, run_id, backend
**Returns**: None
**Description**: 
        Args:
            run_id: The run this authority is scoped to (optional for process-level).
            backend: Optional existing state store to delegate reads to on cache miss.
        

#### read
**Parameters**: self, key, default, state_namespace
**Returns**: tuple[Any, int]
**Description**: Read a state value and its version.

        P2/L4: Returns versioned state through read_versioned_state() when
        state_namespace is provided. Falls back to internal version for
        backward compatibility.

        ADG edges: ``reads_runtime_state``, ``observes_runtime_state``.

        Returns:
            ``(value, version)`` — version is 0 if key has never been written.
        

#### observe
**Parameters**: self, context, stage, actor_id, trace_id
**Returns**: None
**Description**: Emit an explicit observes_runtime_state signal.

        Use at orchestration stage transitions, reasoning context updates,
        mutation commits, rollback/conflict handling, and memory retrievals.
        ADG edge: ``observes_runtime_state``.
        

#### observe_runtime_state
**Parameters**: self, context, stage, actor_id, trace_id
**Returns**: None
**Description**: Emit an observes_runtime_state ADG edge (scanner-visible alias for observe()).

        The method name ``observe_runtime_state`` matches the ADG schema
        ``POLICY_STATE_READ_METHODS`` set, ensuring the static scanner emits
        the ``observes_runtime_state`` edge when this method is called.
        

#### snapshot_runtime
**Parameters**: self, label, run_id
**Returns**: StateSnapshot
**Description**: Capture a snapshot (alias for snapshot()).

#### snapshot_state
**Parameters**: self, label, run_id
**Returns**: StateSnapshot
**Description**: Capture a snapshot and emit snapshots_state ADG edge (scanner-visible).

        The method name ``snapshot_state`` is in ``POLICY_STATE_READ_METHODS`` and
        contains 'snapshot' (without 'runtime'/'health'/'probe'), so the ADG static
        scanner correctly emits the ``snapshots_state`` edge.
        

#### mutation_lineage_record
**Parameters**: self, key, actor_id, policy_hash, trace_id, reason_code
**Returns**: StateMutationRecord | None
**Description**: Return the last StateMutationRecord for ``key``, or None if no commit.

#### commit
**Parameters**: self, key, value, run_id, actor_id, policy_hash, trace_id, reason_code, state_namespace, expected_previous_version
**Returns**: StateVersion
**Description**: Write a state value, incrementing its version.

        P2/L4: Routes through commit_versioned_state_transition() for mandatory
        versioning, conflict detection, and snapshot policy.
        Emits ``writes_through`` and ``state_transition_committed`` ADG edges.
        Returns the new ``StateVersion`` record.
        

#### snapshot
**Parameters**: self, label, run_id
**Returns**: StateSnapshot
**Description**: Capture a point-in-time snapshot of all managed state.

        ADG edge: ``snapshots_state``.
        

#### get_version
**Parameters**: self, key
**Returns**: int
**Description**: Return the current version for ``key`` (0 if never written).

#### detect_conflict
**Parameters**: self, key, expected_version
**Returns**: bool
**Description**: Return True if current version differs from ``expected_version``.

#### ledger
**Parameters**: self
**Returns**: list[StateVersion]
**Description**: Return append-only copy of the commit ledger.

#### snapshots
**Parameters**: self
**Returns**: list[StateSnapshot]
**Description**: Return append-only copy of all snapshots.

#### observation_history
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Return append-only copy of all observations.

#### mutation_records
**Parameters**: self
**Returns**: list[StateMutationRecord]
**Description**: Return append-only copy of all mutation records.

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return statistics for monitoring and CI gate verification.

#### _backend_read
**Parameters**: self, key, default
**Returns**: Any
**Description**: Delegate to backend store on cache miss.

#### run_scope
**Parameters**: self, run_id
**Returns**: Generator[RunStateAuthority, None, None]
**Description**: Return a child RunStateAuthority scoped to a specific run_id.

        The child shares the parent's backend but has its own state ledger.
        On exit, snapshots are promoted back to the parent's snapshot list.
        



## Function: get_run_state_authority

**Returns**: RunStateAuthority
**Description**: Return the process-level RunStateAuthority singleton.



## Function: reset_run_state_authority

**Returns**: None
**Description**: Reset the singleton (for testing).



## Function: create

**Parameters**: cls, run_id, actor_id, previous_state_version, new_state_version, key, value, policy_hash, trace_id, reason_code
**Returns**: StateMutationRecord


## Function: build

**Parameters**: cls, key, value, version, run_id
**Returns**: StateVersion


## Function: build

**Parameters**: cls, run_id, label, state, version_vectors
**Returns**: StateSnapshot


## Function: __init__

**Parameters**: self, run_id, backend
**Returns**: None
**Description**: 
        Args:
            run_id: The run this authority is scoped to (optional for process-level).
            backend: Optional existing state store to delegate reads to on cache miss.
        



## Function: read

**Parameters**: self, key, default, state_namespace
**Returns**: tuple[Any, int]
**Description**: Read a state value and its version.

        P2/L4: Returns versioned state through read_versioned_state() when
        state_namespace is provided. Falls back to internal version for
        backward compatibility.

        ADG edges: ``reads_runtime_state``, ``observes_runtime_state``.

        Returns:
            ``(value, version)`` — version is 0 if key has never been written.
        



## Function: observe

**Parameters**: self, context, stage, actor_id, trace_id
**Returns**: None
**Description**: Emit an explicit observes_runtime_state signal.

        Use at orchestration stage transitions, reasoning context updates,
        mutation commits, rollback/conflict handling, and memory retrievals.
        ADG edge: ``observes_runtime_state``.
        



## Function: observe_runtime_state

**Parameters**: self, context, stage, actor_id, trace_id
**Returns**: None
**Description**: Emit an observes_runtime_state ADG edge (scanner-visible alias for observe()).

        The method name ``observe_runtime_state`` matches the ADG schema
        ``POLICY_STATE_READ_METHODS`` set, ensuring the static scanner emits
        the ``observes_runtime_state`` edge when this method is called.
        



## Function: snapshot_runtime

**Parameters**: self, label, run_id
**Returns**: StateSnapshot
**Description**: Capture a snapshot (alias for snapshot()).



## Function: snapshot_state

**Parameters**: self, label, run_id
**Returns**: StateSnapshot
**Description**: Capture a snapshot and emit snapshots_state ADG edge (scanner-visible).

        The method name ``snapshot_state`` is in ``POLICY_STATE_READ_METHODS`` and
        contains 'snapshot' (without 'runtime'/'health'/'probe'), so the ADG static
        scanner correctly emits the ``snapshots_state`` edge.
        



## Function: mutation_lineage_record

**Parameters**: self, key, actor_id, policy_hash, trace_id, reason_code
**Returns**: StateMutationRecord | None
**Description**: Return the last StateMutationRecord for ``key``, or None if no commit.



## Function: commit

**Parameters**: self, key, value, run_id, actor_id, policy_hash, trace_id, reason_code, state_namespace, expected_previous_version
**Returns**: StateVersion
**Description**: Write a state value, incrementing its version.

        P2/L4: Routes through commit_versioned_state_transition() for mandatory
        versioning, conflict detection, and snapshot policy.
        Emits ``writes_through`` and ``state_transition_committed`` ADG edges.
        Returns the new ``StateVersion`` record.
        



## Function: snapshot

**Parameters**: self, label, run_id
**Returns**: StateSnapshot
**Description**: Capture a point-in-time snapshot of all managed state.

        ADG edge: ``snapshots_state``.
        



## Function: get_version

**Parameters**: self, key
**Returns**: int
**Description**: Return the current version for ``key`` (0 if never written).



## Function: detect_conflict

**Parameters**: self, key, expected_version
**Returns**: bool
**Description**: Return True if current version differs from ``expected_version``.



## Function: ledger

**Parameters**: self
**Returns**: list[StateVersion]
**Description**: Return append-only copy of the commit ledger.



## Function: snapshots

**Parameters**: self
**Returns**: list[StateSnapshot]
**Description**: Return append-only copy of all snapshots.



## Function: observation_history

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Return append-only copy of all observations.



## Function: mutation_records

**Parameters**: self
**Returns**: list[StateMutationRecord]
**Description**: Return append-only copy of all mutation records.



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return statistics for monitoring and CI gate verification.



## Function: _backend_read

**Parameters**: self, key, default
**Returns**: Any
**Description**: Delegate to backend store on cache miss.



## Function: run_scope

**Parameters**: self, run_id
**Returns**: Generator[RunStateAuthority, None, None]
**Description**: Return a child RunStateAuthority scoped to a specific run_id.

        The child shares the parent's backend but has its own state ledger.
        On exit, snapshots are promoted back to the parent's snapshot list.
        



## Usage Examples

### Class Usage

```python
# Using StateMutationRecord
statemutationrecord = StateMutationRecord()
statemutationrecord.create()
```

```python
# Using StateVersion
stateversion = StateVersion()
stateversion.build()
```

```python
# Using StateSnapshot
statesnapshot = StateSnapshot()
statesnapshot.build()
```

### Function Usage

```python
# Using get_run_state_authority
result = get_run_state_authority()
```

```python
# Using reset_run_state_authority
result = reset_run_state_authority()
```

```python
# Using create
result = create(cls, run_id)
```



---
**Generated**: 2026-03-26T09:39:04.464802
**Type**: api_reference
**Quality**: comprehensive
