# API Documentation: simulation_schemas_types

**Target Audience**: developers, api_users

# simulation_schemas_types API Documentation

**File**: `simulation_schemas_types.py`
**Classes**: 2
**Functions**: 1

## Classes

- **SimScenario** (inherits from BaseModel)
- **SimOutcome** (inherits from BaseModel)

## Functions

- **validate_description** -> str


## Class: SimScenario

**Description**: Definition of a simulation scenario for system testing.

**Inherits from**: BaseModel

### Methods

#### validate_description
**Parameters**: cls, value
**Returns**: str
**Description**: [HARDENED] Ensure description is not empty.



## Class: SimOutcome

**Description**: Aggregate results from a simulation run.

**Inherits from**: BaseModel



## Function: validate_description

**Parameters**: cls, value
**Returns**: str
**Description**: [HARDENED] Ensure description is not empty.



## Usage Examples

### Class Usage

```python
# Using SimScenario
simscenario = SimScenario()
simscenario.validate_description()
```

```python
# Using SimOutcome
simoutcome = SimOutcome()
```

### Function Usage

```python
# Using validate_description
result = validate_description(cls, value)
```



---
**Generated**: 2026-03-26T09:39:05.571305
**Type**: api_reference
**Quality**: comprehensive
