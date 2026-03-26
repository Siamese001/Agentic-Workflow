# API Documentation: visualization_updater

**Target Audience**: developers, api_users

# visualization_updater API Documentation

**File**: `visualization_updater.py`
**Classes**: 2
**Functions**: 16

## Classes

- **WorkflowVisualizationContext**
- **TraceContext**

## Functions

- **workflow_visualization_emitted** -> None
- **stage_transition_recorded** -> None
- **owner_transition_recorded** -> None
- **workflow_completed_recorded** -> None
- **update_workflow_visualization** -> WorkflowVisualizationRecord
- **record_stage_transition** -> WorkflowVisualizationRecord
- **record_owner_transition** -> WorkflowVisualizationRecord
- **record_workflow_completion** -> WorkflowVisualizationRecord
- **query_workflow_visualization** -> list[WorkflowVisualizationRecord]
- **update_simple_workflow** -> WorkflowVisualizationRecord
- **create** -> WorkflowVisualizationContext
- **create** -> TraceContext
- **workflow_visualization_emitted** -> None
- **stage_transition_recorded** -> None
- **owner_transition_recorded** -> None
- **workflow_completed_recorded** -> None


## Class: WorkflowVisualizationContext

**Description**: Context for workflow visualization updating.

### Methods

#### create
**Parameters**: cls, run_id, root_trace_id, workflow_id, current_stage, completed_stages, pending_stages, current_owner_agent_id, previous_owner_agent_id
**Returns**: WorkflowVisualizationContext



## Class: TraceContext

**Description**: Context for trace binding.

### Methods

#### create
**Parameters**: cls, trace_id, parent_trace_id, trace_timestamp
**Returns**: TraceContext



## Function: workflow_visualization_emitted

**Parameters**: record_id, run_id, workflow_id, stage, status
**Returns**: None
**Description**: ADG edge emitter for workflow_visualization_emitted.



## Function: stage_transition_recorded

**Parameters**: record_id, from_stage, to_stage, reason
**Returns**: None
**Description**: ADG edge emitter for stage_transition_recorded.



## Function: owner_transition_recorded

**Parameters**: record_id, current_owner, previous_owner
**Returns**: None
**Description**: ADG edge emitter for owner_transition_recorded.



## Function: workflow_completed_recorded

**Parameters**: record_id, final_stage, status
**Returns**: None
**Description**: ADG edge emitter for workflow_completed_recorded.



## Function: update_workflow_visualization

**Parameters**: run_id, workflow_stage, owner_transition, workflow_status, trace_context
**Returns**: WorkflowVisualizationRecord
**Description**: Mandatory entrypoint for workflow visualization updating — P3/L3 spec §3.

    Steps (in order, all mandatory):
      1. record current stage
      2. record owner transition
      3. update pending/completed stage sets
      4. bind to trace
      5. persist workflow visualization state

    Args:
        run_id: Run identifier
        workflow_stage: Current workflow stage
        owner_transition: Tuple of (current_owner, previous_owner)
        workflow_status: Current workflow status
        trace_context: Trace binding context
        completed_stages: Set of completed stages
        pending_stages: Set of pending stages
        stage_transition_reason: Reason for stage transition
        registry: WorkflowVisualizationRegistry to use (uses global if None)

    Returns:
        WorkflowVisualizationRecord — the created and persisted visualization record

    Raises:
        WorkflowVisualizationError: If visualization update is required but fails (Gate A)
    



## Function: record_stage_transition

**Parameters**: run_id, from_stage, to_stage, owner_transition, transition_reason, trace_context
**Returns**: WorkflowVisualizationRecord
**Description**: Record a stage transition with proper metadata.



## Function: record_owner_transition

**Parameters**: run_id, current_stage, owner_transition, trace_context
**Returns**: WorkflowVisualizationRecord
**Description**: Record an owner transition with proper metadata.



## Function: record_workflow_completion

**Parameters**: run_id, final_stage, owner_transition, workflow_status, trace_context
**Returns**: WorkflowVisualizationRecord
**Description**: Record workflow completion with final state.



## Function: query_workflow_visualization

**Parameters**: run_id, workflow_id, record_id, status
**Returns**: list[WorkflowVisualizationRecord]
**Description**: Query workflow visualization records.



## Function: update_simple_workflow

**Parameters**: run_id, current_stage, current_owner, workflow_status, trace_id
**Returns**: WorkflowVisualizationRecord
**Description**: Convenience wrapper for simple workflow visualization updating.



## Function: create

**Parameters**: cls, run_id, root_trace_id, workflow_id, current_stage, completed_stages, pending_stages, current_owner_agent_id, previous_owner_agent_id
**Returns**: WorkflowVisualizationContext


## Function: create

**Parameters**: cls, trace_id, parent_trace_id, trace_timestamp
**Returns**: TraceContext


## Function: workflow_visualization_emitted

**Parameters**: record_id, run_id, workflow_id, stage, status
**Returns**: None
**Description**: ADG edge emitter for workflow_visualization_emitted.



## Function: stage_transition_recorded

**Parameters**: record_id, from_stage, to_stage, reason
**Returns**: None
**Description**: ADG edge emitter for stage_transition_recorded.



## Function: owner_transition_recorded

**Parameters**: record_id, current_owner, previous_owner
**Returns**: None
**Description**: ADG edge emitter for owner_transition_recorded.



## Function: workflow_completed_recorded

**Parameters**: record_id, final_stage, status
**Returns**: None
**Description**: ADG edge emitter for workflow_completed_recorded.



## Usage Examples

### Class Usage

```python
# Using WorkflowVisualizationContext
workflowvisualizationcontext = WorkflowVisualizationContext()
workflowvisualizationcontext.create()
```

```python
# Using TraceContext
tracecontext = TraceContext()
tracecontext.create()
```

### Function Usage

```python
# Using workflow_visualization_emitted
result = workflow_visualization_emitted(record_id, run_id)
```

```python
# Using stage_transition_recorded
result = stage_transition_recorded(record_id, from_stage)
```

```python
# Using owner_transition_recorded
result = owner_transition_recorded(record_id, current_owner)
```



---
**Generated**: 2026-03-26T09:39:04.434954
**Type**: api_reference
**Quality**: comprehensive
