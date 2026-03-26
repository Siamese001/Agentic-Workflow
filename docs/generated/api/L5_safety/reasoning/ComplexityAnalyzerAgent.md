# API Documentation: ComplexityAnalyzerAgent

**Target Audience**: developers, api_users

# ComplexityAnalyzerAgent API Documentation

**File**: `ComplexityAnalyzerAgent.py`
**Classes**: 4
**Functions**: 7

## Classes

- **ComplexityAnalyzerStrategy** (inherits from ValidatorStrategy)
- **ComplexityViolation**
- **ComplexityConfig**
- **ComplexityAnalyzerAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **__init__**
- **analyze_repository** -> dict[str, Any]
- **analyze_file** -> list[ComplexityViolation]
- **_calculate_complexity** -> int
- **heal_repository** -> dict[str, Any]
- **heal** -> dict


## Class: ComplexityAnalyzerStrategy

**Description**: 
    Complexity analysis strategy preserving original ComplexityAnalyzerAgent logic.

    FACADE PATTERN: Encapsulates the complexity analysis logic while delegating
    to the unified strategy pattern.
    

**Inherits from**: ValidatorStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with complexity analysis configuration.



## Class: ComplexityViolation



## Class: ComplexityConfig



## Class: ComplexityAnalyzerAgent

**Description**: 
    [L5 VALIDATOR] static analysis for code complexity.
    Prevents cognitive overload and unverifiable logic.

    FACADE SHELL: Delegates to UnifiedAgent with ComplexityAnalyzerStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, config

#### analyze_repository
**Parameters**: self, target_path
**Returns**: dict[str, Any]
**Description**: Entry point for full scan.

#### analyze_file
**Parameters**: self, file_path
**Returns**: list[ComplexityViolation]
**Description**: Analyze a single file for complexity metrics.

#### _calculate_complexity
**Parameters**: self, node
**Returns**: int
**Description**: Computes McCabe Cyclomatic Complexity.

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Sovereign Interface.
        Note: Complexity cannot be auto-healed safely, only reported.
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal complexity violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (cyclomatic, length, arguments)
                - path: Path to the violating file
                - function_name: Name of the complex function

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with complexity analysis configuration.



## Function: __init__

**Parameters**: self, config


## Function: analyze_repository

**Parameters**: self, target_path
**Returns**: dict[str, Any]
**Description**: Entry point for full scan.



## Function: analyze_file

**Parameters**: self, file_path
**Returns**: list[ComplexityViolation]
**Description**: Analyze a single file for complexity metrics.



## Function: _calculate_complexity

**Parameters**: self, node
**Returns**: int
**Description**: Computes McCabe Cyclomatic Complexity.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Sovereign Interface.
        Note: Complexity cannot be auto-healed safely, only reported.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal complexity violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (cyclomatic, length, arguments)
                - path: Path to the violating file
                - function_name: Name of the complex function

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using ComplexityAnalyzerStrategy
complexityanalyzerstrategy = ComplexityAnalyzerStrategy()
```

```python
# Using ComplexityViolation
complexityviolation = ComplexityViolation()
```

```python
# Using ComplexityConfig
complexityconfig = ComplexityConfig()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using __init__
result = __init__(config)
```

```python
# Using analyze_repository
result = analyze_repository(target_path)
```



---
**Generated**: 2026-03-26T09:39:05.107907
**Type**: api_reference
**Quality**: comprehensive
