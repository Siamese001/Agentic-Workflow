# API Documentation: orchestration_context

**Target Audience**: developers, api_users

# orchestration_context API Documentation

**File**: `orchestration_context.py`
**Classes**: 1
**Functions**: 4

## Classes

- **OrchestrationContext**

## Functions

- **create** -> OrchestrationContext
- **advance** -> OrchestrationContext
- **_emit_agent_executes_agent** -> None
- **to_dict** -> dict[str, Any]


## Class: OrchestrationContext

**Description**: Immutable run-scoped orchestration context carried across every handoff.

    Every agent-to-agent handoff MUST pass this object explicitly.
    Reconstruction from ambient globals is forbidden.

    ADG signals emitted on creation:
        ``agent_executes_agent``  (via _emit_agent_executes_agent helper)
    

### Methods

#### create
**Parameters**: cls, run_id, parent_agent_id, workflow_stage, policy_hash, parent_trace_id, current_work_item_id, state_version, routing_decision_id, metadata
**Returns**: OrchestrationContext
**Description**: Factory: create a context with deterministic routing_decision_id.

#### advance
**Parameters**: self, next_agent_id, next_stage, next_work_item_id
**Returns**: OrchestrationContext
**Description**: Create a child context for the next handoff leg.

        Preserves run_id, policy_hash, parent_trace_id.
        Increments state_version.
        

#### _emit_agent_executes_agent
**Parameters**: self, child_agent_id
**Returns**: None
**Description**: Emit ADG agent_executes_agent signal for graph visibility.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: create

**Parameters**: cls, run_id, parent_agent_id, workflow_stage, policy_hash, parent_trace_id, current_work_item_id, state_version, routing_decision_id, metadata
**Returns**: OrchestrationContext
**Description**: Factory: create a context with deterministic routing_decision_id.



## Function: advance

**Parameters**: self, next_agent_id, next_stage, next_work_item_id
**Returns**: OrchestrationContext
**Description**: Create a child context for the next handoff leg.

        Preserves run_id, policy_hash, parent_trace_id.
        Increments state_version.
        



## Function: _emit_agent_executes_agent

**Parameters**: self, child_agent_id
**Returns**: None
**Description**: Emit ADG agent_executes_agent signal for graph visibility.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using OrchestrationContext
orchestrationcontext = OrchestrationContext()
orchestrationcontext.create()
orchestrationcontext.advance()
```

### Function Usage

```python
# Using create
result = create(cls, run_id)
```

```python
# Using advance
result = advance(next_agent_id, next_stage)
```

```python
# Using _emit_agent_executes_agent
result = _emit_agent_executes_agent(child_agent_id)
```



---
**Generated**: 2026-03-26T09:39:04.098933
**Type**: api_reference
**Quality**: comprehensive
