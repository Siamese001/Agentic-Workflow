# API Documentation: boundary_types

**Target Audience**: developers, api_users

# boundary_types API Documentation

**File**: `boundary_types.py`
**Classes**: 10
**Functions**: 8

## Classes

- **SSOTBinding**
- **ContextRetrievalRequest**
- **SchemaValidationStatus** (inherits from Enum)
- **BoundarySchemaDescriptor**
- **InvariantSeverity** (inherits from Enum)
- **InvariantViolation**
- **InvariantCheck**
- **MetaInvariantReport**
- **SideEffectRegistry**
- **V15DiscoverySchema**

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None


## Class: SSOTBinding

**Description**: §1.5 — Proves a node_id resolves to a valid SSOT definition.

    The binding links the manifest's node_id to the blueprint entry
    that authorizes it.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ContextRetrievalRequest

**Description**: §3.8 — Typed request from L0 to L4 (advisory-only, read-only).

    Required fields: trace_id, query_hash, semantic_clock_tick.
    Constraint: No direct writes from L0.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: SchemaValidationStatus

**Description**: Status of a boundary schema validation.

**Inherits from**: Enum



## Class: BoundarySchemaDescriptor

**Description**: §12.1 / §2.4 — Typed and versioned boundary between layers.

    Every cross-layer call must declare its schema version and the
    source/target layers. Validation status is captured.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: InvariantSeverity

**Description**: Severity of an invariant violation.

**Inherits from**: Enum



## Class: InvariantViolation

**Description**: A single meta-invariant violation with evidence.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: InvariantCheck

**Description**: A single invariant check result.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: MetaInvariantReport

**Description**: Meta-governor report for end-of-wave / end-of-run invariant checks.

    Fields: trace_id, run_id, semantic_clock_tick, checks, pass_fail, violations.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: SideEffectRegistry

**Description**: §12.2 — Immutable registry of side effects produced during a heal wave.

    Tracks all resources touched (read/written) and APIs called,
    enabling deterministic replay and audit.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: V15DiscoverySchema

**Description**: §8.4 — Pinned discovery schema for the V15 Environment Under Test.

    ALL fields are required. Missing field = HARD FAIL in guardian tests.
    MRO scanners MUST consume ONLY this schema (no live reflection fallback).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using SSOTBinding
ssotbinding = SSOTBinding()
```

```python
# Using ContextRetrievalRequest
contextretrievalrequest = ContextRetrievalRequest()
```

```python
# Using SchemaValidationStatus
schemavalidationstatus = SchemaValidationStatus()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:03.429035
**Type**: api_reference
**Quality**: comprehensive
