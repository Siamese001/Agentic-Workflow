# API Documentation: StructuralValidatorAgent

**Target Audience**: developers, api_users

# StructuralValidatorAgent API Documentation

**File**: `StructuralValidatorAgent.py`
**Classes**: 4
**Functions**: 13

## Classes

- **StructureViolationType**
- **StructureViolation**
- **StructureConfig**
- **StructuralValidatorAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **config** -> StructureConfig
- **validate_structure** -> Any
- **violations** -> list[StructureViolation]
- **validate_file** -> list[StructureViolation]
- **_extract_layer** -> str | None
- **_extract_layer_from_module** -> str | None
- **_check_gravity** -> list[StructureViolation]
- **_check_naming** -> list[StructureViolation]
- **force_rename_class** -> dict[str, Any]
- **check_duplicates**
- **heal** -> dict
- **heal_repository** -> dict


## Class: StructureViolationType



## Class: StructureViolation



## Class: StructureConfig



## Class: StructuralValidatorAgent

**Description**: 
    Unified structure enforcement with gravity and naming validation.
    Hardened with Atomic Writes for auto-remediation.

    FACADE SHELL: Delegates to UnifiedAgent with StructuralValidatorStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, config

#### config
**Parameters**: self
**Returns**: StructureConfig

#### validate_structure
**Parameters**: self, target_path
**Returns**: Any
**Description**: 
        Public entry point for ArchitectureGovernorAgent.
        Returns an object with a 'violations' attribute.
        

#### violations
**Parameters**: self
**Returns**: list[StructureViolation]

#### validate_file
**Parameters**: self, file_path
**Returns**: list[StructureViolation]
**Description**: Validate a file for all structure rules.

#### _extract_layer
**Parameters**: self, path
**Returns**: str | None
**Description**: CONSOLIDATED: Delegates to shared L4 utility.

#### _extract_layer_from_module
**Parameters**: self, module
**Returns**: str | None
**Description**: CONSOLIDATED: Delegates to shared L4 utility.

#### _check_gravity
**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]

#### _check_naming
**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]

#### force_rename_class
**Parameters**: self, file_path, old_name, new_name, dry_run
**Returns**: dict[str, Any]
**Description**: Safely renames a class using Atomic Writes.

#### check_duplicates
**Parameters**: self, root

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structural validation violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (naming, import, structure)
                - path: Path to the violating file
                - old_name: Old class name (for rename operations)
                - new_name: New class name (for rename operations)

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for StructuralValidatorAgent.



## Function: __init__

**Parameters**: self, config


## Function: config

**Parameters**: self
**Returns**: StructureConfig


## Function: validate_structure

**Parameters**: self, target_path
**Returns**: Any
**Description**: 
        Public entry point for ArchitectureGovernorAgent.
        Returns an object with a 'violations' attribute.
        



## Function: violations

**Parameters**: self
**Returns**: list[StructureViolation]


## Function: validate_file

**Parameters**: self, file_path
**Returns**: list[StructureViolation]
**Description**: Validate a file for all structure rules.



## Function: _extract_layer

**Parameters**: self, path
**Returns**: str | None
**Description**: CONSOLIDATED: Delegates to shared L4 utility.



## Function: _extract_layer_from_module

**Parameters**: self, module
**Returns**: str | None
**Description**: CONSOLIDATED: Delegates to shared L4 utility.



## Function: _check_gravity

**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]


## Function: _check_naming

**Parameters**: self, file_path, content
**Returns**: list[StructureViolation]


## Function: force_rename_class

**Parameters**: self, file_path, old_name, new_name, dry_run
**Returns**: dict[str, Any]
**Description**: Safely renames a class using Atomic Writes.



## Function: check_duplicates

**Parameters**: self, root


## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structural validation violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (naming, import, structure)
                - path: Path to the violating file
                - old_name: Old class name (for rename operations)
                - new_name: New class name (for rename operations)

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for StructuralValidatorAgent.



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
# Using StructureConfig
structureconfig = StructureConfig()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using config
result = config()
```

```python
# Using validate_structure
result = validate_structure(target_path)
```



---
**Generated**: 2026-03-26T09:39:05.416748
**Type**: api_reference
**Quality**: comprehensive
