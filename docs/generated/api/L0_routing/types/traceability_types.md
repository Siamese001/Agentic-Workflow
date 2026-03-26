# API Documentation: traceability_types

**Target Audience**: developers, api_users

# traceability_types API Documentation

**File**: `traceability_types.py`
**Classes**: 11
**Functions**: 12

## Classes

- **ErrorSignature**
- **PolicyConfigPin**
- **PlanProvenance**
- **RetrievalQuery**
- **RetrievedChunk**
- **RerankScore**
- **CitationEntry**
- **CitationBundle**
- **CognitiveDiffBundle**
- **KnowledgeDirective** (inherits from Enum)
- **KnowledgeAdvisoryConstraint**

## Functions

- **validate_trace_id** -> str
- **compute_error_signature_hash** -> str
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None


## Class: ErrorSignature

**Description**: §5.2 — Deterministic error signature.

    Computed from error_type + target_node_id + time_bucket (semantic clock).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: PolicyConfigPin

**Description**: §4.2 — SHA-256 of policy config captured at healing wave start.

    Verified unchanged before every routing decision within the wave.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: PlanProvenance

**Description**: §6.7 — Links a generated plan to the specific Policy Liaison Node.

    Provides traceability from plan back to the policy that authorized it.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: RetrievalQuery

**Description**: §6.5 — RAG chain step 1: the retrieval query.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: RetrievedChunk

**Description**: §6.5 — RAG chain step 2: a single retrieved chunk.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: RerankScore

**Description**: §6.5 — RAG chain step 3: rerank score for a chunk.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: CitationEntry

**Description**: §6.5 — A single citation linking output to a retrieved chunk.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: CitationBundle

**Description**: §6.5 — RAG chain step 4: the complete citation bundle.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: CognitiveDiffBundle

**Description**: §15.2 — Diff between intended policy and actual execution.

    Required fields per spec:
      trace_id, incident_id, intended_policy_snapshot,
      actual_execution_trace, diff_summary, semantic_clock_tick
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: KnowledgeDirective

**Description**: Directive types from knowledge/graph layer.

**Inherits from**: Enum



## Class: KnowledgeAdvisoryConstraint

**Description**: §6.9 — Knowledge graph outputs are advisory-only.

    Any attempt to issue a control directive from the knowledge layer
    must be rejected fail-closed.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Function: validate_trace_id

**Parameters**: trace_id
**Returns**: str
**Description**: §15.5 — Validate trace ID matches strict format. Fail-closed.



## Function: compute_error_signature_hash

**Parameters**: error_type, target_node_id, time_bucket
**Returns**: str
**Description**: §5.2 — Compute deterministic error signature hash.



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


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ErrorSignature
errorsignature = ErrorSignature()
```

```python
# Using PolicyConfigPin
policyconfigpin = PolicyConfigPin()
```

```python
# Using PlanProvenance
planprovenance = PlanProvenance()
```

### Function Usage

```python
# Using validate_trace_id
result = validate_trace_id(trace_id)
```

```python
# Using compute_error_signature_hash
result = compute_error_signature_hash(error_type, target_node_id)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:03.481363
**Type**: api_reference
**Quality**: comprehensive
