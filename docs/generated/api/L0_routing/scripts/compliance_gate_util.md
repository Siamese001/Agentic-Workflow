# API Documentation: compliance_gate_util

**Target Audience**: developers, api_users

# compliance_gate_util API Documentation

**File**: `compliance_gate_util.py`
**Classes**: 1
**Functions**: 4

## Classes

- **DiscoveredAgent**

## Functions

- **_get_DiscoveredAgent**
- **check_compliance** -> list[str]
- **check_legacy_compatibility** -> dict[str, Any]
- **__init__**


## Class: DiscoveredAgent

### Methods

#### __init__
**Parameters**: self



## Function: _get_DiscoveredAgent



## Function: check_compliance

**Parameters**: discovered_agents
**Returns**: list[str]
**Description**: 
    Validates that all discovered agents conform to architectural requirements.

    Args:
        discovered_agents: List of agents discovered by AgentRegistry

    Returns:
        List of violation descriptions (empty if all compliant)
    



## Function: check_legacy_compatibility

**Returns**: dict[str, Any]
**Description**: 
    Legacy compatibility check for older agent formats.
    This function ensures backward compatibility during migration.

    Returns:
        Dict containing compatibility status and recommendations
    



## Function: __init__

**Parameters**: self


## Usage Examples

### Class Usage

```python
# Using DiscoveredAgent
discoveredagent = DiscoveredAgent()
```

### Function Usage

```python
# Using _get_DiscoveredAgent
result = _get_DiscoveredAgent()
```

```python
# Using check_compliance
result = check_compliance(discovered_agents)
```

```python
# Using check_legacy_compatibility
result = check_legacy_compatibility()
```



---
**Generated**: 2026-03-26T09:39:02.829364
**Type**: api_reference
**Quality**: comprehensive
