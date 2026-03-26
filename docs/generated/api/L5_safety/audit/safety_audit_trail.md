# API Documentation: safety_audit_trail

**Target Audience**: developers, api_users

# safety_audit_trail API Documentation

**File**: `safety_audit_trail.py`
**Classes**: 3
**Functions**: 14

## Classes

- **AuditEventKind** (inherits from str, Enum)
- **SafetyAuditEvent**
- **SafetyAuditTrail**

## Functions

- **get_safety_audit_trail** -> SafetyAuditTrail
- **reset_safety_audit_trail** -> None
- **to_jsonl** -> str
- **__init__** -> None
- **_next_id** -> str
- **_record** -> SafetyAuditEvent
- **record_guardrail_check** -> SafetyAuditEvent
- **record_policy_enforcement** -> SafetyAuditEvent
- **record_tool_gate** -> SafetyAuditEvent
- **record_hitl_decision** -> SafetyAuditEvent
- **flush** -> int
- **all_records** -> list[SafetyAuditEvent]
- **violations** -> list[SafetyAuditEvent]
- **count** -> int


## Class: AuditEventKind

**Description**: Classification of a safety audit event.

**Inherits from**: str, Enum



## Class: SafetyAuditEvent

**Description**: Single safety audit event record.

### Methods

#### to_jsonl
**Parameters**: self
**Returns**: str



## Class: SafetyAuditTrail

**Description**: Immutable append-only audit trail for all L5 safety events.

    Usage::

        trail = SafetyAuditTrail()
        trail.record_guardrail_check(
            module="airlock_guardrail",
            operation="write_file",
            verdict="allow",
            policy_hash="abc123",
            trace_id=trace_id,
            allowed=True,
        )
        trail.flush()
    

### Methods

#### __init__
**Parameters**: self, trail_path
**Returns**: None

#### _next_id
**Parameters**: self
**Returns**: str

#### _record
**Parameters**: self, event
**Returns**: SafetyAuditEvent

#### record_guardrail_check
**Parameters**: self, module, operation, verdict, policy_hash, trace_id, allowed, reason, metadata
**Returns**: SafetyAuditEvent

#### record_policy_enforcement
**Parameters**: self, module, action, verdict, policy_hash, trace_id, allowed, reason, metadata
**Returns**: SafetyAuditEvent

#### record_tool_gate
**Parameters**: self, module, tool_name, risk_level, policy_hash, trace_id, allowed, sandboxed, metadata
**Returns**: SafetyAuditEvent

#### record_hitl_decision
**Parameters**: self, module, decision, trace_id, policy_hash, metadata
**Returns**: SafetyAuditEvent

#### flush
**Parameters**: self
**Returns**: int
**Description**: Write all buffered records to the JSONL trail file.

        Returns count of records written.
        

#### all_records
**Parameters**: self
**Returns**: list[SafetyAuditEvent]

#### violations
**Parameters**: self
**Returns**: list[SafetyAuditEvent]

#### count
**Parameters**: self
**Returns**: int



## Function: get_safety_audit_trail

**Parameters**: path
**Returns**: SafetyAuditTrail


## Function: reset_safety_audit_trail

**Returns**: None


## Function: to_jsonl

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, trail_path
**Returns**: None


## Function: _next_id

**Parameters**: self
**Returns**: str


## Function: _record

**Parameters**: self, event
**Returns**: SafetyAuditEvent


## Function: record_guardrail_check

**Parameters**: self, module, operation, verdict, policy_hash, trace_id, allowed, reason, metadata
**Returns**: SafetyAuditEvent


## Function: record_policy_enforcement

**Parameters**: self, module, action, verdict, policy_hash, trace_id, allowed, reason, metadata
**Returns**: SafetyAuditEvent


## Function: record_tool_gate

**Parameters**: self, module, tool_name, risk_level, policy_hash, trace_id, allowed, sandboxed, metadata
**Returns**: SafetyAuditEvent


## Function: record_hitl_decision

**Parameters**: self, module, decision, trace_id, policy_hash, metadata
**Returns**: SafetyAuditEvent


## Function: flush

**Parameters**: self
**Returns**: int
**Description**: Write all buffered records to the JSONL trail file.

        Returns count of records written.
        



## Function: all_records

**Parameters**: self
**Returns**: list[SafetyAuditEvent]


## Function: violations

**Parameters**: self
**Returns**: list[SafetyAuditEvent]


## Function: count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using AuditEventKind
auditeventkind = AuditEventKind()
```

```python
# Using SafetyAuditEvent
safetyauditevent = SafetyAuditEvent()
safetyauditevent.to_jsonl()
```

```python
# Using SafetyAuditTrail
safetyaudittrail = SafetyAuditTrail()
safetyaudittrail.record_guardrail_check()
safetyaudittrail.record_policy_enforcement()
```

### Function Usage

```python
# Using get_safety_audit_trail
result = get_safety_audit_trail(path)
```

```python
# Using reset_safety_audit_trail
result = reset_safety_audit_trail()
```

```python
# Using to_jsonl
result = to_jsonl()
```



---
**Generated**: 2026-03-26T09:39:04.731915
**Type**: api_reference
**Quality**: comprehensive
