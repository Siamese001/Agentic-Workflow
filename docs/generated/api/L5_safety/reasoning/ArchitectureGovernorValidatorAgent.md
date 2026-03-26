# API Documentation: ArchitectureGovernorValidatorAgent

**Target Audience**: developers, api_users

# ArchitectureGovernorValidatorAgent API Documentation

**File**: `ArchitectureGovernorValidatorAgent.py`
**Classes**: 1
**Functions**: 4

## Classes

- **ArchitectureGovernorValidatorAgent**

## Functions

- **__init__** -> None
- **scan** -> dict[str, Any]
- **to_check_dict** -> dict[str, Any]
- **run** -> dict[str, Any]


## Class: ArchitectureGovernorValidatorAgent

**Description**: L5 Certify-only validator for architectural governance.

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### scan
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Run ArchitectureGovernorAgent.heal_repository in dry-run mode.

        Args:
            target_territory: Optional territory to scope the scan.

        Returns:
            Raw governance report dict from heal_repository(dry_run=True).
        

#### to_check_dict
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.

#### run
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: scan

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Run ArchitectureGovernorAgent.heal_repository in dry-run mode.

        Args:
            target_territory: Optional territory to scope the scan.

        Returns:
            Raw governance report dict from heal_repository(dry_run=True).
        



## Function: to_check_dict

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.



## Function: run

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Usage Examples

### Class Usage

```python
# Using ArchitectureGovernorValidatorAgent
architecturegovernorvalidatoragent = ArchitectureGovernorValidatorAgent()
architecturegovernorvalidatoragent.scan()
architecturegovernorvalidatoragent.to_check_dict()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using scan
result = scan(target_territory)
```

```python
# Using to_check_dict
result = to_check_dict(target_territory)
```



---
**Generated**: 2026-03-26T09:39:05.044410
**Type**: api_reference
**Quality**: comprehensive
