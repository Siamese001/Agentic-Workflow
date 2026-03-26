# API Documentation: boundary_contracts

**Target Audience**: developers, api_users

# boundary_contracts API Documentation

**File**: `boundary_contracts.py`
**Classes**: 4
**Functions**: 9

## Classes

- **SSOTBindingError** (inherits from Exception)
- **ContextRetrievalError** (inherits from Exception)
- **BoundarySchemaError** (inherits from Exception)
- **MetaInvariantError** (inherits from Exception)

## Functions

- **resolve_ssot_binding** -> SSOTBinding
- **build_context_retrieval_request** -> ContextRetrievalRequest
- **validate_context_retrieval_read_only** -> bool
- **validate_boundary_schema** -> bool
- **build_boundary_schema** -> BoundarySchemaDescriptor
- **assert_cross_run_pins** -> tuple[InvariantCheck, InvariantViolation | None]
- **assert_chain_closure** -> tuple[InvariantCheck, InvariantViolation | None]
- **run_meta_invariants** -> MetaInvariantReport
- **fail_closed_on_violation** -> bool


## Class: SSOTBindingError

**Description**: Raised when SSOT binding resolution fails.

**Inherits from**: Exception



## Class: ContextRetrievalError

**Description**: Raised when context retrieval request validation fails.

**Inherits from**: Exception



## Class: BoundarySchemaError

**Description**: Raised when boundary schema validation fails.

**Inherits from**: Exception



## Class: MetaInvariantError

**Description**: Raised when meta-invariant check fails (fail-closed).

**Inherits from**: Exception



## Function: resolve_ssot_binding

**Parameters**: node_id, blueprint_registry
**Returns**: SSOTBinding
**Description**: §1.5 — Resolve node_id against the structure blueprint registry.

    blueprint_registry maps node_id -> blueprint_entry.
    Fail-closed: unresolved node_id raises SSOTBindingError.
    



## Function: build_context_retrieval_request

**Parameters**: trace_id, query_hash, semantic_clock_tick
**Returns**: ContextRetrievalRequest
**Description**: §3.8 — Build a typed context retrieval request (L0→L4).



## Function: validate_context_retrieval_read_only

**Parameters**: request
**Returns**: bool
**Description**: §3.8 — Validate that the request is read-only. Fail-closed.



## Function: validate_boundary_schema

**Parameters**: descriptor
**Returns**: bool
**Description**: §12.1 / §2.4 — Validate a boundary schema descriptor. Fail-closed.

    Rejects INVALID or MISSING schemas.
    



## Function: build_boundary_schema

**Parameters**: schema_id, schema_version, source_layer, target_layer, known_schemas
**Returns**: BoundarySchemaDescriptor
**Description**: §12.1 / §2.4 — Build a boundary schema descriptor.

    If known_schemas is provided, validates schema_id exists and version matches.
    



## Function: assert_cross_run_pins

**Parameters**: discovery_hash, expected_discovery_hash, schema_version, expected_schema_version
**Returns**: tuple[InvariantCheck, InvariantViolation | None]
**Description**: Assert cross-run pinned values are unchanged.



## Function: assert_chain_closure

**Parameters**: expected_artifacts, actual_artifacts
**Returns**: tuple[InvariantCheck, InvariantViolation | None]
**Description**: Assert P1–P5 artifact chain closure: no orphans, no missing.



## Function: run_meta_invariants

**Parameters**: trace_id, run_id, semantic_clock_tick, discovery_hash, expected_discovery_hash, schema_version, expected_schema_version, expected_artifacts, actual_artifacts
**Returns**: MetaInvariantReport
**Description**: Run all meta-invariant checks and produce a report.

    Fail-closed: if any check fails, pass_fail is False.
    



## Function: fail_closed_on_violation

**Parameters**: report
**Returns**: bool
**Description**: Raise MetaInvariantError if the report contains any violations.



## Usage Examples

### Class Usage

```python
# Using SSOTBindingError
ssotbindingerror = SSOTBindingError()
```

```python
# Using ContextRetrievalError
contextretrievalerror = ContextRetrievalError()
```

```python
# Using BoundarySchemaError
boundaryschemaerror = BoundarySchemaError()
```

### Function Usage

```python
# Using resolve_ssot_binding
result = resolve_ssot_binding(node_id, blueprint_registry)
```

```python
# Using build_context_retrieval_request
result = build_context_retrieval_request(trace_id, query_hash)
```

```python
# Using validate_context_retrieval_read_only
result = validate_context_retrieval_read_only(request)
```



---
**Generated**: 2026-03-26T09:39:02.604399
**Type**: api_reference
**Quality**: comprehensive
