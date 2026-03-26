# API Documentation: register_all_validators_util

**Target Audience**: developers, api_users

# register_all_validators_util API Documentation

**File**: `register_all_validators_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **initialize** -> dict[str, Any]
- **get_integration_status** -> dict[str, Any]
- **reset** -> None


## Function: initialize

**Returns**: dict[str, Any]
**Description**: 
    Initialize all orphan agent integrations.

    This function registers:
    - Red team validators (adversarial_probe, boundary_testing)
    - Chaos resilience healing strategy
    - Dependency pruning healing strategy

    Returns:
        dict with initialization status and details
    



## Function: get_integration_status

**Returns**: dict[str, Any]
**Description**: 
    Return comprehensive status of all integrations.

    Returns:
        dict with:
        - initialized: bool
        - validators_registered: list of validator names
        - strategies_registered: list of strategy names
        - module_status: dict of each module's status
    



## Function: reset

**Returns**: None
**Description**: 
    Reset integration state (for testing purposes only).

    WARNING: This should only be used in test fixtures.
    



## Usage Examples

### Function Usage

```python
# Using initialize
result = initialize()
```

```python
# Using get_integration_status
result = get_integration_status()
```

```python
# Using reset
result = reset()
```



---
**Generated**: 2026-03-26T09:39:05.675532
**Type**: api_reference
**Quality**: comprehensive
