# API Documentation: run_scoped_state_ledger

**Target Audience**: developers, api_users

# run_scoped_state_ledger API Documentation

**File**: `run_scoped_state_ledger.py`
**Classes**: 6
**Functions**: 17

## Classes

- **ReadEntry**
- **ObservationEntry**
- **MutationEntry**
- **SnapshotEntry**
- **ConflictEntry**
- **RunScopedStateLedger**

## Functions

- **get_state_ledger** -> RunScopedStateLedger
- **release_state_ledger** -> None
- **active_ledger_run_ids** -> list[str]
- **__init__** -> None
- **run_id** -> str
- **trace_id** -> str
- **record_read** -> ReadEntry
- **record_observation** -> ObservationEntry
- **record_mutation** -> MutationEntry
- **record_snapshot** -> SnapshotEntry
- **record_conflict** -> ConflictEntry
- **reads** -> list[ReadEntry]
- **observations** -> list[ObservationEntry]
- **mutations** -> list[MutationEntry]
- **snapshots** -> list[SnapshotEntry]
- **conflicts** -> list[ConflictEntry]
- **summary** -> dict[str, Any]


## Class: ReadEntry

**Description**: Record of a single state read.



## Class: ObservationEntry

**Description**: Record of an explicit state observation signal.



## Class: MutationEntry

**Description**: Record of a committed state mutation.



## Class: SnapshotEntry

**Description**: Record of a state snapshot.



## Class: ConflictEntry

**Description**: Record of a detected state conflict.



## Class: RunScopedStateLedger

**Description**: Per-run append-only ledger for all state interactions.

    Bind one ledger per run_id. All state reads, observations, mutations,
    snapshots, and conflicts are recorded here for audit and CI gate closure.

    Usage::

        ledger = RunScopedStateLedger(run_id="run-001", trace_id="trace-abc")
        ledger.record_observation("orchestration_stage", stage="plan_start", actor_id="mission_runner")
        ledger.record_mutation("phase", prev_version=0, new_version=1,
                               mutation_hash="abc", actor_id="mission_runner")
        snap = ledger.record_snapshot("run_complete", mutation_count=3)
    

### Methods

#### __init__
**Parameters**: self, run_id, trace_id
**Returns**: None

#### run_id
**Parameters**: self
**Returns**: str

#### trace_id
**Parameters**: self
**Returns**: str

#### record_read
**Parameters**: self, key, state_version
**Returns**: ReadEntry
**Description**: Record a state read and emit reads_runtime_state.

#### record_observation
**Parameters**: self, context, stage, actor_id
**Returns**: ObservationEntry
**Description**: Record an explicit state observation and emit observes_runtime_state.

#### record_mutation
**Parameters**: self, key, previous_state_version, new_state_version, mutation_hash, actor_id, policy_hash, reason_code
**Returns**: MutationEntry
**Description**: Record a committed state mutation.

#### record_snapshot
**Parameters**: self, label, state, mutation_count, final_state_version
**Returns**: SnapshotEntry
**Description**: Record a state snapshot and emit snapshots_state.

#### record_conflict
**Parameters**: self, key, expected_version, actual_version, resolved
**Returns**: ConflictEntry
**Description**: Record a detected version conflict event.

#### reads
**Parameters**: self
**Returns**: list[ReadEntry]

#### observations
**Parameters**: self
**Returns**: list[ObservationEntry]

#### mutations
**Parameters**: self
**Returns**: list[MutationEntry]

#### snapshots
**Parameters**: self
**Returns**: list[SnapshotEntry]

#### conflicts
**Parameters**: self
**Returns**: list[ConflictEntry]

#### summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return ledger summary for CI gate and monitoring.



## Function: get_state_ledger

**Parameters**: run_id, trace_id
**Returns**: RunScopedStateLedger
**Description**: Get or create a RunScopedStateLedger for ``run_id``.



## Function: release_state_ledger

**Parameters**: run_id
**Returns**: None
**Description**: Release the ledger for ``run_id`` after run completion.



## Function: active_ledger_run_ids

**Returns**: list[str]
**Description**: Return all currently active ledger run IDs.



## Function: __init__

**Parameters**: self, run_id, trace_id
**Returns**: None


## Function: run_id

**Parameters**: self
**Returns**: str


## Function: trace_id

**Parameters**: self
**Returns**: str


## Function: record_read

**Parameters**: self, key, state_version
**Returns**: ReadEntry
**Description**: Record a state read and emit reads_runtime_state.



## Function: record_observation

**Parameters**: self, context, stage, actor_id
**Returns**: ObservationEntry
**Description**: Record an explicit state observation and emit observes_runtime_state.



## Function: record_mutation

**Parameters**: self, key, previous_state_version, new_state_version, mutation_hash, actor_id, policy_hash, reason_code
**Returns**: MutationEntry
**Description**: Record a committed state mutation.



## Function: record_snapshot

**Parameters**: self, label, state, mutation_count, final_state_version
**Returns**: SnapshotEntry
**Description**: Record a state snapshot and emit snapshots_state.



## Function: record_conflict

**Parameters**: self, key, expected_version, actual_version, resolved
**Returns**: ConflictEntry
**Description**: Record a detected version conflict event.



## Function: reads

**Parameters**: self
**Returns**: list[ReadEntry]


## Function: observations

**Parameters**: self
**Returns**: list[ObservationEntry]


## Function: mutations

**Parameters**: self
**Returns**: list[MutationEntry]


## Function: snapshots

**Parameters**: self
**Returns**: list[SnapshotEntry]


## Function: conflicts

**Parameters**: self
**Returns**: list[ConflictEntry]


## Function: summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return ledger summary for CI gate and monitoring.



## Usage Examples

### Class Usage

```python
# Using ReadEntry
readentry = ReadEntry()
```

```python
# Using ObservationEntry
observationentry = ObservationEntry()
```

```python
# Using MutationEntry
mutationentry = MutationEntry()
```

### Function Usage

```python
# Using get_state_ledger
result = get_state_ledger(run_id, trace_id)
```

```python
# Using release_state_ledger
result = release_state_ledger(run_id)
```

```python
# Using active_ledger_run_ids
result = active_ledger_run_ids()
```



---
**Generated**: 2026-03-26T09:39:04.461117
**Type**: api_reference
**Quality**: comprehensive
