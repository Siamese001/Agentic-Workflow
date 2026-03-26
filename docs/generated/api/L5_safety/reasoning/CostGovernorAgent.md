# API Documentation: CostGovernorAgent

**Target Audience**: developers, api_users

# CostGovernorAgent API Documentation

**File**: `CostGovernorAgent.py`
**Classes**: 2
**Functions**: 4

## Classes

- **BudgetExceededError** (inherits from Exception)
- **CostGovernorAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **track** -> float
- **heal_repository** -> dict[str, int]
- **heal** -> dict


## Class: BudgetExceededError

**Description**: Raised when LLM spending exceeds the configured budget limit.

**Inherits from**: Exception



## Class: CostGovernorAgent

**Description**: L5 Safety agent that tracks and limits LLM spend across models and tools.

    This financial guardrail monitors API costs and enforces budget constraints.
    It calculates costs based on token usage and raises BudgetExceededError
    when the configured limit is exceeded.

    Attributes:
        config: configuration dictionary with budget settings.
        limit: Maximum allowed spend in dollars.
        spend: Current accumulated spend in dollars.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize the cost governor with budget configuration.

        Args:
            config: configuration dictionary containing:
                - budget_limit: Maximum allowed spend in dollars (default: 10.0)
        

#### track
**Parameters**: self, model, input_tokens, output_tokens
**Returns**: float
**Description**: Calculate and record the cost of an LLM call.

        Args:
            model: Name of the LLM model used.
            input_tokens: Number of input tokens in the request.
            output_tokens: Number of output tokens in the response.

        Returns:
            Cost of this call in dollars.

        Raises:
            BudgetExceededError: If total spend exceeds the configured limit.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal cost governance violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (budget_exceeded)
                - model: Model that caused the overspend
                - spend: Current spend amount

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize the cost governor with budget configuration.

        Args:
            config: configuration dictionary containing:
                - budget_limit: Maximum allowed spend in dollars (default: 10.0)
        



## Function: track

**Parameters**: self, model, input_tokens, output_tokens
**Returns**: float
**Description**: Calculate and record the cost of an LLM call.

        Args:
            model: Name of the LLM model used.
            input_tokens: Number of input tokens in the request.
            output_tokens: Number of output tokens in the response.

        Returns:
            Cost of this call in dollars.

        Raises:
            BudgetExceededError: If total spend exceeds the configured limit.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal cost governance violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (budget_exceeded)
                - model: Model that caused the overspend
                - spend: Current spend amount

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using BudgetExceededError
budgetexceedederror = BudgetExceededError()
```

```python
# Using CostGovernorAgent
costgovernoragent = CostGovernorAgent()
costgovernoragent.track()
costgovernoragent.heal_repository()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using track
result = track(model, input_tokens)
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:05.112658
**Type**: api_reference
**Quality**: comprehensive
