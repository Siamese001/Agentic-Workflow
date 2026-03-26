# API Documentation: activation_gate

**Target Audience**: developers, api_users

# activation_gate API Documentation

**File**: `activation_gate.py`
**Classes**: 0
**Functions**: 1


## Functions

- **assert_activation_allowed** -> None


## Function: assert_activation_allowed

**Parameters**: trace_id
**Returns**: None
**Description**: FAIL-CLOSED activation gate.

    Verifies that all three enforcement subsystems are importable.
    Raises PermissionError with a deterministic message listing any
    missing components if the check fails.

    Args:
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If any required enforcement component is missing.
    



## Usage Examples

### Function Usage

```python
# Using assert_activation_allowed
result = assert_activation_allowed(trace_id)
```



---
**Generated**: 2026-03-26T09:39:04.755326
**Type**: api_reference
**Quality**: comprehensive
