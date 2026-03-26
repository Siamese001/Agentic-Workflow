# API Documentation: run_scoped_state_authority

**Target Audience**: developers, api_users

# run_scoped_state_authority API Documentation

**File**: `run_scoped_state_authority.py`
**Classes**: 5
**Functions**: 23

## Classes

- **StateSnapshot**
- **WorkContract**
- **FrozenStateError** (inherits from RuntimeError)
- **RunScopedStateAuthority**
- **frozen_section**

## Functions

- **get_state_authority** -> RunScopedStateAuthority
- **release_state_authority** -> None
- **active_run_ids** -> list[str]
- **capture** -> StateSnapshot
- **stamp** -> WorkContract
- **__init__** -> None
- **run_id** -> str
- **is_frozen** -> bool
- **_trace_id** -> str
- **stamp_work_contract** -> WorkContract
- **write** -> None
- **read** -> Any
- **delete** -> None
- **keys** -> list[str]
- **snapshot** -> StateSnapshot
- **freeze** -> None
- **unfreeze** -> None
- **frozen_critical_section** -> RunScopedStateAuthority.frozen_section
- **work_contract** -> WorkContract | None
- **snapshot_history** -> list[StateSnapshot]
- **__init__** -> None
- **__enter__** -> RunScopedStateAuthority.frozen_section
- **__exit__** -> bool


## Class: StateSnapshot

**Description**: Immutable point-in-time snapshot of the run-scoped state.

### Methods

#### capture
**Parameters**: cls, run_id, trace_id, state, frozen
**Returns**: StateSnapshot



## Class: WorkContract

**Description**: Immutable work contract stamped at run start.

### Methods

#### stamp
**Parameters**: cls, run_id, trace_id, task_description
**Returns**: WorkContract



## Class: FrozenStateError

**Description**: Raised when a write is attempted on a frozen state.

**Inherits from**: RuntimeError



## Class: RunScopedStateAuthority

**Description**: Single authoritative state ledger for one execution run.

    All L4 state reads and writes must route through this authority.
    Provides freezing (critical section), snapshots, and a work contract
    anchoring the run identity.

    Usage::

        auth = RunScopedStateAuthority(run_id="run-abc")
        auth.stamp_work_contract("Summarise campaign brief")

        auth.write("context.prompt", prompt_text)
        value = auth.read("context.prompt")

        with auth.frozen_section():
            # no writes permitted inside
            result = read_only_operation()

        snap = auth.snapshot()
    

### Methods

#### __init__
**Parameters**: self, run_id
**Returns**: None

#### run_id
**Parameters**: self
**Returns**: str

#### is_frozen
**Parameters**: self
**Returns**: bool

#### _trace_id
**Parameters**: self
**Returns**: str

#### stamp_work_contract
**Parameters**: self, task_description
**Returns**: WorkContract
**Description**: Stamp an immutable work contract anchoring this run's identity.

        Emits ``stamps_work_contract`` ADG edge.
        

#### write
**Parameters**: self, key, value
**Returns**: None
**Description**: Write a value under ``key``.

        P2/L4: Routes through commit_versioned_state_transition() for mandatory
        versioning, conflict detection, and snapshot policy.
        Raises :class:`FrozenStateError` if the authority is currently frozen.
        Emits writes_through and state_transition_committed ADG edges.
        

#### read
**Parameters**: self, key, default
**Returns**: Any
**Description**: Read a value by ``key`` (returns ``default`` if absent).

        P2/L4: Returns versioned state when state_namespace is provided.
        

#### delete
**Parameters**: self, key
**Returns**: None
**Description**: Remove ``key`` from state.

#### keys
**Parameters**: self
**Returns**: list[str]

#### snapshot
**Parameters**: self
**Returns**: StateSnapshot
**Description**: Capture an immutable snapshot of the current state.

        Emits ``snapshots_state`` ADG edge.
        

#### freeze
**Parameters**: self
**Returns**: None
**Description**: Freeze state — all writes blocked until ``unfreeze()``.

        Emits ``freezes_context`` ADG edge.
        

#### unfreeze
**Parameters**: self
**Returns**: None
**Description**: Unfreeze state — writes permitted again.

        Emits ``unfreezes_context`` ADG edge.
        

#### frozen_critical_section
**Parameters**: self
**Returns**: RunScopedStateAuthority.frozen_section
**Description**: Return a context manager that freezes state for a critical section.

#### work_contract
**Parameters**: self
**Returns**: WorkContract | None

#### snapshot_history
**Parameters**: self
**Returns**: list[StateSnapshot]



## Class: frozen_section

**Description**: Context manager: freeze state for the duration of the block.

### Methods

#### __init__
**Parameters**: self, authority
**Returns**: None

#### __enter__
**Parameters**: self
**Returns**: RunScopedStateAuthority.frozen_section

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: bool



## Function: get_state_authority

**Parameters**: run_id
**Returns**: RunScopedStateAuthority
**Description**: Get or create a :class:`RunScopedStateAuthority` for ``run_id``.



## Function: release_state_authority

**Parameters**: run_id
**Returns**: None
**Description**: Release the authority for ``run_id`` (call at run end).



## Function: active_run_ids

**Returns**: list[str]


## Function: capture

**Parameters**: cls, run_id, trace_id, state, frozen
**Returns**: StateSnapshot


## Function: stamp

**Parameters**: cls, run_id, trace_id, task_description
**Returns**: WorkContract


## Function: __init__

**Parameters**: self, run_id
**Returns**: None


## Function: run_id

**Parameters**: self
**Returns**: str


## Function: is_frozen

**Parameters**: self
**Returns**: bool


## Function: _trace_id

**Parameters**: self
**Returns**: str


## Function: stamp_work_contract

**Parameters**: self, task_description
**Returns**: WorkContract
**Description**: Stamp an immutable work contract anchoring this run's identity.

        Emits ``stamps_work_contract`` ADG edge.
        



## Function: write

**Parameters**: self, key, value
**Returns**: None
**Description**: Write a value under ``key``.

        P2/L4: Routes through commit_versioned_state_transition() for mandatory
        versioning, conflict detection, and snapshot policy.
        Raises :class:`FrozenStateError` if the authority is currently frozen.
        Emits writes_through and state_transition_committed ADG edges.
        



## Function: read

**Parameters**: self, key, default
**Returns**: Any
**Description**: Read a value by ``key`` (returns ``default`` if absent).

        P2/L4: Returns versioned state when state_namespace is provided.
        



## Function: delete

**Parameters**: self, key
**Returns**: None
**Description**: Remove ``key`` from state.



## Function: keys

**Parameters**: self
**Returns**: list[str]


## Function: snapshot

**Parameters**: self
**Returns**: StateSnapshot
**Description**: Capture an immutable snapshot of the current state.

        Emits ``snapshots_state`` ADG edge.
        



## Function: freeze

**Parameters**: self
**Returns**: None
**Description**: Freeze state — all writes blocked until ``unfreeze()``.

        Emits ``freezes_context`` ADG edge.
        



## Function: unfreeze

**Parameters**: self
**Returns**: None
**Description**: Unfreeze state — writes permitted again.

        Emits ``unfreezes_context`` ADG edge.
        



## Function: frozen_critical_section

**Parameters**: self
**Returns**: RunScopedStateAuthority.frozen_section
**Description**: Return a context manager that freezes state for a critical section.



## Function: work_contract

**Parameters**: self
**Returns**: WorkContract | None


## Function: snapshot_history

**Parameters**: self
**Returns**: list[StateSnapshot]


## Function: __init__

**Parameters**: self, authority
**Returns**: None


## Function: __enter__

**Parameters**: self
**Returns**: RunScopedStateAuthority.frozen_section


## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using StateSnapshot
statesnapshot = StateSnapshot()
statesnapshot.capture()
```

```python
# Using WorkContract
workcontract = WorkContract()
workcontract.stamp()
```

```python
# Using FrozenStateError
frozenstateerror = FrozenStateError()
```

### Function Usage

```python
# Using get_state_authority
result = get_state_authority(run_id)
```

```python
# Using release_state_authority
result = release_state_authority(run_id)
```

```python
# Using active_run_ids
result = active_run_ids()
```



---
**Generated**: 2026-03-26T09:39:04.457336
**Type**: api_reference
**Quality**: comprehensive
