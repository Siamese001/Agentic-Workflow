# API Documentation: violation_event_types

**Target Audience**: developers, api_users

# violation_event_types API Documentation

**File**: `violation_event_types.py`
**Classes**: 1
**Functions**: 6

## Classes

- **ViolationEvent**

## Functions

- **_sha256** -> str
- **emit_violation_event** -> ViolationEvent
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **to_dict** -> dict[str, Any]
- **from_dict** -> ViolationEvent


## Class: ViolationEvent

**Description**: 
    Typed record of a Guardian decision outcome.

    Fields
    ------
    schema_version   : int   — bumped on breaking schema changes
    mission_id       : str   — non-empty identifier for the mission/run
    commit_tick      : int   — monotonic execution boundary (>= 0)
    guardian_decision: str   — one of "allow", "block", "escalate"
    violation_codes  : list  — sorted list of string violation codes
    severity_score   : float — in [0.0, 1.0]
    created_at_utc   : str   — ISO-8601 UTC timestamp string
    event_hash       : str   — sha256(canonical_bytes()); auto-computed
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding event_hash (self-referential).
        Keys sorted, violation_codes sorted list.
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]

#### from_dict
**Parameters**: cls, data
**Returns**: ViolationEvent



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: emit_violation_event

**Parameters**: mission_id, commit_tick, guardian_decision, violation_codes, severity_score, created_at_utc
**Returns**: ViolationEvent
**Description**: 
    Construct and emit a ViolationEvent.

    Pure recording — does not alter the guardian_decision.
    If _registry is provided, appends to it (for in-memory accumulation).
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding event_hash (self-referential).
        Keys sorted, violation_codes sorted list.
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: from_dict

**Parameters**: cls, data
**Returns**: ViolationEvent


## Usage Examples

### Class Usage

```python
# Using ViolationEvent
violationevent = ViolationEvent()
violationevent.canonical_bytes()
violationevent.to_dict()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using emit_violation_event
result = emit_violation_event(mission_id, commit_tick)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.657398
**Type**: api_reference
**Quality**: comprehensive
