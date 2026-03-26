# API Documentation: chaos_healing_integration_types

**Target Audience**: developers, api_users

# chaos_healing_integration_types API Documentation

**File**: `chaos_healing_integration_types.py`
**Classes**: 2
**Functions**: 9

## Classes

- **HealingStrategyProtocol** (inherits from Protocol)
- **ChaosResilienceStrategy**

## Functions

- **get_chaos_strategy** -> ChaosResilienceStrategy
- **register_chaos_healing** -> dict[str, Any]
- **get_integration_status** -> dict[str, Any]
- **can_heal** -> bool
- **heal** -> dict
- **__init__** -> None
- **_ensure_initialized** -> None
- **can_heal** -> bool
- **heal** -> dict


## Class: HealingStrategyProtocol

**Description**: Protocol for healing strategies - matches HealingSovereignOrchestrator interface.

**Inherits from**: Protocol

### Methods

#### can_heal
**Parameters**: self, violation
**Returns**: bool
**Description**: Check if this strategy can heal the violation.

#### heal
**Parameters**: self, violation, context
**Returns**: dict
**Description**: Execute healing and return result.



## Class: ChaosResilienceStrategy

**Description**: 
    Healing strategy that validates system resilience after healing.

    Use case: After a healing operation completes, run chaos tests
    to verify the system can handle failures gracefully.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the chaos resilience strategy.

#### _ensure_initialized
**Parameters**: self
**Returns**: None
**Description**: Lazy initialization to avoid import cycles.

#### can_heal
**Parameters**: self, violation
**Returns**: bool
**Description**: 
        Check if this strategy can handle the violation.

        Args:
            violation: Violation details with 'type' key

        Returns:
            True if this strategy can handle the violation type
        

#### heal
**Parameters**: self, violation, context
**Returns**: dict
**Description**: 
        Run chaos tests and report resilience status.

        Args:
            violation: Violation details
            context: Healing context (may include dry_run flag)

        Returns:
            dict with healing results
        



## Function: get_chaos_strategy

**Returns**: ChaosResilienceStrategy
**Description**: Get or create the chaos resilience strategy instance.



## Function: register_chaos_healing

**Returns**: dict[str, Any]
**Description**: 
    Register chaos engineering as a healing strategy.

    Returns:
        dict with registration status
    



## Function: get_integration_status

**Returns**: dict[str, Any]
**Description**: Get the current status of chaos healing integration.



## Function: can_heal

**Parameters**: self, violation
**Returns**: bool
**Description**: Check if this strategy can heal the violation.



## Function: heal

**Parameters**: self, violation, context
**Returns**: dict
**Description**: Execute healing and return result.



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the chaos resilience strategy.



## Function: _ensure_initialized

**Parameters**: self
**Returns**: None
**Description**: Lazy initialization to avoid import cycles.



## Function: can_heal

**Parameters**: self, violation
**Returns**: bool
**Description**: 
        Check if this strategy can handle the violation.

        Args:
            violation: Violation details with 'type' key

        Returns:
            True if this strategy can handle the violation type
        



## Function: heal

**Parameters**: self, violation, context
**Returns**: dict
**Description**: 
        Run chaos tests and report resilience status.

        Args:
            violation: Violation details
            context: Healing context (may include dry_run flag)

        Returns:
            dict with healing results
        



## Usage Examples

### Class Usage

```python
# Using HealingStrategyProtocol
healingstrategyprotocol = HealingStrategyProtocol()
healingstrategyprotocol.can_heal()
healingstrategyprotocol.heal()
```

```python
# Using ChaosResilienceStrategy
chaosresiliencestrategy = ChaosResilienceStrategy()
chaosresiliencestrategy.can_heal()
chaosresiliencestrategy.heal()
```

### Function Usage

```python
# Using get_chaos_strategy
result = get_chaos_strategy()
```

```python
# Using register_chaos_healing
result = register_chaos_healing()
```

```python
# Using get_integration_status
result = get_integration_status()
```



---
**Generated**: 2026-03-26T09:39:05.752208
**Type**: api_reference
**Quality**: comprehensive
