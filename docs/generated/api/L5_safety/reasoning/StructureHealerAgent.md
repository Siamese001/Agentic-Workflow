# API Documentation: StructureHealerAgent

**Target Audience**: developers, api_users

# StructureHealerAgent API Documentation

**File**: `StructureHealerAgent.py`
**Classes**: 4
**Functions**: 20

## Classes

- **StructureHealingType** (inherits from Enum)
- **StructureHealingAction**
- **StructureHealerConfig**
- **StructureHealerAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_legacy_gravity_healer** -> StructureHealerAgent
- **create_legacy_naming_healer** -> StructureHealerAgent
- **__init__**
- **heal_repository** -> dict[str, Any]
- **heal_all** -> list[StructureHealingAction]
- **heal_naming** -> list[StructureHealingAction]
- **heal_gravity** -> list[StructureHealingAction]
- **heal_territory** -> list[StructureHealingAction]
- **_extract_layer** -> str | None
- **_extract_layer_from_module** -> str | None
- **_is_valid_gravity** -> bool
- **_backup_file** -> Path | None
- **get_actions** -> list[StructureHealingAction]
- **heal** -> dict
- **_heal_gravity_violation** -> dict
- **_heal_hierarchy_violation** -> dict
- **_heal_naming_violation** -> dict
- **_heal_territory_violation** -> dict
- **_heal_blueprint_violation** -> dict
- **_heal_structure_violation** -> dict


## Class: StructureHealingType

**Description**: Types of structure healing.

**Inherits from**: Enum



## Class: StructureHealingAction

**Description**: Represents a structure healing action.



## Class: StructureHealerConfig

**Description**: configuration for structure healing.



## Class: StructureHealerAgent

**Description**: 
    Unified structure healer for gravity, hierarchy, naming, and territory.

    FACADE SHELL: Delegates to UnifiedAgent with StructureHealingStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.

    Consolidates:
    - GravityHealerAgent
    - HierarchyHealerAgent
    - NamingLawHealerAgent
    - TerritoryHealerAgent
    - BlueprintHierarchyHealerAgent

    Usage:
        healer = StructureHealerAgent()

        # Heal naming violations
        actions = healer.heal_naming(Path("BadName.py"))

        # Heal all structure issues
        actions = healer.heal_all(Path("my_agent.py"))
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, agent_config

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Wraps heal_all to provide the standard Sovereign interface.
        

#### heal_all
**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Run all enabled healing on a file.

#### heal_naming
**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Heal naming convention violations.

#### heal_gravity
**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Heal gravity (layer import) violations.

#### heal_territory
**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Heal territory/location violations.

#### _extract_layer
**Parameters**: self, path
**Returns**: str | None
**Description**: Extract layer from file path.

#### _extract_layer_from_module
**Parameters**: self, module
**Returns**: str | None
**Description**: Extract layer from module name.

#### _is_valid_gravity
**Parameters**: self, source_layer, target_layer
**Returns**: bool
**Description**: Check if import follows gravity rules.

#### _backup_file
**Parameters**: self, file_path
**Returns**: Path | None
**Description**: Create backup before healing.

#### get_actions
**Parameters**: self
**Returns**: list[StructureHealingAction]
**Description**: Get all recorded healing actions.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structure violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, hierarchy, naming, territory, blueprint)
                - path: Path to the violating file
                - severity: Severity level of the violation
                - line_number: Line number of the violation (if applicable)

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        

#### _heal_gravity_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal gravity violations.

#### _heal_hierarchy_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal hierarchy violations.

#### _heal_naming_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal naming violations.

#### _heal_territory_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal territory violations.

#### _heal_blueprint_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal blueprint violations.



## Function: create_legacy_gravity_healer

**Returns**: StructureHealerAgent
**Description**: Create healer for gravity only.



## Function: create_legacy_naming_healer

**Returns**: StructureHealerAgent
**Description**: Create healer for naming only.



## Function: __init__

**Parameters**: self, project_root, agent_config


## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Wraps heal_all to provide the standard Sovereign interface.
        



## Function: heal_all

**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Run all enabled healing on a file.



## Function: heal_naming

**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Heal naming convention violations.



## Function: heal_gravity

**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Heal gravity (layer import) violations.



## Function: heal_territory

**Parameters**: self, file_path
**Returns**: list[StructureHealingAction]
**Description**: Heal territory/location violations.



## Function: _extract_layer

**Parameters**: self, path
**Returns**: str | None
**Description**: Extract layer from file path.



## Function: _extract_layer_from_module

**Parameters**: self, module
**Returns**: str | None
**Description**: Extract layer from module name.



## Function: _is_valid_gravity

**Parameters**: self, source_layer, target_layer
**Returns**: bool
**Description**: Check if import follows gravity rules.



## Function: _backup_file

**Parameters**: self, file_path
**Returns**: Path | None
**Description**: Create backup before healing.



## Function: get_actions

**Parameters**: self
**Returns**: list[StructureHealingAction]
**Description**: Get all recorded healing actions.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structure violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, hierarchy, naming, territory, blueprint)
                - path: Path to the violating file
                - severity: Severity level of the violation
                - line_number: Line number of the violation (if applicable)

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: _heal_gravity_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal gravity violations.



## Function: _heal_hierarchy_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal hierarchy violations.



## Function: _heal_naming_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal naming violations.



## Function: _heal_territory_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal territory violations.



## Function: _heal_blueprint_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal blueprint violations.



## Function: _heal_structure_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Internal heal method with standard_heal decorator.



## Usage Examples

### Class Usage

```python
# Using StructureHealingType
structurehealingtype = StructureHealingType()
```

```python
# Using StructureHealingAction
structurehealingaction = StructureHealingAction()
```

```python
# Using StructureHealerConfig
structurehealerconfig = StructureHealerConfig()
```

### Function Usage

```python
# Using create_legacy_gravity_healer
result = create_legacy_gravity_healer()
```

```python
# Using create_legacy_naming_healer
result = create_legacy_naming_healer()
```

```python
# Using __init__
result = __init__(project_root, agent_config)
```



---
**Generated**: 2026-03-26T09:39:05.428911
**Type**: api_reference
**Quality**: comprehensive
