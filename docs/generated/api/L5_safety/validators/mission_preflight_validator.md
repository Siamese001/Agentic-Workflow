# API Documentation: mission_preflight_validator

**Target Audience**: developers, api_users

# mission_preflight_validator API Documentation

**File**: `mission_preflight_validator.py`
**Classes**: 1
**Functions**: 10

## Classes

- **MissionPreflight**

## Functions

- **__init__**
- **_get_location_agent**
- **_get_hierarchy_agent**
- **_get_import_agent**
- **run_preflight** -> dict[str, Any]
- **_check_span_of_two** -> int
- **_check_hierarchy** -> list[tuple[Path, str]]
- **_check_gravity** -> int
- **_check_file_locations** -> int
- **_print_dashboard** -> None


## Class: MissionPreflight

**Description**: 
    L5 Mission Preflight Validator

    Integrates Void Compliance into the Master Validation Sweep.
    Executes pre-flight checks before any validation begins.
    

### Methods

#### __init__
**Parameters**: self, project_root, healing_enabled
**Description**: 
        Initialize the preflight validator.

        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled
        

#### _get_location_agent
**Parameters**: self
**Description**: Lazy load LocationAgent.

#### _get_hierarchy_agent
**Parameters**: self
**Description**: Lazy load HierarchyAgent.

#### _get_import_agent
**Parameters**: self
**Description**: Lazy load import healer.

#### run_preflight
**Parameters**: self, target_sector
**Returns**: dict[str, Any]
**Description**: 
        Execute the full preflight compliance check.

        Args:
            target_sector: Path to the target sector for validation

        Returns:
            Dict with compliance results and Violation counts
        

#### _check_span_of_two
**Parameters**: self, target_path
**Returns**: int
**Description**: Check Span-of-Two compliance using HierarchyAgent.

#### _check_hierarchy
**Parameters**: self, target_path
**Returns**: list[tuple[Path, str]]
**Description**: Check hierarchy alignment using HierarchyAgent.

#### _check_gravity
**Parameters**: self, target_path
**Returns**: int
**Description**: Check import waterfall violations.

#### _check_file_locations
**Parameters**: self, target_path
**Returns**: int
**Description**: Check file location validation.

#### _print_dashboard
**Parameters**: self, results
**Returns**: None
**Description**: Print the sovereignty dashboard.



## Function: __init__

**Parameters**: self, project_root, healing_enabled
**Description**: 
        Initialize the preflight validator.

        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled
        



## Function: _get_location_agent

**Parameters**: self
**Description**: Lazy load LocationAgent.



## Function: _get_hierarchy_agent

**Parameters**: self
**Description**: Lazy load HierarchyAgent.



## Function: _get_import_agent

**Parameters**: self
**Description**: Lazy load import healer.



## Function: run_preflight

**Parameters**: self, target_sector
**Returns**: dict[str, Any]
**Description**: 
        Execute the full preflight compliance check.

        Args:
            target_sector: Path to the target sector for validation

        Returns:
            Dict with compliance results and Violation counts
        



## Function: _check_span_of_two

**Parameters**: self, target_path
**Returns**: int
**Description**: Check Span-of-Two compliance using HierarchyAgent.



## Function: _check_hierarchy

**Parameters**: self, target_path
**Returns**: list[tuple[Path, str]]
**Description**: Check hierarchy alignment using HierarchyAgent.



## Function: _check_gravity

**Parameters**: self, target_path
**Returns**: int
**Description**: Check import waterfall violations.



## Function: _check_file_locations

**Parameters**: self, target_path
**Returns**: int
**Description**: Check file location validation.



## Function: _print_dashboard

**Parameters**: self, results
**Returns**: None
**Description**: Print the sovereignty dashboard.



## Usage Examples

### Class Usage

```python
# Using MissionPreflight
missionpreflight = MissionPreflight()
missionpreflight.run_preflight()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, healing_enabled)
```

```python
# Using _get_location_agent
result = _get_location_agent()
```

```python
# Using _get_hierarchy_agent
result = _get_hierarchy_agent()
```



---
**Generated**: 2026-03-26T09:39:05.850937
**Type**: api_reference
**Quality**: comprehensive
