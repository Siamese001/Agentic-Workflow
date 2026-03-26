# API Documentation: human_escalation

**Target Audience**: developers, api_users

# human_escalation API Documentation

**File**: `human_escalation.py`
**Classes**: 5
**Functions**: 21

## Classes

- **EscalationTriggerType** (inherits from Enum)
- **ReviewerOutcome** (inherits from Enum)
- **HumanEscalationError** (inherits from Exception)
- **HumanEscalationRecord**
- **HumanEscalationRegistry**

## Functions

- **get_human_escalation_registry** -> HumanEscalationRegistry
- **reset_human_escalation_registry** -> None
- **create** -> HumanEscalationRecord
- **has_policy_designated_escalation** -> bool
- **has_reviewer_queue_assignment** -> bool
- **has_reviewer_outcome** -> bool
- **is_blocking_automated_completion** -> bool
- **has_explicit_override** -> bool
- **__init__** -> None
- **get_instance** -> HumanEscalationRegistry
- **persist_record** -> None
- **update_reviewer_outcome** -> HumanEscalationRecord
- **query_by_escalation_id** -> HumanEscalationRecord | None
- **query_by_run_id** -> list[HumanEscalationRecord]
- **query_by_trace_id** -> list[HumanEscalationRecord]
- **query_by_queue_id** -> list[HumanEscalationRecord]
- **query_by_reviewer_id** -> list[HumanEscalationRecord]
- **query_by_outcome** -> list[HumanEscalationRecord]
- **get_record_count** -> int
- **verify_policy_designated_escalation** -> bool
- **verify_reviewer_outcome_present** -> bool


## Class: EscalationTriggerType

**Description**: Type of escalation trigger.

**Inherits from**: Enum



## Class: ReviewerOutcome

**Description**: Human reviewer outcome.

**Inherits from**: Enum



## Class: HumanEscalationError

**Description**: Raised when policy-designated human-gated action occurs without escalation record (Gate A).

**Inherits from**: Exception



## Class: HumanEscalationRecord

**Description**: Immutable human escalation record for safety governance (11 required fields).

### Methods

#### create
**Parameters**: cls, escalation_id, run_id, trace_id, policy_hash, action_class, escalation_reason, escalation_trigger_type, reviewer_queue_id, reviewer_id, reviewer_outcome, override_flag, final_decision
**Returns**: HumanEscalationRecord
**Description**: Factory to create HumanEscalationRecord with computed fields.

#### has_policy_designated_escalation
**Parameters**: self
**Returns**: bool
**Description**: Check if record has policy-designated escalation (Gate A).

#### has_reviewer_queue_assignment
**Parameters**: self
**Returns**: bool
**Description**: Check if escalation has reviewer queue assignment (Gate B).

#### has_reviewer_outcome
**Parameters**: self
**Returns**: bool
**Description**: Check if escalation has reviewer outcome (Gate C).

#### is_blocking_automated_completion
**Parameters**: self
**Returns**: bool
**Description**: Check if escalation blocks automated completion (Gate D).

#### has_explicit_override
**Parameters**: self
**Returns**: bool
**Description**: Check if override has explicit flag and reason hash (Gate E).



## Class: HumanEscalationRegistry

**Description**: Thread-safe registry for human escalation records and outcomes.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: HumanEscalationRegistry
**Description**: Singleton accessor.

#### persist_record
**Parameters**: self, record
**Returns**: None
**Description**: Persist a human escalation record.

#### update_reviewer_outcome
**Parameters**: self, escalation_id, reviewer_id, reviewer_outcome, final_decision, override_flag
**Returns**: HumanEscalationRecord
**Description**: Update reviewer outcome for an escalation.

#### query_by_escalation_id
**Parameters**: self, escalation_id
**Returns**: HumanEscalationRecord | None
**Description**: Query human escalation record by escalation_id.

#### query_by_run_id
**Parameters**: self, run_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by run_id.

#### query_by_trace_id
**Parameters**: self, trace_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by trace_id.

#### query_by_queue_id
**Parameters**: self, reviewer_queue_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by reviewer queue.

#### query_by_reviewer_id
**Parameters**: self, reviewer_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by reviewer.

#### query_by_outcome
**Parameters**: self, reviewer_outcome
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by reviewer outcome.

#### get_record_count
**Parameters**: self, outcome
**Returns**: int
**Description**: Get count of human escalation records, optionally filtered by outcome.

#### verify_policy_designated_escalation
**Parameters**: self, escalation_id
**Returns**: bool
**Description**: Verify escalation has policy designation (Gate A).

#### verify_reviewer_outcome_present
**Parameters**: self, escalation_id
**Returns**: bool
**Description**: Verify reviewer outcome is present (Gate C).



## Function: get_human_escalation_registry

**Returns**: HumanEscalationRegistry
**Description**: Get the singleton HumanEscalationRegistry instance.



## Function: reset_human_escalation_registry

**Returns**: None
**Description**: Reset the singleton HumanEscalationRegistry (for testing).



## Function: create

**Parameters**: cls, escalation_id, run_id, trace_id, policy_hash, action_class, escalation_reason, escalation_trigger_type, reviewer_queue_id, reviewer_id, reviewer_outcome, override_flag, final_decision
**Returns**: HumanEscalationRecord
**Description**: Factory to create HumanEscalationRecord with computed fields.



## Function: has_policy_designated_escalation

**Parameters**: self
**Returns**: bool
**Description**: Check if record has policy-designated escalation (Gate A).



## Function: has_reviewer_queue_assignment

**Parameters**: self
**Returns**: bool
**Description**: Check if escalation has reviewer queue assignment (Gate B).



## Function: has_reviewer_outcome

**Parameters**: self
**Returns**: bool
**Description**: Check if escalation has reviewer outcome (Gate C).



## Function: is_blocking_automated_completion

**Parameters**: self
**Returns**: bool
**Description**: Check if escalation blocks automated completion (Gate D).



## Function: has_explicit_override

**Parameters**: self
**Returns**: bool
**Description**: Check if override has explicit flag and reason hash (Gate E).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: HumanEscalationRegistry
**Description**: Singleton accessor.



## Function: persist_record

**Parameters**: self, record
**Returns**: None
**Description**: Persist a human escalation record.



## Function: update_reviewer_outcome

**Parameters**: self, escalation_id, reviewer_id, reviewer_outcome, final_decision, override_flag
**Returns**: HumanEscalationRecord
**Description**: Update reviewer outcome for an escalation.



## Function: query_by_escalation_id

**Parameters**: self, escalation_id
**Returns**: HumanEscalationRecord | None
**Description**: Query human escalation record by escalation_id.



## Function: query_by_run_id

**Parameters**: self, run_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by run_id.



## Function: query_by_trace_id

**Parameters**: self, trace_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by trace_id.



## Function: query_by_queue_id

**Parameters**: self, reviewer_queue_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by reviewer queue.



## Function: query_by_reviewer_id

**Parameters**: self, reviewer_id
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by reviewer.



## Function: query_by_outcome

**Parameters**: self, reviewer_outcome
**Returns**: list[HumanEscalationRecord]
**Description**: Query human escalation records by reviewer outcome.



## Function: get_record_count

**Parameters**: self, outcome
**Returns**: int
**Description**: Get count of human escalation records, optionally filtered by outcome.



## Function: verify_policy_designated_escalation

**Parameters**: self, escalation_id
**Returns**: bool
**Description**: Verify escalation has policy designation (Gate A).



## Function: verify_reviewer_outcome_present

**Parameters**: self, escalation_id
**Returns**: bool
**Description**: Verify reviewer outcome is present (Gate C).



## Usage Examples

### Class Usage

```python
# Using EscalationTriggerType
escalationtriggertype = EscalationTriggerType()
```

```python
# Using ReviewerOutcome
revieweroutcome = ReviewerOutcome()
```

```python
# Using HumanEscalationError
humanescalationerror = HumanEscalationError()
```

### Function Usage

```python
# Using get_human_escalation_registry
result = get_human_escalation_registry()
```

```python
# Using reset_human_escalation_registry
result = reset_human_escalation_registry()
```

```python
# Using create
result = create(cls, escalation_id)
```



---
**Generated**: 2026-03-26T09:39:04.990547
**Type**: api_reference
**Quality**: comprehensive
