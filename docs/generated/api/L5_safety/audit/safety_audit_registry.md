# API Documentation: safety_audit_registry

**Target Audience**: developers, api_users

# safety_audit_registry API Documentation

**File**: `safety_audit_registry.py`
**Classes**: 6
**Functions**: 17

## Classes

- **SafetyAuditMissingError** (inherits from Exception)
- **HumanReviewAuditError** (inherits from Exception)
- **AuditQueryError** (inherits from Exception)
- **SafetyAuditRecord**
- **HumanReviewAuditRecord**
- **SafetyAuditRegistry**

## Functions

- **get_safety_audit_registry** -> SafetyAuditRegistry
- **reset_safety_audit_registry** -> None
- **create** -> SafetyAuditRecord
- **create** -> HumanReviewAuditRecord
- **__init__** -> None
- **get_instance** -> SafetyAuditRegistry
- **persist_audit** -> None
- **persist_human_review** -> None
- **query_by_run_id** -> list[SafetyAuditRecord]
- **query_by_trace_id** -> list[SafetyAuditRecord]
- **query_by_audit_id** -> SafetyAuditRecord | None
- **query_human_review** -> HumanReviewAuditRecord | None
- **get_audit_count** -> int
- **verify_audit_exists** -> bool
- **verify_policy_hash_present** -> bool
- **verify_decision_outcome_present** -> bool
- **verify_human_review_metadata** -> bool


## Class: SafetyAuditMissingError

**Description**: Raised when safety decision occurs without required audit record (Gate A).

**Inherits from**: Exception



## Class: HumanReviewAuditError

**Description**: Raised when human review occurs without reviewer metadata (Gate D).

**Inherits from**: Exception



## Class: AuditQueryError

**Description**: Raised when audit record query fails (Gate E).

**Inherits from**: Exception



## Class: SafetyAuditRecord

**Description**: Immutable audit record for safety-governed actions (12 required fields).

### Methods

#### create
**Parameters**: cls, run_id, trace_id, policy_hash, policy_version, decision_type, decision_outcome, reason, actor_id, action_class, evaluated_input, evaluated_output
**Returns**: SafetyAuditRecord
**Description**: Factory to create SafetyAuditRecord with computed hashes.



## Class: HumanReviewAuditRecord

**Description**: Audit record for human-reviewed safety decisions.

### Methods

#### create
**Parameters**: cls, base_audit, reviewer_id, reviewer_outcome, override_flag, override_reason
**Returns**: HumanReviewAuditRecord
**Description**: Factory to create HumanReviewAuditRecord.



## Class: SafetyAuditRegistry

**Description**: Thread-safe registry for safety audit records and queries.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: SafetyAuditRegistry
**Description**: Singleton accessor.

#### persist_audit
**Parameters**: self, audit
**Returns**: None
**Description**: Persist a safety audit record (Gate A step 5).

#### persist_human_review
**Parameters**: self, review
**Returns**: None
**Description**: Persist a human review audit record.

#### query_by_run_id
**Parameters**: self, run_id
**Returns**: list[SafetyAuditRecord]
**Description**: Query audit records by run_id (Gate E).

#### query_by_trace_id
**Parameters**: self, trace_id
**Returns**: list[SafetyAuditRecord]
**Description**: Query audit records by trace_id (Gate E).

#### query_by_audit_id
**Parameters**: self, audit_id
**Returns**: SafetyAuditRecord | None
**Description**: Query audit record by safety_audit_id.

#### query_human_review
**Parameters**: self, audit_id
**Returns**: HumanReviewAuditRecord | None
**Description**: Query human review audit by base audit_id.

#### get_audit_count
**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of audit records, optionally filtered by run_id.

#### verify_audit_exists
**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify audit record exists (Gate A).

#### verify_policy_hash_present
**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify audit record has policy hash (Gate B).

#### verify_decision_outcome_present
**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify audit record has decision outcome (Gate C).

#### verify_human_review_metadata
**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify human review has reviewer metadata (Gate D).



## Function: get_safety_audit_registry

**Returns**: SafetyAuditRegistry
**Description**: Get the singleton SafetyAuditRegistry instance.



## Function: reset_safety_audit_registry

**Returns**: None
**Description**: Reset the singleton SafetyAuditRegistry (for testing).



## Function: create

**Parameters**: cls, run_id, trace_id, policy_hash, policy_version, decision_type, decision_outcome, reason, actor_id, action_class, evaluated_input, evaluated_output
**Returns**: SafetyAuditRecord
**Description**: Factory to create SafetyAuditRecord with computed hashes.



## Function: create

**Parameters**: cls, base_audit, reviewer_id, reviewer_outcome, override_flag, override_reason
**Returns**: HumanReviewAuditRecord
**Description**: Factory to create HumanReviewAuditRecord.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: SafetyAuditRegistry
**Description**: Singleton accessor.



## Function: persist_audit

**Parameters**: self, audit
**Returns**: None
**Description**: Persist a safety audit record (Gate A step 5).



## Function: persist_human_review

**Parameters**: self, review
**Returns**: None
**Description**: Persist a human review audit record.



## Function: query_by_run_id

**Parameters**: self, run_id
**Returns**: list[SafetyAuditRecord]
**Description**: Query audit records by run_id (Gate E).



## Function: query_by_trace_id

**Parameters**: self, trace_id
**Returns**: list[SafetyAuditRecord]
**Description**: Query audit records by trace_id (Gate E).



## Function: query_by_audit_id

**Parameters**: self, audit_id
**Returns**: SafetyAuditRecord | None
**Description**: Query audit record by safety_audit_id.



## Function: query_human_review

**Parameters**: self, audit_id
**Returns**: HumanReviewAuditRecord | None
**Description**: Query human review audit by base audit_id.



## Function: get_audit_count

**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of audit records, optionally filtered by run_id.



## Function: verify_audit_exists

**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify audit record exists (Gate A).



## Function: verify_policy_hash_present

**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify audit record has policy hash (Gate B).



## Function: verify_decision_outcome_present

**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify audit record has decision outcome (Gate C).



## Function: verify_human_review_metadata

**Parameters**: self, audit_id
**Returns**: bool
**Description**: Verify human review has reviewer metadata (Gate D).



## Usage Examples

### Class Usage

```python
# Using SafetyAuditMissingError
safetyauditmissingerror = SafetyAuditMissingError()
```

```python
# Using HumanReviewAuditError
humanreviewauditerror = HumanReviewAuditError()
```

```python
# Using AuditQueryError
auditqueryerror = AuditQueryError()
```

### Function Usage

```python
# Using get_safety_audit_registry
result = get_safety_audit_registry()
```

```python
# Using reset_safety_audit_registry
result = reset_safety_audit_registry()
```

```python
# Using create
result = create(cls, run_id)
```



---
**Generated**: 2026-03-26T09:39:04.728833
**Type**: api_reference
**Quality**: comprehensive
