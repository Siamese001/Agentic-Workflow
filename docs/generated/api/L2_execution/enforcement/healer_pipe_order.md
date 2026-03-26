# API Documentation: healer_pipe_order

**Target Audience**: developers, api_users

# healer_pipe_order API Documentation

**File**: `healer_pipe_order.py`
**Classes**: 0
**Functions**: 1


## Functions

- **enforce_healer_pipe_order** -> None


## Function: enforce_healer_pipe_order

**Parameters**: expected_steps, observed_steps, trace_id
**Returns**: None
**Description**: Validate that observed_steps exactly matches expected_steps.

    This is the SINGLE runtime gate for G-2-3 enforcement.

    Args:
        expected_steps: The canonical 10-step tuple (HEALER_PIPE_ORDER).
        observed_steps: Steps actually executed, in execution order.
        trace_id: Optional trace identifier for diagnostics.

    Raises:
        AssertionError: If expected_steps length != 10.
        PermissionError: If observed_steps does not exactly match expected_steps
            (wrong length, wrong order, missing/extra/duplicated steps).
    



## Usage Examples

### Function Usage

```python
# Using enforce_healer_pipe_order
result = enforce_healer_pipe_order(expected_steps, observed_steps)
```



---
**Generated**: 2026-03-26T09:39:03.707673
**Type**: api_reference
**Quality**: comprehensive
