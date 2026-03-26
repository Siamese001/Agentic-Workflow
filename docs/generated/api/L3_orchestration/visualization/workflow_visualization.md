# API Documentation: workflow_visualization

**Target Audience**: developers, api_users

# workflow_visualization API Documentation

**File**: `workflow_visualization.py`
**Classes**: 6
**Functions**: 25

## Classes

- **WorkflowStatus** (inherits from Enum)
- **StageTransitionReason** (inherits from Enum)
- **WorkflowVisualizationError** (inherits from Exception)
- **WorkflowVisualizationRecord**
- **WorkflowStageModel**
- **WorkflowVisualizationRegistry**

## Functions

- **get_workflow_visualization_registry** -> WorkflowVisualizationRegistry
- **reset_workflow_visualization_registry** -> None
- **create** -> WorkflowVisualizationRecord
- **has_current_stage** -> bool
- **has_workflow_status** -> bool
- **has_owner_transition** -> bool
- **is_terminal_workflow** -> bool
- **has_blocked_reason** -> bool
- **create** -> WorkflowStageModel
- **is_valid_transition** -> bool
- **is_terminal_stage** -> bool
- **is_retry_stage** -> bool
- **is_escalation_stage** -> bool
- **__init__** -> None
- **get_instance** -> WorkflowVisualizationRegistry
- **persist_record** -> None
- **register_stage_model** -> None
- **query_by_run_id** -> list[WorkflowVisualizationRecord]
- **query_by_workflow_id** -> list[WorkflowVisualizationRecord]
- **query_by_status** -> list[WorkflowVisualizationRecord]
- **query_by_record_id** -> WorkflowVisualizationRecord | None
- **get_stage_model** -> WorkflowStageModel | None
- **get_record_count** -> int
- **verify_record_exists** -> bool
- **verify_current_stage_present** -> bool


## Class: WorkflowStatus

**Description**: Status of workflow operations.

**Inherits from**: Enum



## Class: StageTransitionReason

**Description**: Reason for stage transitions.

**Inherits from**: Enum



## Class: WorkflowVisualizationError

**Description**: Raised when stage transition occurs without workflow visualization update (Gate A).

**Inherits from**: Exception



## Class: WorkflowVisualizationRecord

**Description**: Immutable workflow visualization record for operational telemetry (13 required fields).

### Methods

#### create
**Parameters**: cls, run_id, root_trace_id, workflow_id, current_stage, completed_stages, pending_stages, current_owner_agent_id, previous_owner_agent_id, workflow_status, stage_transition_reason
**Returns**: WorkflowVisualizationRecord
**Description**: Factory to create WorkflowVisualizationRecord with computed fields.

#### has_current_stage
**Parameters**: self
**Returns**: bool
**Description**: Check if record has current_stage (Gate A).

#### has_workflow_status
**Parameters**: self
**Returns**: bool
**Description**: Check if workflow status is present (Gate B).

#### has_owner_transition
**Parameters**: self
**Returns**: bool
**Description**: Check if owner transition is recorded (Gate C).

#### is_terminal_workflow
**Parameters**: self
**Returns**: bool
**Description**: Check if workflow is in terminal state (Gate D).

#### has_blocked_reason
**Parameters**: self
**Returns**: bool
**Description**: Check if blocked workflow has blocked reason (Gate E).



## Class: WorkflowStageModel

**Description**: Explicit stage model for workflow visualization.

### Methods

#### create
**Parameters**: cls, workflow_id, stage_names, allowed_transitions, terminal_stages, retry_stages, escalation_stages
**Returns**: WorkflowStageModel

#### is_valid_transition
**Parameters**: self, from_stage, to_stage
**Returns**: bool
**Description**: Check if transition is allowed.

#### is_terminal_stage
**Parameters**: self, stage
**Returns**: bool
**Description**: Check if stage is terminal.

#### is_retry_stage
**Parameters**: self, stage
**Returns**: bool
**Description**: Check if stage is a retry stage.

#### is_escalation_stage
**Parameters**: self, stage
**Returns**: bool
**Description**: Check if stage is an escalation stage.



## Class: WorkflowVisualizationRegistry

**Description**: Thread-safe registry for workflow visualization records and queries.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: WorkflowVisualizationRegistry
**Description**: Singleton accessor.

#### persist_record
**Parameters**: self, record
**Returns**: None
**Description**: Persist a workflow visualization record.

#### register_stage_model
**Parameters**: self, stage_model
**Returns**: None
**Description**: Register a workflow stage model.

#### query_by_run_id
**Parameters**: self, run_id
**Returns**: list[WorkflowVisualizationRecord]
**Description**: Query workflow visualization records by run_id.

#### query_by_workflow_id
**Parameters**: self, workflow_id
**Returns**: list[WorkflowVisualizationRecord]
**Description**: Query workflow visualization records by workflow_id.

#### query_by_status
**Parameters**: self, status
**Returns**: list[WorkflowVisualizationRecord]
**Description**: Query workflow visualization records by status.

#### query_by_record_id
**Parameters**: self, record_id
**Returns**: WorkflowVisualizationRecord | None
**Description**: Query workflow visualization record by workflow_visualization_id.

#### get_stage_model
**Parameters**: self, workflow_id
**Returns**: WorkflowStageModel | None
**Description**: Get stage model for a workflow.

#### get_record_count
**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of workflow visualization records, optionally filtered by run_id.

#### verify_record_exists
**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify workflow visualization record exists (Gate A).

#### verify_current_stage_present
**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify record has current_stage (Gate A).



## Function: get_workflow_visualization_registry

**Returns**: WorkflowVisualizationRegistry
**Description**: Get the singleton WorkflowVisualizationRegistry instance.



## Function: reset_workflow_visualization_registry

**Returns**: None
**Description**: Reset the singleton WorkflowVisualizationRegistry (for testing).



## Function: create

**Parameters**: cls, run_id, root_trace_id, workflow_id, current_stage, completed_stages, pending_stages, current_owner_agent_id, previous_owner_agent_id, workflow_status, stage_transition_reason
**Returns**: WorkflowVisualizationRecord
**Description**: Factory to create WorkflowVisualizationRecord with computed fields.



## Function: has_current_stage

**Parameters**: self
**Returns**: bool
**Description**: Check if record has current_stage (Gate A).



## Function: has_workflow_status

**Parameters**: self
**Returns**: bool
**Description**: Check if workflow status is present (Gate B).



## Function: has_owner_transition

**Parameters**: self
**Returns**: bool
**Description**: Check if owner transition is recorded (Gate C).



## Function: is_terminal_workflow

**Parameters**: self
**Returns**: bool
**Description**: Check if workflow is in terminal state (Gate D).



## Function: has_blocked_reason

**Parameters**: self
**Returns**: bool
**Description**: Check if blocked workflow has blocked reason (Gate E).



## Function: create

**Parameters**: cls, workflow_id, stage_names, allowed_transitions, terminal_stages, retry_stages, escalation_stages
**Returns**: WorkflowStageModel


## Function: is_valid_transition

**Parameters**: self, from_stage, to_stage
**Returns**: bool
**Description**: Check if transition is allowed.



## Function: is_terminal_stage

**Parameters**: self, stage
**Returns**: bool
**Description**: Check if stage is terminal.



## Function: is_retry_stage

**Parameters**: self, stage
**Returns**: bool
**Description**: Check if stage is a retry stage.



## Function: is_escalation_stage

**Parameters**: self, stage
**Returns**: bool
**Description**: Check if stage is an escalation stage.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: WorkflowVisualizationRegistry
**Description**: Singleton accessor.



## Function: persist_record

**Parameters**: self, record
**Returns**: None
**Description**: Persist a workflow visualization record.



## Function: register_stage_model

**Parameters**: self, stage_model
**Returns**: None
**Description**: Register a workflow stage model.



## Function: query_by_run_id

**Parameters**: self, run_id
**Returns**: list[WorkflowVisualizationRecord]
**Description**: Query workflow visualization records by run_id.



## Function: query_by_workflow_id

**Parameters**: self, workflow_id
**Returns**: list[WorkflowVisualizationRecord]
**Description**: Query workflow visualization records by workflow_id.



## Function: query_by_status

**Parameters**: self, status
**Returns**: list[WorkflowVisualizationRecord]
**Description**: Query workflow visualization records by status.



## Function: query_by_record_id

**Parameters**: self, record_id
**Returns**: WorkflowVisualizationRecord | None
**Description**: Query workflow visualization record by workflow_visualization_id.



## Function: get_stage_model

**Parameters**: self, workflow_id
**Returns**: WorkflowStageModel | None
**Description**: Get stage model for a workflow.



## Function: get_record_count

**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of workflow visualization records, optionally filtered by run_id.



## Function: verify_record_exists

**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify workflow visualization record exists (Gate A).



## Function: verify_current_stage_present

**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify record has current_stage (Gate A).



## Usage Examples

### Class Usage

```python
# Using WorkflowStatus
workflowstatus = WorkflowStatus()
```

```python
# Using StageTransitionReason
stagetransitionreason = StageTransitionReason()
```

```python
# Using WorkflowVisualizationError
workflowvisualizationerror = WorkflowVisualizationError()
```

### Function Usage

```python
# Using get_workflow_visualization_registry
result = get_workflow_visualization_registry()
```

```python
# Using reset_workflow_visualization_registry
result = reset_workflow_visualization_registry()
```

```python
# Using create
result = create(cls, run_id)
```



---
**Generated**: 2026-03-26T09:39:04.437922
**Type**: api_reference
**Quality**: comprehensive
