# API Documentation: gravity_leak_validator

**Target Audience**: developers, api_users

# gravity_leak_validator API Documentation

**File**: `gravity_leak_validator.py`
**Classes**: 1
**Functions**: 3

## Classes

- **GravityLeakValidatorAgent**

## Functions

- **__init__** -> None
- **certify** -> dict[str, Any]
- **validate** -> dict[str, Any]


## Class: GravityLeakValidatorAgent

**Description**: Certify-only validator that detects gravity-leak violations without fixing them.

    Mirrors the domain of GravityLeakHealerAgent (GravityLeakRepairAgent) but
    performs NO mutations — suitable for validators/ territory.

    Usage::

        agent = GravityLeakValidatorAgent(project_root=Path("."))
        result = agent.certify()
        assert result["check_id"] == "gravity_leak"
    

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### certify
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Run a dry-run gravity-leak scan and return a check_dict.

        Returns:
            check_dict compatible with HEALER_REGISTRY dispatch:
                check_id, passed, violations_found, summary
        

#### validate
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for certify() — standard validator interface.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: certify

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Run a dry-run gravity-leak scan and return a check_dict.

        Returns:
            check_dict compatible with HEALER_REGISTRY dispatch:
                check_id, passed, violations_found, summary
        



## Function: validate

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for certify() — standard validator interface.



## Usage Examples

### Class Usage

```python
# Using GravityLeakValidatorAgent
gravityleakvalidatoragent = GravityLeakValidatorAgent()
gravityleakvalidatoragent.certify()
gravityleakvalidatoragent.validate()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using certify
result = certify()
```

```python
# Using validate
result = validate()
```



---
**Generated**: 2026-03-26T09:39:05.803660
**Type**: api_reference
**Quality**: comprehensive
