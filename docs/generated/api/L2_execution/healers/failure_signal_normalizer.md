# API Documentation: failure_signal_normalizer

**Target Audience**: developers, api_users

# failure_signal_normalizer API Documentation

**File**: `failure_signal_normalizer.py`
**Classes**: 0
**Functions**: 3


## Functions

- **normalize_failure_signal** -> str
- **extract_failure_metadata** -> dict
- **generate_fallback_vector** -> list[float]


## Function: normalize_failure_signal

**Parameters**: action
**Returns**: str
**Description**: Compose a normalized embedding-input text from a healing action dict.

    The normalized text encodes the *semantic content* of the failure —
    failure type, the gate that triggered it, the agent that handled it,
    and (when present) the first 200 chars of error_message / stack_trace.
    Territory and other metadata are captured separately (not embedded) per
    the Embedding Lifecycle architecture (territory is metadata, not content).

    Field priority:
      1. failure_type / routing_tier — stable category string (uppercased)
      2. routing_gate   — specific check ID that triggered the failure;
                          more structured and semantic than fix_summary alone
      3. agent          — healer that processed the event
      4. fix_summary    — optional human-readable description of the repair
      5. error_message  — first 200 chars of the raw error message (D1)
      6. stack_trace    — first 200 chars of the exception stack trace (D1)

    Args:
        action: A healing action dict as stored in
            state_mgr.state["healing_actions"].  Expected keys (all
            optional with safe defaults):
              - "type" / "routing_tier": failure category string
              - "routing_gate": specific gate/check identifier (e.g. "gate:import_boundary_check")
              - "agent": healer identifier
              - "fix_summary": human-readable repair description
              - "error_message": raw error string (enrichment field)
              - "stack_trace": exception traceback text (enrichment field)

    Returns:
        A normalized ASCII text string for embedding, e.g.:
        "IMPORT_BOUNDARY_VIOLATION gate:import_boundary_check DependencyRepairAgent yaml config loader"
    



## Function: extract_failure_metadata

**Parameters**: action
**Returns**: dict
**Description**: Extract metadata fields that are stored alongside (not embedded into) the vector.

    These fields are stored as metadata in the vector DB record per the
    Embedding Lifecycle architecture: territory, invariant ids, repo context.

    Args:
        action: A healing action dict.

    Returns:
        Dict of metadata fields to store alongside the failure_vector.
    



## Function: generate_fallback_vector

**Parameters**: text
**Returns**: list[float]
**Description**: Produce a deterministic 16-dimensional L2-normalised fallback vector.

    Used in BOOTSTRAP_MODE only (initial environment setup) to ensure
    failure_vector is never None. The vector carries no semantic meaning but
    preserves determinism and allows FAISS storage to proceed.
    Normal operation MUST use bge-m3 (mandatory system dependency).

    The vector is tagged with ``vector_source="hash-fallback"`` metadata by
    the caller; downstream novelty/cluster logic MUST NOT interpret it as a
    real semantic embedding (enforced by VectorSourceMismatchError in C3).

    Args:
        text: The normalized failure signal text (output of normalize_failure_signal).

    Returns:
        A 16-dimensional L2-normalised list[float]. Never empty, never None.
        Two consecutive calls with identical text always return identical output.
    



## Usage Examples

### Function Usage

```python
# Using normalize_failure_signal
result = normalize_failure_signal(action)
```

```python
# Using extract_failure_metadata
result = extract_failure_metadata(action)
```

```python
# Using generate_fallback_vector
result = generate_fallback_vector(text)
```



---
**Generated**: 2026-03-26T09:39:03.801050
**Type**: api_reference
**Quality**: comprehensive
