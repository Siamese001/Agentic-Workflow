# API Documentation: cognitive_diff_types

**Target Audience**: developers, api_users

# cognitive_diff_types API Documentation

**File**: `cognitive_diff_types.py`
**Classes**: 3
**Functions**: 9

## Classes

- **CognitiveStateSnapshot**
- **DiffOp**
- **L3CognitiveDiffBundle**

## Functions

- **compute_cognitive_diff** -> tuple[DiffOp, ...]
- **_compute_bundle_trace_id** -> str
- **emit_cognitive_diff_bundle** -> L3CognitiveDiffBundle
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]


## Class: CognitiveStateSnapshot

**Description**: Minimal, stable snapshot of cognitive state at a decision boundary.

    All fields are JSON-primitive compatible. No repr(), no Enum objects.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: DiffOp

**Description**: A single field-level diff operation between before and after states.

    path: dotted field name (e.g., "selected_path", "risk_score")
    before: JSON-primitive value from the before state
    after: JSON-primitive value from the after state
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: L3CognitiveDiffBundle

**Description**: §Wave4.2 — Deterministic cognitive diff emitted at L3 orchestration boundary.

    Required fields:
      artifact_type     — fixed "COGNITIVE_DIFF_BUNDLE"
      semantic_clock    — required SemanticClockSnapshot (Phase 3.2)
      trace_id          — deterministic (SHA-256 of canonical payload)
      before            — CognitiveStateSnapshot
      after             — CognitiveStateSnapshot
      diff              — sorted tuple of DiffOp
      policy_config_hash — optional
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic serialization with sorted keys.



## Function: compute_cognitive_diff

**Parameters**: before, after
**Returns**: tuple[DiffOp, ...]
**Description**: Compute sorted diff ops between two CognitiveStateSnapshot instances.

    Compares all tracked fields. Only changed fields produce a DiffOp.
    Ops are sorted by path (alphabetical).
    



## Function: _compute_bundle_trace_id

**Parameters**: before, after, tick
**Returns**: str
**Description**: Deterministic trace_id from canonical payload hash.



## Function: emit_cognitive_diff_bundle

**Parameters**: before, after, semantic_clock, policy_config_hash
**Returns**: L3CognitiveDiffBundle
**Description**: §Wave4.2 — Build an L3CognitiveDiffBundle deterministically.

    1. Compute sorted diff ops
    2. Generate deterministic trace_id
    3. Return frozen bundle
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


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
# Using CognitiveStateSnapshot
cognitivestatesnapshot = CognitiveStateSnapshot()
cognitivestatesnapshot.to_dict()
```

```python
# Using DiffOp
diffop = DiffOp()
diffop.to_dict()
```

```python
# Using L3CognitiveDiffBundle
l3cognitivediffbundle = L3CognitiveDiffBundle()
l3cognitivediffbundle.to_dict()
```

### Function Usage

```python
# Using compute_cognitive_diff
result = compute_cognitive_diff(before, after)
```

```python
# Using _compute_bundle_trace_id
result = _compute_bundle_trace_id(before, after)
```

```python
# Using emit_cognitive_diff_bundle
result = emit_cognitive_diff_bundle(before, after)
```



---
**Generated**: 2026-03-26T09:39:04.363226
**Type**: api_reference
**Quality**: comprehensive
