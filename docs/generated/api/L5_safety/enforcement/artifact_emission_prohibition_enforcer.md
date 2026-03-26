# API Documentation: artifact_emission_prohibition_enforcer

**Target Audience**: developers, api_users

# artifact_emission_prohibition_enforcer API Documentation

**File**: `artifact_emission_prohibition_enforcer.py`
**Classes**: 0
**Functions**: 1


## Functions

- **assert_layer_may_emit** -> None


## Function: assert_layer_may_emit

**Parameters**: artifact_kind, layer, trace_id
**Returns**: None
**Description**: Fail-closed guard: raises PermissionError if layer may not emit this artifact.

    Args:
        artifact_kind: The artifact type being constructed (e.g. "RESULT", "HEALING_PLAN").
        layer: The calling layer identifier (e.g. "L0", "L2", "L5", "L6").
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If layer is in FORBIDDEN_EMISSION_LAYERS and
            artifact_kind is in FORBIDDEN_ARTIFACT_KINDS.
    



## Usage Examples

### Function Usage

```python
# Using assert_layer_may_emit
result = assert_layer_may_emit(artifact_kind, layer)
```



---
**Generated**: 2026-03-26T09:39:04.776643
**Type**: api_reference
**Quality**: comprehensive
