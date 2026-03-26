# API Documentation: safety_audit_emitter

**Target Audience**: developers, api_users

# safety_audit_emitter API Documentation

**File**: `safety_audit_emitter.py`
**Classes**: 4
**Functions**: 13

## Classes

- **SafetyContext**
- **DecisionContext**
- **TraceContext**
- **HumanReviewContext**

## Functions

- **safety_audit_emitted** -> None
- **human_review_audited** -> None
- **emit_safety_audit_record** -> SafetyAuditRecord
- **emit_human_review_audit** -> HumanReviewAuditRecord
- **query_safety_audits** -> list[SafetyAuditRecord]
- **emit_guardrail_audit** -> SafetyAuditRecord
- **emit_safety_plane_validation_audit** -> SafetyAuditRecord
- **create** -> SafetyContext
- **create** -> DecisionContext
- **create** -> TraceContext
- **create** -> HumanReviewContext
- **safety_audit_emitted** -> None
- **human_review_audited** -> None


## Class: SafetyContext

**Description**: Context for safety audit emission.

### Methods

#### create
**Parameters**: cls, policy_hash, policy_version, decision_type, reason
**Returns**: SafetyContext



## Class: DecisionContext

**Description**: Context for decision outcome and evaluation.

### Methods

#### create
**Parameters**: cls, decision_outcome, evaluated_input, evaluated_output, actor_id, action_class
**Returns**: DecisionContext



## Class: TraceContext

**Description**: Context for trace linkage.

### Methods

#### create
**Parameters**: cls, run_id, trace_id, governed_action_id
**Returns**: TraceContext



## Class: HumanReviewContext

**Description**: Context for human review audit extension.

### Methods

#### create
**Parameters**: cls, reviewer_id, reviewer_outcome, override_flag, override_reason
**Returns**: HumanReviewContext



## Function: safety_audit_emitted

**Parameters**: audit_id, run_id, trace_id, decision_type, outcome, policy_hash, actor_id, action_class
**Returns**: None
**Description**: ADG edge emitter for safety_audit_emitted.



## Function: human_review_audited

**Parameters**: audit_id, reviewer_id, outcome, override
**Returns**: None
**Description**: ADG edge emitter for human_review_audited.



## Function: emit_safety_audit_record

**Parameters**: safety_context, decision_context, trace_context
**Returns**: SafetyAuditRecord
**Description**: Mandatory entrypoint for safety audit emission — P2/L5 spec §3.

    Steps (in order, all mandatory):
      1. attach policy hash
      2. attach decision outcome
      3. attach reason hash
      4. attach actor and action class
      5. persist audit record

    Args:
        safety_context: SafetyContext with policy hash, version, decision type, reason
        decision_context: DecisionContext with outcome and evaluation data
        trace_context: TraceContext with run_id, trace_id, governed_action_id
        registry: SafetyAuditRegistry to use (uses global if None)

    Returns:
        SafetyAuditRecord for the emitted audit

    Raises:
        SafetyAuditMissingError: If required context is missing (Gate A)
    



## Function: emit_human_review_audit

**Parameters**: base_audit, human_review_context
**Returns**: HumanReviewAuditRecord
**Description**: Emit human review audit record (Gate D).



## Function: query_safety_audits

**Parameters**: run_id, trace_id, audit_id
**Returns**: list[SafetyAuditRecord]
**Description**: Query safety audit records (Gate E).



## Function: emit_guardrail_audit

**Parameters**: run_id, trace_id, policy_hash, decision_outcome, evaluated_input, evaluated_output, reason, actor_id, action_class
**Returns**: SafetyAuditRecord
**Description**: Convenience wrapper for guardrail decisions.



## Function: emit_safety_plane_validation_audit

**Parameters**: run_id, trace_id, policy_hash, decision_outcome, evaluated_input, reason, actor_id
**Returns**: SafetyAuditRecord
**Description**: Convenience wrapper for safety plane validations.



## Function: create

**Parameters**: cls, policy_hash, policy_version, decision_type, reason
**Returns**: SafetyContext


## Function: create

**Parameters**: cls, decision_outcome, evaluated_input, evaluated_output, actor_id, action_class
**Returns**: DecisionContext


## Function: create

**Parameters**: cls, run_id, trace_id, governed_action_id
**Returns**: TraceContext


## Function: create

**Parameters**: cls, reviewer_id, reviewer_outcome, override_flag, override_reason
**Returns**: HumanReviewContext


## Function: safety_audit_emitted

**Parameters**: audit_id, run_id, trace_id, decision_type, outcome, policy_hash, actor_id, action_class
**Returns**: None
**Description**: ADG edge emitter for safety_audit_emitted.



## Function: human_review_audited

**Parameters**: audit_id, reviewer_id, outcome, override
**Returns**: None
**Description**: ADG edge emitter for human_review_audited.



## Usage Examples

### Class Usage

```python
# Using SafetyContext
safetycontext = SafetyContext()
safetycontext.create()
```

```python
# Using DecisionContext
decisioncontext = DecisionContext()
decisioncontext.create()
```

```python
# Using TraceContext
tracecontext = TraceContext()
tracecontext.create()
```

### Function Usage

```python
# Using safety_audit_emitted
result = safety_audit_emitted(audit_id, run_id)
```

```python
# Using human_review_audited
result = human_review_audited(audit_id, reviewer_id)
```

```python
# Using emit_safety_audit_record
result = emit_safety_audit_record(safety_context, decision_context)
```



---
**Generated**: 2026-03-26T09:39:04.725683
**Type**: api_reference
**Quality**: comprehensive
