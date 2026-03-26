# API Documentation: self_healing_trigger_types

**Target Audience**: developers, api_users

# self_healing_trigger_types API Documentation

**File**: `self_healing_trigger_types.py`
**Classes**: 1
**Functions**: 5

## Classes

- **L2SelfHealingTrigger**

## Functions

- **_compute_trigger_trace_id** -> str
- **is_healing_authorized** -> bool
- **emit_self_healing_trigger** -> L2SelfHealingTrigger | None
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]


## Class: L2SelfHealingTrigger

**Description**: §Wave4.3 — Authorized self-healing trigger emitted at L2 control spine.

    Required fields:
      artifact_type        — fixed "SELF_HEALING_TRIGGER"
      semantic_clock       — required SemanticClockSnapshot
      trace_id             — deterministic (SHA-256 of canonical payload)
      target               — stable identifier (file path or subsystem key)
      reason_code          — stable string (no Enum objects)
      recommended_actions  — sorted tuple of action strings
      risk_tier            — tier string (e.g., "low", "medium", "high", "critical")
      authorization        — how healing was authorized ("AUTO_APPROVED" or "HIL_APPROVED")
      policy_config_hash   — optional
      route_context        — optional stable string
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic serialization with sorted keys.



## Function: _compute_trigger_trace_id

**Parameters**: target, reason_code, actions, tick
**Returns**: str
**Description**: Deterministic trace_id from canonical payload hash.



## Function: is_healing_authorized

**Parameters**: decision
**Returns**: bool
**Description**: §Wave4.3 — Check if a decision authorizes healing emission.



## Function: emit_self_healing_trigger

**Parameters**: decision, target, reason_code, recommended_actions, risk_tier, semantic_clock, policy_config_hash, route_context
**Returns**: L2SelfHealingTrigger | None
**Description**: §Wave4.3 — Emit a SelfHealingTrigger ONLY when authorized.

    Returns None if healing is not authorized (rejected/pending/read-only).
    Raises ValueError if semantic_clock is None (even for authorized paths).

    Authorization gate:
      AUTO_APPROVED / HIL_APPROVED → emit trigger
      Everything else → return None (no emission)
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic serialization with sorted keys.



## Usage Examples

### Class Usage

```python
# Using L2SelfHealingTrigger
l2selfhealingtrigger = L2SelfHealingTrigger()
l2selfhealingtrigger.to_dict()
```

### Function Usage

```python
# Using _compute_trigger_trace_id
result = _compute_trigger_trace_id(target, reason_code)
```

```python
# Using is_healing_authorized
result = is_healing_authorized(decision)
```

```python
# Using emit_self_healing_trigger
result = emit_self_healing_trigger(decision, target)
```



---
**Generated**: 2026-03-26T09:39:04.005383
**Type**: api_reference
**Quality**: comprehensive
