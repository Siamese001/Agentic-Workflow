# API Documentation: replay_bundle_types

**Target Audience**: developers, api_users

# replay_bundle_types API Documentation

**File**: `replay_bundle_types.py`
**Classes**: 1
**Functions**: 5

## Classes

- **ReplayBundle**

## Functions

- **_sha256** -> str
- **build_replay_bundle** -> ReplayBundle
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **to_dict** -> dict[str, Any]


## Class: ReplayBundle

**Description**: 
    Immutable execution evidence artifact.

    Fields
    ------
    schema_version              : int
    mission_id                  : str   — non-empty
    execution_start_tick        : int   — >= 0
    execution_end_tick          : int   — >= execution_start_tick
    manifest_hash               : str   — non-empty sha256 of execution manifest
    active_config_hashes        : dict  — {policy_hash, routing_hash, model_hash, budget_hash, ...}
    retrieval_used              : bool  — True iff L4 retrieval was performed
    citation_hash               : str   — required iff retrieval_used=True
    prior_detection_signal_hash : str   — empty string if no prior signal
    prior_violation_event_hashes: list  — sorted list of ViolationEvent.event_hash strings
    tool_intent_hashes          : list  — sorted list of ToolIntent.intent_hash strings
    tool_result_hashes          : list  — sorted list of ToolResult.result_hash strings
    replay_hash                 : str   — sha256(canonical_bytes); auto-computed
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding replay_hash (self-referential).
        All list fields sorted. active_config_hashes keys sorted.
        No volatile fields (timestamps, trace IDs).
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: build_replay_bundle

**Parameters**: mission_id, execution_start_tick, execution_end_tick, manifest_hash, active_config_hashes
**Returns**: ReplayBundle
**Description**: Factory: build a ReplayBundle from execution parameters.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding replay_hash (self-referential).
        All list fields sorted. active_config_hashes keys sorted.
        No volatile fields (timestamps, trace IDs).
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using ReplayBundle
replaybundle = ReplayBundle()
replaybundle.canonical_bytes()
replaybundle.to_dict()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using build_replay_bundle
result = build_replay_bundle(mission_id, execution_start_tick)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.641583
**Type**: api_reference
**Quality**: comprehensive
