# API Documentation: StructureEnforcerAgent

**Target Audience**: developers, api_users

# StructureEnforcerAgent API Documentation

**File**: `StructureEnforcerAgent.py`
**Classes**: 5
**Functions**: 17

## Classes

- **StructureViolationType**
- **StructureViolation**
- **NamingRule**
- **StructureConfig**
- **StructureEnforcerAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_legacy_gravity_enforcer** -> StructureEnforcerAgent
- **create_legacy_naming_enforcer** -> StructureEnforcerAgent
- **create_legacy_doc_enforcer** -> StructureEnforcerAgent
- **heal_repository** -> dict[str, Any]
- **__init__**
- **validate_file** -> list[StructureViolation]
- **_extract_layer** -> str | None
- **_extract_layer_from_module** -> str | None
- **_check_gravity** -> list[StructureViolation]
- **_check_naming** -> list[StructureViolation]
- **_check_documentation** -> list[StructureViolation]
- **_check_ascii** -> list[StructureViolation]
- **check_gravity_import** -> tuple[bool, str]
- **force_rename_class** -> dict[str, Any]
- **validate_hierarchy** -> list[StructureViolation]
- **get_violations** -> list[StructureViolation]
- **heal** -> dict


## Class: StructureViolationType

**Description**: Types of structure violations.



## Class: StructureViolation

**Description**: Represents a structure violation.



## Class: NamingRule

**Description**: Naming convention rule.



## Class: StructureConfig

**Description**: configuration for structure enforcement.



## Class: StructureEnforcerAgent

**Description**: 
    Unified structure enforcement with gravity and naming.

    Consolidates:
    - GravityEnforcerAgent (layer imports)
    - HierarchyEnforcerAgent (hierarchy)
    - NamingEnforcerAgent (naming)
    - DocEnforcerAgent (documentation)
    - ASCIIEnforcerAgent (ASCII)
    - StrictDocEnforcerAgent (strict docs)

    Usage:
        enforcer = StructureEnforcerAgent()

        # Validate structure
        violations = enforcer.validate_file(Path("my_agent.py"))

        # Check gravity
        is_valid = enforcer.check_gravity_import("L2", "L5")

        # Force rename
        enforcer.force_rename_class(Path("BadName.py"), "BadName", "BadNameAgent")
    

**Inherits from**: SovereignBaseAgent

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self, project_root, agent_config

#### validate_file
**Parameters**: self, file_path
**Returns**: list[StructureViolation]
**Description**: Validate a file for all structure rules.

#### _extract_layer
**Parameters**: self, path
**Returns**: str | None
**Description**: Extract layer from file path.

#### _extract_layer_from_module
**Parameters**: self, module
**Returns**: str | None
**Description**: Extract layer from module name.

#### _check_gravity
**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check gravity (layer import) violations.

#### _check_naming
**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check naming convention violations.

#### _check_documentation
**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check documentation violations.

#### _check_ascii
**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check ASCII compliance.

#### check_gravity_import
**Parameters**: self, source_layer, target_layer
**Returns**: tuple[bool, str]
**Description**: 
        Check if an import from source to target layer is allowed.

        Args:
            source_layer: Layer doing the import (e.g., "L2")
            target_layer: Layer being imported (e.g., "L5")

        Returns:
            Tuple of (allowed, reason)
        

#### force_rename_class
**Parameters**: self, file_path, old_name, new_name, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Force rename a class to comply with naming conventions.

        Args:
            file_path: Path to the file
            old_name: Current class name
            new_name: New class name (should end with Agent)
            dry_run: If True, don't actually modify

        Returns:
            Result dictionary
        

#### validate_hierarchy
**Parameters**: self, file_path
**Returns**: list[StructureViolation]
**Description**: Validate file hierarchy placement.

#### get_violations
**Parameters**: self
**Returns**: list[StructureViolation]
**Description**: Get all recorded violations.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structure enforcement violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, hierarchy, naming, documentation, ascii)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: create_legacy_gravity_enforcer

**Returns**: StructureEnforcerAgent
**Description**: Create enforcer for gravity rules.



## Function: create_legacy_naming_enforcer

**Returns**: StructureEnforcerAgent
**Description**: Create enforcer for naming conventions.



## Function: create_legacy_doc_enforcer

**Returns**: StructureEnforcerAgent
**Description**: Create enforcer for documentation.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self, project_root, agent_config


## Function: validate_file

**Parameters**: self, file_path
**Returns**: list[StructureViolation]
**Description**: Validate a file for all structure rules.



## Function: _extract_layer

**Parameters**: self, path
**Returns**: str | None
**Description**: Extract layer from file path.



## Function: _extract_layer_from_module

**Parameters**: self, module
**Returns**: str | None
**Description**: Extract layer from module name.



## Function: _check_gravity

**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check gravity (layer import) violations.



## Function: _check_naming

**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check naming convention violations.



## Function: _check_documentation

**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check documentation violations.



## Function: _check_ascii

**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]
**Description**: Check ASCII compliance.



## Function: check_gravity_import

**Parameters**: self, source_layer, target_layer
**Returns**: tuple[bool, str]
**Description**: 
        Check if an import from source to target layer is allowed.

        Args:
            source_layer: Layer doing the import (e.g., "L2")
            target_layer: Layer being imported (e.g., "L5")

        Returns:
            Tuple of (allowed, reason)
        



## Function: force_rename_class

**Parameters**: self, file_path, old_name, new_name, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Force rename a class to comply with naming conventions.

        Args:
            file_path: Path to the file
            old_name: Current class name
            new_name: New class name (should end with Agent)
            dry_run: If True, don't actually modify

        Returns:
            Result dictionary
        



## Function: validate_hierarchy

**Parameters**: self, file_path
**Returns**: list[StructureViolation]
**Description**: Validate file hierarchy placement.



## Function: get_violations

**Parameters**: self
**Returns**: list[StructureViolation]
**Description**: Get all recorded violations.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structure enforcement violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, hierarchy, naming, documentation, ascii)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Usage Examples

### Class Usage

```python
# Using StructureViolationType
structureviolationtype = StructureViolationType()
```

```python
# Using StructureViolation
structureviolation = StructureViolation()
```

```python
# Using NamingRule
namingrule = NamingRule()
```

### Function Usage

```python
# Using create_legacy_gravity_enforcer
result = create_legacy_gravity_enforcer()
```

```python
# Using create_legacy_naming_enforcer
result = create_legacy_naming_enforcer()
```

```python
# Using create_legacy_doc_enforcer
result = create_legacy_doc_enforcer()
```



---
**Generated**: 2026-03-26T09:39:05.423119
**Type**: api_reference
**Quality**: comprehensive
