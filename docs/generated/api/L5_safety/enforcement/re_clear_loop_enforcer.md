# API Documentation: re_clear_loop_enforcer

**Target Audience**: developers, api_users

# re_clear_loop_enforcer API Documentation

**File**: `re_clear_loop_enforcer.py`
**Classes**: 3
**Functions**: 5

## Classes

- **ReClearViolation** (inherits from RuntimeError)
- **ReClearStatus** (inherits from str, Enum)
- **ReClearTicket**

## Functions

- **open_ticket** -> ReClearTicket
- **__post_init__** -> None
- **_assert_mutable** -> None
- **re_evaluate** -> ReClearTicket
- **escalate** -> ReClearTicket


## Class: ReClearViolation

**Description**: Raised when the re-clear loop contract is violated.

**Inherits from**: RuntimeError



## Class: ReClearStatus

**Inherits from**: str, Enum



## Class: ReClearTicket

**Description**: Tracks a single L5 violation through the Path D re-clear lifecycle.

    Spec: L5 Safety Path D — immutable once CLEARED or BLOCKED.
    Fields:
        ticket_id: Stable unique identifier (non-empty).
        constraint_id: The L5 constraint that was violated.
        violation_summary: Human-readable description of the violation.
        status: Current lifecycle status.
        remediation_evidence: Evidence dict populated by re_evaluate().
        escalation_note: Required when status=ESCALATED.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### _assert_mutable
**Parameters**: self
**Returns**: None

#### re_evaluate
**Parameters**: self, constraint_fn, evidence
**Returns**: ReClearTicket
**Description**: Re-evaluate the original constraint after remediation.

        Args:
            constraint_fn: Returns True if the constraint is now satisfied, False if still violated.
            evidence: Optional evidence dict to record with the outcome.

        Returns:
            A new ReClearTicket with updated status (CLEARED or BLOCKED).

        Raises:
            ReClearViolation: If the ticket is already terminal.
        

#### escalate
**Parameters**: self, note
**Returns**: ReClearTicket
**Description**: Escalate a BLOCKED ticket with a mandatory note.

        Only BLOCKED tickets may be escalated.
        Raises ReClearViolation if ticket is not BLOCKED.
        



## Function: open_ticket

**Parameters**: ticket_id, constraint_id, violation_summary
**Returns**: ReClearTicket
**Description**: Open a new Path D re-clear ticket for a detected violation.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: _assert_mutable

**Parameters**: self
**Returns**: None


## Function: re_evaluate

**Parameters**: self, constraint_fn, evidence
**Returns**: ReClearTicket
**Description**: Re-evaluate the original constraint after remediation.

        Args:
            constraint_fn: Returns True if the constraint is now satisfied, False if still violated.
            evidence: Optional evidence dict to record with the outcome.

        Returns:
            A new ReClearTicket with updated status (CLEARED or BLOCKED).

        Raises:
            ReClearViolation: If the ticket is already terminal.
        



## Function: escalate

**Parameters**: self, note
**Returns**: ReClearTicket
**Description**: Escalate a BLOCKED ticket with a mandatory note.

        Only BLOCKED tickets may be escalated.
        Raises ReClearViolation if ticket is not BLOCKED.
        



## Usage Examples

### Class Usage

```python
# Using ReClearViolation
reclearviolation = ReClearViolation()
```

```python
# Using ReClearStatus
reclearstatus = ReClearStatus()
```

```python
# Using ReClearTicket
reclearticket = ReClearTicket()
reclearticket.re_evaluate()
reclearticket.escalate()
```

### Function Usage

```python
# Using open_ticket
result = open_ticket(ticket_id, constraint_id)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _assert_mutable
result = _assert_mutable()
```



---
**Generated**: 2026-03-26T09:39:04.916781
**Type**: api_reference
**Quality**: comprehensive
