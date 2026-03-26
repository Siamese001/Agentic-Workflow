# API Documentation: embedding_non_interference_guardrail

**Target Audience**: developers, api_users

# embedding_non_interference_guardrail API Documentation

**File**: `embedding_non_interference_guardrail.py`
**Classes**: 1
**Functions**: 5

## Classes

- **C0InterferenceViolation** (inherits from RuntimeError)

## Functions

- **assert_c0_context_clean** -> None
- **assert_no_c0_influence** -> None
- **verify_routing_decision_clean** -> bool
- **assert_routing_decision_clean** -> None
- **scan_file_for_c0_mutations** -> list[str]


## Class: C0InterferenceViolation

**Description**: Raised when C0 RAG context is found to influence routing inputs.

**Inherits from**: RuntimeError



## Function: assert_c0_context_clean

**Parameters**: c0_context
**Returns**: None
**Description**: Assert that *c0_context* does not contain routing-influencing fields.

    C0 context is strictly informational.  The presence of any field from
    ``_C0_FORBIDDEN_FIELDS`` means C0 is leaking into routing / execution
    tier / safety configuration — a hard violation.

    Args:
        c0_context: The C0 context dict to inspect.

    Raises:
        C0InterferenceViolation: if any forbidden field is present.
    



## Function: assert_no_c0_influence

**Parameters**: routing_inputs, c0_context
**Returns**: None
**Description**: Assert that *routing_inputs* contains no C0 RAG markers.

    Args:
        routing_inputs: The dict of inputs passed to the routing tier
            (e.g. RoutingInputs fields, manifest dict).
        c0_context: Optional C0 context dict.  If provided, we additionally
            verify that none of its keys/values appear verbatim in
            routing_inputs.

    Raises:
        C0InterferenceViolation: if any C0 marker is detected.
    



## Function: verify_routing_decision_clean

**Parameters**: decision
**Returns**: bool
**Description**: Return True if *decision* contains no C0 provenance markers.

    Does NOT raise; returns False on detection so callers can log and decide
    whether to hard-fail.
    



## Function: assert_routing_decision_clean

**Parameters**: decision
**Returns**: None
**Description**: Raise C0InterferenceViolation if *decision* carries C0 markers.



## Function: scan_file_for_c0_mutations

**Parameters**: source_path
**Returns**: list[str]
**Description**: AST-scan *source_path* for writes to C0-marker attributes.

    Returns a list of violation strings (empty == clean).
    



## Usage Examples

### Class Usage

```python
# Using C0InterferenceViolation
c0interferenceviolation = C0InterferenceViolation()
```

### Function Usage

```python
# Using assert_c0_context_clean
result = assert_c0_context_clean(c0_context)
```

```python
# Using assert_no_c0_influence
result = assert_no_c0_influence(routing_inputs, c0_context)
```

```python
# Using verify_routing_decision_clean
result = verify_routing_decision_clean(decision)
```



---
**Generated**: 2026-03-26T09:39:04.813067
**Type**: api_reference
**Quality**: comprehensive
