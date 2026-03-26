# API Documentation: hitl_escalation_activator

**Target Audience**: developers, api_users

# hitl_escalation_activator API Documentation

**File**: `hitl_escalation_activator.py`
**Classes**: 3
**Functions**: 11

## Classes

- **EscalationPriority** (inherits from str, Enum)
- **EscalationRequest**
- **HITLEscalationActivator**

## Functions

- **get_hitl_escalation_activator** -> HITLEscalationActivator
- **reset_hitl_escalation_activator** -> None
- **resolve** -> None
- **__init__** -> None
- **register_handler** -> None
- **_trace_id** -> str
- **escalate** -> EscalationRequest
- **pending** -> list[EscalationRequest]
- **resolved** -> list[EscalationRequest]
- **requires_human_review** -> bool
- **pending_count** -> int


## Class: EscalationPriority

**Inherits from**: str, Enum



## Class: EscalationRequest

**Description**: Single HITL escalation request.

### Methods

#### resolve
**Parameters**: self, decision
**Returns**: None



## Class: HITLEscalationActivator

**Description**: Activates HITL escalation from enforcement verdicts.

    Usage::

        activator = HITLEscalationActivator()
        activator.register_handler(my_async_review_handler)

        # When PolicyEnforcementPoint returns ESCALATE:
        escalation = activator.escalate(
            agent="ToolSafetyGate",
            module="tool_safety_gate",
            trigger_reason="policy hash missing",
            proposed_action="invoke eval tool",
            priority=EscalationPriority.HIGH,
            policy_hash="",
        )
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register_handler
**Parameters**: self, handler
**Returns**: None
**Description**: Register a review handler (sync). Handler returns decision string or None.

#### _trace_id
**Parameters**: self
**Returns**: str

#### escalate
**Parameters**: self, agent, module, trigger_reason, proposed_action, priority, policy_hash, metadata
**Returns**: EscalationRequest
**Description**: Activate HITL escalation for a given trigger.

        Emits ``hitl_escalation_activation`` + ``reenters_safety`` ADG edges.
        Logs via HITLDecisionLogger.
        

#### pending
**Parameters**: self
**Returns**: list[EscalationRequest]

#### resolved
**Parameters**: self
**Returns**: list[EscalationRequest]

#### requires_human_review
**Parameters**: self, request
**Returns**: bool
**Description**: Check if a request requires human review (ADG: requires_human_review edge).

        All escalations with priority >= HIGH require human review.
        

#### pending_count
**Parameters**: self
**Returns**: int



## Function: get_hitl_escalation_activator

**Returns**: HITLEscalationActivator


## Function: reset_hitl_escalation_activator

**Returns**: None


## Function: resolve

**Parameters**: self, decision
**Returns**: None


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register_handler

**Parameters**: self, handler
**Returns**: None
**Description**: Register a review handler (sync). Handler returns decision string or None.



## Function: _trace_id

**Parameters**: self
**Returns**: str


## Function: escalate

**Parameters**: self, agent, module, trigger_reason, proposed_action, priority, policy_hash, metadata
**Returns**: EscalationRequest
**Description**: Activate HITL escalation for a given trigger.

        Emits ``hitl_escalation_activation`` + ``reenters_safety`` ADG edges.
        Logs via HITLDecisionLogger.
        



## Function: pending

**Parameters**: self
**Returns**: list[EscalationRequest]


## Function: resolved

**Parameters**: self
**Returns**: list[EscalationRequest]


## Function: requires_human_review

**Parameters**: self, request
**Returns**: bool
**Description**: Check if a request requires human review (ADG: requires_human_review edge).

        All escalations with priority >= HIGH require human review.
        



## Function: pending_count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using EscalationPriority
escalationpriority = EscalationPriority()
```

```python
# Using EscalationRequest
escalationrequest = EscalationRequest()
escalationrequest.resolve()
```

```python
# Using HITLEscalationActivator
hitlescalationactivator = HITLEscalationActivator()
hitlescalationactivator.register_handler()
hitlescalationactivator.escalate()
```

### Function Usage

```python
# Using get_hitl_escalation_activator
result = get_hitl_escalation_activator()
```

```python
# Using reset_hitl_escalation_activator
result = reset_hitl_escalation_activator()
```

```python
# Using resolve
result = resolve(decision)
```



---
**Generated**: 2026-03-26T09:39:05.012483
**Type**: api_reference
**Quality**: comprehensive
