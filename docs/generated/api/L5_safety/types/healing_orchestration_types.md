# API Documentation: healing_orchestration_types

**Target Audience**: developers, api_users

# healing_orchestration_types API Documentation

**File**: `healing_orchestration_types.py`
**Classes**: 3
**Functions**: 10

## Classes

- **HealingResult**
- **HealingSuiteResult**
- **HealingOrchestrationSuite**

## Functions

- **get_healing_suite** -> HealingOrchestrationSuite
- **run_healing_operation** -> HealingSuiteResult
- **__init__** -> None
- **_ensure_initialized** -> None
- **run_strategy** -> HealingResult
- **run_all** -> HealingSuiteResult
- **run_resilience_check** -> HealingResult
- **run_dependency_cleanup** -> HealingResult
- **get_available_strategies** -> list[str]
- **get_status** -> dict[str, Any]


## Class: HealingResult

**Description**: Result from a single healing operation.



## Class: HealingSuiteResult

**Description**: Aggregated result from running the full healing suite.



## Class: HealingOrchestrationSuite

**Description**: 
    Orchestrates healing operations across multiple strategies.

    Usage:
        suite = HealingOrchestrationSuite()
        result = suite.run_all(
            violation={"type": "resilience_check"},
            context={"dry_run": True}
        )
        if result.overall_success:
            print(f"Healed {result.total_violations_fixed} violations")
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the healing orchestration suite.

#### _ensure_initialized
**Parameters**: self
**Returns**: None
**Description**: Lazy initialization of healing strategies.

#### run_strategy
**Parameters**: self, strategy_name, violation, context
**Returns**: HealingResult
**Description**: 
        Run a specific healing strategy.

        Args:
            strategy_name: Name of the strategy to run
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingResult with healing details
        

#### run_all
**Parameters**: self, violation, context
**Returns**: HealingSuiteResult
**Description**: 
        Run all applicable healing strategies for a violation.

        Args:
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingSuiteResult with aggregated results
        

#### run_resilience_check
**Parameters**: self, context
**Returns**: HealingResult
**Description**: 
        Run chaos resilience check specifically.

        Args:
            context: Optional healing context

        Returns:
            HealingResult from chaos resilience strategy
        

#### run_dependency_cleanup
**Parameters**: self, dry_run, context
**Returns**: HealingResult
**Description**: 
        Run dependency pruning specifically.

        Args:
            dry_run: If True, only report what would be done
            context: Optional additional context

        Returns:
            HealingResult from dependency pruning strategy
        

#### get_available_strategies
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available strategy names.

#### get_status
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current status of the healing suite.



## Function: get_healing_suite

**Returns**: HealingOrchestrationSuite
**Description**: Get or create the global healing orchestration suite.



## Function: run_healing_operation

**Parameters**: violation, context
**Returns**: HealingSuiteResult
**Description**: 
    Convenience function to run healing for a violation.

    Args:
        violation: Violation details to heal
        context: Optional healing context

    Returns:
        HealingSuiteResult with all healing results
    



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the healing orchestration suite.



## Function: _ensure_initialized

**Parameters**: self
**Returns**: None
**Description**: Lazy initialization of healing strategies.



## Function: run_strategy

**Parameters**: self, strategy_name, violation, context
**Returns**: HealingResult
**Description**: 
        Run a specific healing strategy.

        Args:
            strategy_name: Name of the strategy to run
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingResult with healing details
        



## Function: run_all

**Parameters**: self, violation, context
**Returns**: HealingSuiteResult
**Description**: 
        Run all applicable healing strategies for a violation.

        Args:
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingSuiteResult with aggregated results
        



## Function: run_resilience_check

**Parameters**: self, context
**Returns**: HealingResult
**Description**: 
        Run chaos resilience check specifically.

        Args:
            context: Optional healing context

        Returns:
            HealingResult from chaos resilience strategy
        



## Function: run_dependency_cleanup

**Parameters**: self, dry_run, context
**Returns**: HealingResult
**Description**: 
        Run dependency pruning specifically.

        Args:
            dry_run: If True, only report what would be done
            context: Optional additional context

        Returns:
            HealingResult from dependency pruning strategy
        



## Function: get_available_strategies

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available strategy names.



## Function: get_status

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current status of the healing suite.



## Usage Examples

### Class Usage

```python
# Using HealingResult
healingresult = HealingResult()
```

```python
# Using HealingSuiteResult
healingsuiteresult = HealingSuiteResult()
```

```python
# Using HealingOrchestrationSuite
healingorchestrationsuite = HealingOrchestrationSuite()
healingorchestrationsuite.run_strategy()
healingorchestrationsuite.run_all()
```

### Function Usage

```python
# Using get_healing_suite
result = get_healing_suite()
```

```python
# Using run_healing_operation
result = run_healing_operation(violation, context)
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:05.508899
**Type**: api_reference
**Quality**: comprehensive
