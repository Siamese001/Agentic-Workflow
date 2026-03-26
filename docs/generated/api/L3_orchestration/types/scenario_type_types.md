# API Documentation: scenario_type_types

**Target Audience**: developers, api_users

# scenario_type_types API Documentation

**File**: `scenario_type_types.py`
**Classes**: 5
**Functions**: 3

## Classes

- **ScenarioType** (inherits from Enum)
- **PerformanceLevel** (inherits from Enum)
- **TrainingScenario**
- **BenchmarkResult**
- **TrainingSession**

## Functions

- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]


## Class: ScenarioType

**Description**: Types of training scenarios.

**Inherits from**: Enum



## Class: PerformanceLevel

**Description**: Performance level classifications.

**Inherits from**: Enum



## Class: TrainingScenario

**Description**: Training scenario for agent evaluation.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: BenchmarkResult

**Description**: Result from benchmark execution.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: TrainingSession

**Description**: Complete training session.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Usage Examples

### Class Usage

```python
# Using ScenarioType
scenariotype = ScenarioType()
```

```python
# Using PerformanceLevel
performancelevel = PerformanceLevel()
```

```python
# Using TrainingScenario
trainingscenario = TrainingScenario()
trainingscenario.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.416778
**Type**: api_reference
**Quality**: comprehensive
