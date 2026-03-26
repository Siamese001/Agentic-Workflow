# API Documentation: run_scoped_orchestration_ledger

**Target Audience**: developers, api_users

# run_scoped_orchestration_ledger API Documentation

**File**: `run_scoped_orchestration_ledger.py`
**Classes**: 3
**Functions**: 17

## Classes

- **StageStatus** (inherits from str, Enum)
- **StageOwnershipRecord**
- **RunScopedOrchestrationLedger**

## Functions

- **get_orchestration_ledger** -> RunScopedOrchestrationLedger
- **reset_orchestration_ledgers** -> None
- **mark_active** -> None
- **mark_completed** -> None
- **mark_failed** -> None
- **mark_escalated** -> None
- **__init__** -> None
- **record_handoff** -> None
- **record_stage_transition** -> StageOwnershipRecord
- **record_task_ownership** -> None
- **record_escalation** -> None
- **all_handoffs** -> list[OrchestrationHandoffContract]
- **active_stages** -> list[StageOwnershipRecord]
- **pending_stages** -> list[StageOwnershipRecord]
- **completed_stages** -> list[StageOwnershipRecord]
- **task_owner** -> str | None
- **summary** -> dict[str, Any]


## Class: StageStatus

**Description**: Status of a workflow stage.

**Inherits from**: str, Enum



## Class: StageOwnershipRecord

**Description**: Records ownership transition for one workflow stage.

### Methods

#### mark_active
**Parameters**: self
**Returns**: None

#### mark_completed
**Parameters**: self, continuation
**Returns**: None

#### mark_failed
**Parameters**: self
**Returns**: None

#### mark_escalated
**Parameters**: self
**Returns**: None



## Class: RunScopedOrchestrationLedger

**Description**: Single interface for recording all L3 agent handoffs within one run.

    All L3 orchestrators MUST write to this ledger through this interface.
    Direct orchestration state mutation outside this ledger is forbidden.

    Usage::

        ledger = get_orchestration_ledger(run_id="run_abc123")
        ledger.record_handoff(contract)
        ledger.record_stage_transition(
            stage="decomposition",
            owner="DecompositionOrchestrator",
            next_owner="ExecutionOrchestrator",
            handoff_id=contract.handoff_id,
        )
    

### Methods

#### __init__
**Parameters**: self, run_id
**Returns**: None

#### record_handoff
**Parameters**: self, contract
**Returns**: None
**Description**: Record a typed handoff contract in the ledger.

        Emits ``agent_executes_agent`` ADG edge signal.
        

#### record_stage_transition
**Parameters**: self, stage, owner_agent_id, next_owner_agent_id, handoff_id, continuation_signal
**Returns**: StageOwnershipRecord
**Description**: Record a workflow stage ownership transition.

        Hard rule: no workflow stage transition without this record.
        

#### record_task_ownership
**Parameters**: self, work_item_id, owner_agent_id
**Returns**: None
**Description**: Assign task ownership to an agent.

#### record_escalation
**Parameters**: self, stage, agent_id, reason
**Returns**: None
**Description**: Record an escalation event.

#### all_handoffs
**Parameters**: self
**Returns**: list[OrchestrationHandoffContract]
**Description**: Return all recorded handoff contracts.

#### active_stages
**Parameters**: self
**Returns**: list[StageOwnershipRecord]
**Description**: Return all stage records with ACTIVE status.

#### pending_stages
**Parameters**: self
**Returns**: list[StageOwnershipRecord]
**Description**: Return all stage records with PENDING status.

#### completed_stages
**Parameters**: self
**Returns**: list[StageOwnershipRecord]
**Description**: Return all completed stage records.

#### task_owner
**Parameters**: self, work_item_id
**Returns**: str | None
**Description**: Return the current owner agent for a work item.

#### summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return a summary of ledger state.



## Function: get_orchestration_ledger

**Parameters**: run_id
**Returns**: RunScopedOrchestrationLedger
**Description**: Get or create the run-scoped orchestration ledger.



## Function: reset_orchestration_ledgers

**Returns**: None
**Description**: Reset all ledgers (for testing).



## Function: mark_active

**Parameters**: self
**Returns**: None


## Function: mark_completed

**Parameters**: self, continuation
**Returns**: None


## Function: mark_failed

**Parameters**: self
**Returns**: None


## Function: mark_escalated

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, run_id
**Returns**: None


## Function: record_handoff

**Parameters**: self, contract
**Returns**: None
**Description**: Record a typed handoff contract in the ledger.

        Emits ``agent_executes_agent`` ADG edge signal.
        



## Function: record_stage_transition

**Parameters**: self, stage, owner_agent_id, next_owner_agent_id, handoff_id, continuation_signal
**Returns**: StageOwnershipRecord
**Description**: Record a workflow stage ownership transition.

        Hard rule: no workflow stage transition without this record.
        



## Function: record_task_ownership

**Parameters**: self, work_item_id, owner_agent_id
**Returns**: None
**Description**: Assign task ownership to an agent.



## Function: record_escalation

**Parameters**: self, stage, agent_id, reason
**Returns**: None
**Description**: Record an escalation event.



## Function: all_handoffs

**Parameters**: self
**Returns**: list[OrchestrationHandoffContract]
**Description**: Return all recorded handoff contracts.



## Function: active_stages

**Parameters**: self
**Returns**: list[StageOwnershipRecord]
**Description**: Return all stage records with ACTIVE status.



## Function: pending_stages

**Parameters**: self
**Returns**: list[StageOwnershipRecord]
**Description**: Return all stage records with PENDING status.



## Function: completed_stages

**Parameters**: self
**Returns**: list[StageOwnershipRecord]
**Description**: Return all completed stage records.



## Function: task_owner

**Parameters**: self, work_item_id
**Returns**: str | None
**Description**: Return the current owner agent for a work item.



## Function: summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return a summary of ledger state.



## Usage Examples

### Class Usage

```python
# Using StageStatus
stagestatus = StageStatus()
```

```python
# Using StageOwnershipRecord
stageownershiprecord = StageOwnershipRecord()
stageownershiprecord.mark_active()
stageownershiprecord.mark_completed()
```

```python
# Using RunScopedOrchestrationLedger
runscopedorchestrationledger = RunScopedOrchestrationLedger()
runscopedorchestrationledger.record_handoff()
runscopedorchestrationledger.record_stage_transition()
```

### Function Usage

```python
# Using get_orchestration_ledger
result = get_orchestration_ledger(run_id)
```

```python
# Using reset_orchestration_ledgers
result = reset_orchestration_ledgers()
```

```python
# Using mark_active
result = mark_active()
```



---
**Generated**: 2026-03-26T09:39:04.104723
**Type**: api_reference
**Quality**: comprehensive
