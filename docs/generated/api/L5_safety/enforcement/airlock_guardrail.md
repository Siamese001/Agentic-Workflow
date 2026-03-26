# API Documentation: airlock_guardrail

**Target Audience**: developers, api_users

# airlock_guardrail API Documentation

**File**: `airlock_guardrail.py`
**Classes**: 1
**Functions**: 2

## Classes

- **AirlockProtocol**

## Functions

- **__init__**
- **_validate_risk_parameters** -> bool


## Class: AirlockProtocol

**Description**: 
    L5 Safety Guardrail: The Execution Airlock.
    Validates tool calls against a mission-specific Permission matrix.
    

### Methods

#### __init__
**Parameters**: self, config

#### _validate_risk_parameters
**Parameters**: self, tool, args
**Returns**: bool



## Function: __init__

**Parameters**: self, config


## Function: _validate_risk_parameters

**Parameters**: self, tool, args
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using AirlockProtocol
airlockprotocol = AirlockProtocol()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using _validate_risk_parameters
result = _validate_risk_parameters(tool, args)
```



---
**Generated**: 2026-03-26T09:39:04.766882
**Type**: api_reference
**Quality**: comprehensive
