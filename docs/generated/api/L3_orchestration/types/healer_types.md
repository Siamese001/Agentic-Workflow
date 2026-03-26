# API Documentation: healer_types

**Target Audience**: developers, api_users

# healer_types API Documentation

**File**: `healer_types.py`
**Classes**: 2
**Functions**: 4

## Classes

- **IHealerProtocol** (inherits from Protocol)
- **LegacyAgentAdapter**

## Functions

- **heal** -> dict[str, Any]
- **__init__**
- **heal** -> dict[str, Any]
- **_wrap_legacy_result** -> dict[str, Any]


## Class: IHealerProtocol

**Description**: The strict interface Phase 2 expects.

**Inherits from**: Protocol

### Methods

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: Ellipsis



## Class: LegacyAgentAdapter

**Description**: 
    Universal Wrapper for LEGACY agents.
    Translates 'heal(violation)' calls into whatever method the legacy agent has.
    

### Methods

#### __init__
**Parameters**: self, legacy_agent

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Smartly routes the heal request to known legacy signatures.
        

#### _wrap_legacy_result
**Parameters**: self, result
**Returns**: dict[str, Any]
**Description**: Converts arbitrary legacy returns (bools, strings, lists) to SSOT Schema.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: Ellipsis



## Function: __init__

**Parameters**: self, legacy_agent


## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Smartly routes the heal request to known legacy signatures.
        



## Function: _wrap_legacy_result

**Parameters**: self, result
**Returns**: dict[str, Any]
**Description**: Converts arbitrary legacy returns (bools, strings, lists) to SSOT Schema.



## Usage Examples

### Class Usage

```python
# Using IHealerProtocol
ihealerprotocol = IHealerProtocol()
ihealerprotocol.heal()
```

```python
# Using LegacyAgentAdapter
legacyagentadapter = LegacyAgentAdapter()
legacyagentadapter.heal()
```

### Function Usage

```python
# Using heal
result = heal(violation)
```

```python
# Using __init__
result = __init__(legacy_agent)
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:04.381151
**Type**: api_reference
**Quality**: comprehensive
