# API Documentation: safety_layer_enforcer

**Target Audience**: developers, api_users

# safety_layer_enforcer API Documentation

**File**: `safety_layer_enforcer.py`
**Classes**: 1
**Functions**: 6

## Classes

- **L5SafetyLayer**

## Functions

- **create_l5_safety_layer** -> L5SafetyLayer
- **__init__**
- **_validate_cost_estimate** -> bool
- **track_action_cost** -> float
- **get_safety_stats** -> dict[str, Any]
- **cleanup** -> Any


## Class: L5SafetyLayer

**Description**: L5 Safety Layer that validates all actions before execution.

### Methods

#### __init__
**Parameters**: self, cost_limit_usd
**Description**: Initialize the safety layer.

        Args:
            cost_limit_usd: Maximum allowed cost in USD
        

#### _validate_cost_estimate
**Parameters**: self, request
**Returns**: bool
**Description**: Validate if the estimated cost is within budget.

        Args:
            request: ActionRequest to validate

        Returns:
            True if cost is acceptable, False otherwise
        

#### track_action_cost
**Parameters**: self, model, input_tokens, output_tokens
**Returns**: float
**Description**: Track actual cost after action execution.

        Args:
            model: Model used
            input_tokens: Input tokens consumed
            output_tokens: Output tokens generated

        Returns:
            Cost of the action

        Raises:
            BudgetExceededError: If budget is exceeded
        

#### get_safety_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get safety layer statistics.

        Returns:
            Dictionary with safety statistics
        

#### cleanup
**Parameters**: self
**Returns**: Any
**Description**: Cleanup resources and sessions.



## Function: create_l5_safety_layer

**Parameters**: cost_limit_usd
**Returns**: L5SafetyLayer
**Description**: Factory function to create L5 safety layer.

    Args:
        cost_limit_usd: Maximum allowed cost in USD

    Returns:
        L5SafetyLayer instance
    



## Function: __init__

**Parameters**: self, cost_limit_usd
**Description**: Initialize the safety layer.

        Args:
            cost_limit_usd: Maximum allowed cost in USD
        



## Function: _validate_cost_estimate

**Parameters**: self, request
**Returns**: bool
**Description**: Validate if the estimated cost is within budget.

        Args:
            request: ActionRequest to validate

        Returns:
            True if cost is acceptable, False otherwise
        



## Function: track_action_cost

**Parameters**: self, model, input_tokens, output_tokens
**Returns**: float
**Description**: Track actual cost after action execution.

        Args:
            model: Model used
            input_tokens: Input tokens consumed
            output_tokens: Output tokens generated

        Returns:
            Cost of the action

        Raises:
            BudgetExceededError: If budget is exceeded
        



## Function: get_safety_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get safety layer statistics.

        Returns:
            Dictionary with safety statistics
        



## Function: cleanup

**Parameters**: self
**Returns**: Any
**Description**: Cleanup resources and sessions.



## Usage Examples

### Class Usage

```python
# Using L5SafetyLayer
l5safetylayer = L5SafetyLayer()
l5safetylayer.track_action_cost()
l5safetylayer.get_safety_stats()
```

### Function Usage

```python
# Using create_l5_safety_layer
result = create_l5_safety_layer(cost_limit_usd)
```

```python
# Using __init__
result = __init__(cost_limit_usd)
```

```python
# Using _validate_cost_estimate
result = _validate_cost_estimate(request)
```



---
**Generated**: 2026-03-26T09:39:04.925421
**Type**: api_reference
**Quality**: comprehensive
