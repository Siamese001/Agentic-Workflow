# API Documentation: escalation_orchestrator

**Target Audience**: developers, api_users

# escalation_orchestrator API Documentation

**File**: `escalation_orchestrator.py`
**Classes**: 3
**Functions**: 20

## Classes

- **SafetyContext**
- **GovernedAction**
- **TraceContext**

## Functions

- **escalates_to_human** -> None
- **reviewer_outcome_recorded** -> None
- **override_executed** -> None
- **escalation_blocked** -> None
- **escalate_for_human_review** -> HumanEscalationRecord
- **_classify_trigger_type** -> EscalationTriggerType
- **_determine_reviewer_queue** -> str
- **_attach_to_reviewer_queue** -> None
- **_block_automated_completion** -> None
- **_bind_to_trace** -> None
- **record_reviewer_outcome** -> HumanEscalationRecord
- **execute_override** -> HumanEscalationRecord
- **query_human_escalation** -> list[HumanEscalationRecord]
- **escalate_simple_action** -> HumanEscalationRecord
- **create** -> SafetyContext
- **create** -> GovernedAction
- **create** -> TraceContext
- **escalates_to_human** -> None
- **reviewer_outcome_recorded** -> None
- **override_executed** -> None


## Class: SafetyContext

**Description**: Context for safety escalation.

### Methods

#### create
**Parameters**: cls, policy_hash, action_class, requires_human_review, safety_plane_available, risk_level
**Returns**: SafetyContext



## Class: GovernedAction

**Description**: Context for governed action requiring escalation.

### Methods

#### create
**Parameters**: cls, action_name, action_parameters, execution_context, actor_id, target_system
**Returns**: GovernedAction



## Class: TraceContext

**Description**: Context for trace binding.

### Methods

#### create
**Parameters**: cls, trace_id, run_id, parent_trace_id, trace_timestamp
**Returns**: TraceContext



## Function: escalates_to_human

**Parameters**: escalation_id, trigger_type, queue_id
**Returns**: None
**Description**: ADG edge emitter for escalates_to_human.



## Function: reviewer_outcome_recorded

**Parameters**: escalation_id, reviewer_id, outcome
**Returns**: None
**Description**: ADG edge emitter for reviewer_outcome_recorded.



## Function: override_executed

**Parameters**: escalation_id, reviewer_id, reason
**Returns**: None
**Description**: ADG edge emitter for override_executed.



## Function: escalation_blocked

**Parameters**: escalation_id, reason
**Returns**: None
**Description**: ADG edge emitter for escalation_blocked.



## Function: escalate_for_human_review

**Parameters**: safety_context, governed_action, escalation_reason, trace_context
**Returns**: HumanEscalationRecord
**Description**: Mandatory entrypoint for human safety escalation — P3/L5 spec §3.

    Steps (in order, all mandatory):
      1. classify trigger type
      2. bind policy hash
      3. create escalation record
      4. attach to reviewer queue
      5. block automated completion until review outcome
      6. bind final decision back to trace

    Args:
        safety_context: Safety context for escalation
        governed_action: Governed action requiring escalation
        escalation_reason: Reason for escalation
        trace_context: Trace binding context
        registry: HumanEscalationRegistry to use (uses global if None)

    Returns:
        HumanEscalationRecord — the created and persisted escalation record

    Raises:
        HumanEscalationError: If escalation is required but fails (Gate A)
    



## Function: _classify_trigger_type

**Parameters**: safety_context, governed_action, escalation_reason
**Returns**: EscalationTriggerType
**Description**: Classify the escalation trigger type.



## Function: _determine_reviewer_queue

**Parameters**: safety_context, governed_action
**Returns**: str
**Description**: Determine the appropriate reviewer queue.



## Function: _attach_to_reviewer_queue

**Parameters**: record, reviewer_queue_id
**Returns**: None
**Description**: Attach escalation to reviewer queue.



## Function: _block_automated_completion

**Parameters**: record
**Returns**: None
**Description**: Block automated completion until review outcome.



## Function: _bind_to_trace

**Parameters**: record, trace_context
**Returns**: None
**Description**: Bind escalation to trace.



## Function: record_reviewer_outcome

**Parameters**: escalation_id, reviewer_id, reviewer_outcome, final_decision, override_flag
**Returns**: HumanEscalationRecord
**Description**: Record reviewer outcome for an escalation.



## Function: execute_override

**Parameters**: escalation_id, reviewer_id, override_reason
**Returns**: HumanEscalationRecord
**Description**: Execute override for an escalation.



## Function: query_human_escalation

**Parameters**: escalation_id, run_id, trace_id, reviewer_queue_id, reviewer_id, outcome
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records.



## Function: escalate_simple_action

**Parameters**: action_name, escalation_reason, policy_hash, trace_id, run_id, actor_id
**Returns**: HumanEscalationRecord
**Description**: Convenience wrapper for simple action escalation.



## Function: create

**Parameters**: cls, policy_hash, action_class, requires_human_review, safety_plane_available, risk_level
**Returns**: SafetyContext


## Function: create

**Parameters**: cls, action_name, action_parameters, execution_context, actor_id, target_system
**Returns**: GovernedAction


## Function: create

**Parameters**: cls, trace_id, run_id, parent_trace_id, trace_timestamp
**Returns**: TraceContext


## Function: escalates_to_human

**Parameters**: escalation_id, trigger_type, queue_id
**Returns**: None
**Description**: ADG edge emitter for escalates_to_human.



## Function: reviewer_outcome_recorded

**Parameters**: escalation_id, reviewer_id, outcome
**Returns**: None
**Description**: ADG edge emitter for reviewer_outcome_recorded.



## Function: override_executed

**Parameters**: escalation_id, reviewer_id, reason
**Returns**: None
**Description**: ADG edge emitter for override_executed.



## Usage Examples

### Class Usage

```python
# Using SafetyContext
safetycontext = SafetyContext()
safetycontext.create()
```

```python
# Using GovernedAction
governedaction = GovernedAction()
governedaction.create()
```

```python
# Using TraceContext
tracecontext = TraceContext()
tracecontext.create()
```

### Function Usage

```python
# Using escalates_to_human
result = escalates_to_human(escalation_id, trigger_type)
```

```python
# Using reviewer_outcome_recorded
result = reviewer_outcome_recorded(escalation_id, reviewer_id)
```

```python
# Using override_executed
result = override_executed(escalation_id, reviewer_id)
```



---
**Generated**: 2026-03-26T09:39:04.987872
**Type**: api_reference
**Quality**: comprehensive
