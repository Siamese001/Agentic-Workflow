# API Documentation: dependency_healing_integration_types

**Target Audience**: developers, api_users

# dependency_healing_integration_types API Documentation

**File**: `dependency_healing_integration_types.py`
**Classes**: 3
**Functions**: 10

## Classes

- **HealingStrategyProtocol** (inherits from Protocol)
- **DependencyPruningStrategy**
- **MockContext**

## Functions

- **get_dependency_strategy** -> DependencyPruningStrategy
- **register_dependency_healing** -> dict[str, Any]
- **get_integration_status** -> dict[str, Any]
- **can_heal** -> bool
- **heal** -> dict
- **__init__** -> None
- **_ensure_initialized** -> None
- **can_heal** -> bool
- **heal** -> dict
- **report** -> None


## Class: HealingStrategyProtocol

**Description**: Protocol for healing strategies.

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



## Class: DependencyPruningStrategy

**Description**: 
    Healing strategy for unused dependency violations.

    Wraps DependencyPruningAgent to detect and optionally remove
    unused Python dependencies from requirements.txt.
    

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None
**Description**: 
        Initialize the dependency pruning strategy.

        Args:
            project_root: Root directory of the project (defaults to cwd)
        

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
        Prune unused dependencies.

        Args:
            violation: Violation details (may include specific package)
            context: Healing context (may include dry_run flag)

        Returns:
            dict with healing results
        



## Class: MockContext

### Methods

#### report
**Parameters**: self, msg
**Returns**: None



## Function: get_dependency_strategy

**Parameters**: project_root
**Returns**: DependencyPruningStrategy
**Description**: Get or create the dependency pruning strategy instance.



## Function: register_dependency_healing

**Parameters**: project_root
**Returns**: dict[str, Any]
**Description**: 
    Register dependency pruning as a healing strategy.

    Args:
        project_root: Optional project root path

    Returns:
        dict with registration status
    



## Function: get_integration_status

**Returns**: dict[str, Any]
**Description**: Get the current status of dependency healing integration.



## Function: can_heal

**Parameters**: self, violation
**Returns**: bool
**Description**: Check if this strategy can heal the violation.



## Function: heal

**Parameters**: self, violation, context
**Returns**: dict
**Description**: Execute healing and return result.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None
**Description**: 
        Initialize the dependency pruning strategy.

        Args:
            project_root: Root directory of the project (defaults to cwd)
        



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
        Prune unused dependencies.

        Args:
            violation: Violation details (may include specific package)
            context: Healing context (may include dry_run flag)

        Returns:
            dict with healing results
        



## Function: report

**Parameters**: self, msg
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using HealingStrategyProtocol
healingstrategyprotocol = HealingStrategyProtocol()
healingstrategyprotocol.can_heal()
healingstrategyprotocol.heal()
```

```python
# Using DependencyPruningStrategy
dependencypruningstrategy = DependencyPruningStrategy()
dependencypruningstrategy.can_heal()
dependencypruningstrategy.heal()
```

```python
# Using MockContext
mockcontext = MockContext()
mockcontext.report()
```

### Function Usage

```python
# Using get_dependency_strategy
result = get_dependency_strategy(project_root)
```

```python
# Using register_dependency_healing
result = register_dependency_healing(project_root)
```

```python
# Using get_integration_status
result = get_integration_status()
```



---
**Generated**: 2026-03-26T09:39:05.784524
**Type**: api_reference
**Quality**: comprehensive
