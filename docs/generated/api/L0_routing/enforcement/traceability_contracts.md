# API Documentation: traceability_contracts

**Target Audience**: developers, api_users

# traceability_contracts API Documentation

**File**: `traceability_contracts.py`
**Classes**: 8
**Functions**: 12

## Classes

- **TraceIDFormatError** (inherits from Exception)
- **ErrorSignatureError** (inherits from Exception)
- **PolicyConfigPinError** (inherits from Exception)
- **ManifestHashError** (inherits from Exception)
- **PlanProvenanceError** (inherits from Exception)
- **RAGChainError** (inherits from Exception)
- **CognitiveDiffError** (inherits from Exception)
- **AdvisoryViolationError** (inherits from Exception)

## Functions

- **generate_trace_id** -> str
- **build_error_signature** -> ErrorSignature
- **pin_policy_config** -> PolicyConfigPin
- **verify_policy_config_unchanged** -> bool
- **verify_manifest_hash** -> bool
- **build_plan_provenance** -> PlanProvenance
- **build_retrieval_query** -> RetrievalQuery
- **build_retrieved_chunk** -> RetrievedChunk
- **validate_retrieval_set** -> bool
- **validate_citation_chain** -> bool
- **build_cognitive_diff_bundle** -> CognitiveDiffBundle
- **enforce_advisory_only** -> KnowledgeAdvisoryConstraint


## Class: TraceIDFormatError

**Description**: Raised when a trace ID does not match the required format.

**Inherits from**: Exception



## Class: ErrorSignatureError

**Description**: Raised when error signature construction fails.

**Inherits from**: Exception



## Class: PolicyConfigPinError

**Description**: Raised when policy config pin construction or verification fails.

**Inherits from**: Exception



## Class: ManifestHashError

**Description**: Raised when manifest hash verification fails.

**Inherits from**: Exception



## Class: PlanProvenanceError

**Description**: Raised when plan provenance construction fails.

**Inherits from**: Exception



## Class: RAGChainError

**Description**: Raised when RAG chain validation fails.

**Inherits from**: Exception



## Class: CognitiveDiffError

**Description**: Raised when CognitiveDiffBundle construction fails.

**Inherits from**: Exception



## Class: AdvisoryViolationError

**Description**: Raised when knowledge layer attempts a control directive.

**Inherits from**: Exception



## Function: generate_trace_id

**Parameters**: hex_suffix
**Returns**: str
**Description**: §15.5 — Generate a compliant trace ID: CC3AL1-{8 uppercase hex chars}.



## Function: build_error_signature

**Parameters**: error_type, target_node_id, time_bucket
**Returns**: ErrorSignature
**Description**: §5.2 — Build a deterministic error signature. Fail-closed.



## Function: pin_policy_config

**Parameters**: wave_id, policy_config_bytes, semantic_clock_tick
**Returns**: PolicyConfigPin
**Description**: §4.2 — Capture SHA-256 of policy config at wave start.



## Function: verify_policy_config_unchanged

**Parameters**: pin, current_config_bytes
**Returns**: bool
**Description**: §4.2 — Verify policy config unchanged since wave start. Fail-closed.



## Function: verify_manifest_hash

**Parameters**: ast_snippet, manifest_hash
**Returns**: bool
**Description**: §1.6 — Verify manifest_hash matches SHA-256 of ast_snippet bytes.



## Function: build_plan_provenance

**Parameters**: trace_id, plan_id, policy_liaison_node, semantic_clock_tick, plan_content
**Returns**: PlanProvenance
**Description**: §6.7 — Build a PlanProvenance linking plan to policy liaison node.



## Function: build_retrieval_query

**Parameters**: trace_id, query_text, source_agent, semantic_clock_tick
**Returns**: RetrievalQuery
**Description**: §6.5 — Build a RetrievalQuery with deterministic hash.



## Function: build_retrieved_chunk

**Parameters**: chunk_id, source_id, content, location, retrieval_query_hash
**Returns**: RetrievedChunk
**Description**: §6.5 — Build a RetrievedChunk with content hash.



## Function: validate_retrieval_set

**Parameters**: chunks, rerank_scores
**Returns**: bool
**Description**: §6.5 — Validate retrieval set: stable ordering, all chunks scored.

    - Every chunk must have a corresponding rerank score.
    - Rerank scores must be in descending order (stable ranking).
    



## Function: validate_citation_chain

**Parameters**: bundle, chunks, query
**Returns**: bool
**Description**: §6.5 — Validate citation chain end-to-end.

    - Every chunk must have at least one citation in the bundle.
    - Every citation must reference a valid chunk_id.
    - Bundle retrieval_query_hash must match query.query_hash.
    - Every citation retrieval_hash must match query.query_hash.
    



## Function: build_cognitive_diff_bundle

**Parameters**: trace_id, incident_id, intended_policy_snapshot, actual_execution_trace, diff_summary, semantic_clock_tick
**Returns**: CognitiveDiffBundle
**Description**: §15.2 — Build a CognitiveDiffBundle for incident response.



## Function: enforce_advisory_only

**Parameters**: constraint
**Returns**: KnowledgeAdvisoryConstraint
**Description**: §6.9 — Enforce that knowledge outputs are advisory-only.

    Fail-closed: if directive_type is CONTROL, raise immediately.
    



## Usage Examples

### Class Usage

```python
# Using TraceIDFormatError
traceidformaterror = TraceIDFormatError()
```

```python
# Using ErrorSignatureError
errorsignatureerror = ErrorSignatureError()
```

```python
# Using PolicyConfigPinError
policyconfigpinerror = PolicyConfigPinError()
```

### Function Usage

```python
# Using generate_trace_id
result = generate_trace_id(hex_suffix)
```

```python
# Using build_error_signature
result = build_error_signature(error_type, target_node_id)
```

```python
# Using pin_policy_config
result = pin_policy_config(wave_id, policy_config_bytes)
```



---
**Generated**: 2026-03-26T09:39:02.639004
**Type**: api_reference
**Quality**: comprehensive
