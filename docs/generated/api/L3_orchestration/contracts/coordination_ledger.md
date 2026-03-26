# API Documentation: coordination_ledger

**Target Audience**: developers, api_users

# coordination_ledger API Documentation

**File**: `coordination_ledger.py`
**Classes**: 8
**Functions**: 13

## Classes

- **WorkflowStatus** (inherits from str, Enum)
- **TaskStatus** (inherits from str, Enum)
- **TaskRecord**
- **OwnershipTransition**
- **CoordinationLedger**
- **MissingCoordinationLedger** (inherits from RuntimeError)
- **InvalidOwnershipTransition** (inherits from ValueError)
- **InvalidStageTransition** (inherits from ValueError)

## Functions

- **_hash_task_ids** -> str
- **get_coordination_ledger** -> CoordinationLedger | None
- **initialise_coordination_ledger** -> CoordinationLedger
- **update_coordination_ledger** -> CoordinationLedger
- **complete_coordination_ledger** -> CoordinationLedger
- **reset_coordination_ledgers** -> None
- **transition** -> None
- **tasks_by_status** -> list[TaskRecord]
- **queued_tasks** -> list[TaskRecord]
- **in_progress_tasks** -> list[TaskRecord]
- **completed_tasks** -> list[TaskRecord]
- **ownership_history** -> list[OwnershipTransition]
- **to_dict** -> dict[str, Any]


## Class: WorkflowStatus

**Description**: Top-level status of an entire run workflow.

**Inherits from**: str, Enum



## Class: TaskStatus

**Description**: Lifecycle status of a single task within a run.

**Inherits from**: str, Enum



## Class: TaskRecord

**Description**: Explicit task state entry in the CoordinationLedger.

### Methods

#### transition
**Parameters**: self, new_status
**Returns**: None



## Class: OwnershipTransition

**Description**: Immutable record of one agent ownership change.



## Class: CoordinationLedger

**Description**: Run-scoped coordination state ledger.

    Carries the 11 fields required by the P1/L3 spec plus mutable
    task and transition history.  Immutability is enforced at the
    field level — use update_coordination_ledger() to create new
    state versions; never mutate fields directly.
    

### Methods

#### tasks_by_status
**Parameters**: self, status
**Returns**: list[TaskRecord]

#### queued_tasks
**Parameters**: self
**Returns**: list[TaskRecord]

#### in_progress_tasks
**Parameters**: self
**Returns**: list[TaskRecord]

#### completed_tasks
**Parameters**: self
**Returns**: list[TaskRecord]

#### ownership_history
**Parameters**: self
**Returns**: list[OwnershipTransition]

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: MissingCoordinationLedger

**Description**: Raised when update_coordination_ledger() is called without an existing ledger.

**Inherits from**: RuntimeError



## Class: InvalidOwnershipTransition

**Description**: Raised when the caller is not the current owner.

**Inherits from**: ValueError



## Class: InvalidStageTransition

**Description**: Raised when stage transition metadata is missing.

**Inherits from**: ValueError



## Function: _hash_task_ids

**Parameters**: tasks, statuses
**Returns**: str


## Function: get_coordination_ledger

**Parameters**: run_id
**Returns**: CoordinationLedger | None
**Description**: Return the CoordinationLedger for run_id, or None if not initialised.



## Function: initialise_coordination_ledger

**Parameters**: run_id, root_trace_id, owner_agent_id, policy_hash, initial_stage
**Returns**: CoordinationLedger
**Description**: Create and register a new CoordinationLedger for a run.

    Emits ``observes_runtime_state`` ADG edge.
    



## Function: update_coordination_ledger

**Parameters**: run_id, owner_agent_id, stage_transition, task_update, orchestration_context
**Returns**: CoordinationLedger
**Description**: Mandatory entrypoint for all coordination state mutations.

    Steps enforced:
        1. validate run_id (ledger must exist)
        2. validate current owner
        3. validate stage transition metadata
        4. update ledger fields
        5. emit trace linkage (agent_executes_agent, observes_runtime_state)
        6. persist new state_version

    Args:
        run_id:               Run identifier. Ledger must already be initialised.
        owner_agent_id:       Agent claiming or updating ownership.
        stage_transition:     Dict with keys: previous_stage, new_stage,
                              handoff_reason, new_owner (optional).
        task_update:          Dict with task_id, status, description (optional).
        orchestration_context: Context object for trace/policy binding.

    Returns:
        Updated CoordinationLedger.

    Raises:
        MissingCoordinationLedger:   ledger not found for run_id.
        InvalidOwnershipTransition:  caller not current owner and no new_owner given.
        InvalidStageTransition:      stage_transition missing required keys.
    



## Function: complete_coordination_ledger

**Parameters**: run_id, final_status
**Returns**: CoordinationLedger
**Description**: Mark a run's CoordinationLedger as complete.

    Emits ``snapshots_state`` ADG edge for completed runs.
    



## Function: reset_coordination_ledgers

**Returns**: None
**Description**: Reset all ledgers (for testing).



## Function: transition

**Parameters**: self, new_status
**Returns**: None


## Function: tasks_by_status

**Parameters**: self, status
**Returns**: list[TaskRecord]


## Function: queued_tasks

**Parameters**: self
**Returns**: list[TaskRecord]


## Function: in_progress_tasks

**Parameters**: self
**Returns**: list[TaskRecord]


## Function: completed_tasks

**Parameters**: self
**Returns**: list[TaskRecord]


## Function: ownership_history

**Parameters**: self
**Returns**: list[OwnershipTransition]


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using WorkflowStatus
workflowstatus = WorkflowStatus()
```

```python
# Using TaskStatus
taskstatus = TaskStatus()
```

```python
# Using TaskRecord
taskrecord = TaskRecord()
taskrecord.transition()
```

### Function Usage

```python
# Using _hash_task_ids
result = _hash_task_ids(tasks, statuses)
```

```python
# Using get_coordination_ledger
result = get_coordination_ledger(run_id)
```

```python
# Using initialise_coordination_ledger
result = initialise_coordination_ledger(run_id, root_trace_id)
```



---
**Generated**: 2026-03-26T09:39:04.096280
**Type**: api_reference
**Quality**: comprehensive
