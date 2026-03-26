# API Documentation: CodeEnforcerAgent

**Target Audience**: developers, api_users

# CodeEnforcerAgent API Documentation

**File**: `CodeEnforcerAgent.py`
**Classes**: 6
**Functions**: 20

## Classes

- **EnforcementType** (inherits from Enum)
- **ViolationSeverity** (inherits from Enum)
- **CodeViolation**
- **SignedException**
- **EnforcementConfig**
- **CodeEnforcerAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_legacy_ssot_enforcer** -> CodeEnforcerAgent
- **create_legacy_standards_enforcer** -> CodeEnforcerAgent
- **create_legacy_sovereignty_enforcer** -> CodeEnforcerAgent
- **heal_repository** -> dict[str, Any]
- **__init__**
- **validate_file** -> list[CodeViolation]
- **_check_standards** -> list[CodeViolation]
- **_check_patterns** -> list[CodeViolation]
- **_check_type_hints** -> list[CodeViolation]
- **_check_sovereignty_violations** -> list[CodeViolation]
- **_extract_layer** -> str | None
- **_extract_layer_from_import** -> str | None
- **_is_sovereignty_violation** -> bool
- **check_sovereignty** -> tuple[bool, str]
- **grant_exception** -> SignedException
- **sync_ssot_registry** -> dict[str, Any]
- **update_ssot_registry** -> bool
- **get_violations** -> list[CodeViolation]
- **heal** -> dict
- **_heal_enforcement_violation** -> dict


## Class: EnforcementType

**Description**: Types of code enforcement.

**Inherits from**: Enum



## Class: ViolationSeverity

**Description**: Severity levels for violations.

**Inherits from**: Enum



## Class: CodeViolation

**Description**: Represents a code violation.



## Class: SignedException

**Description**: Signed exception for cross-layer access.



## Class: EnforcementConfig

**Description**: configuration for code enforcement.



## Class: CodeEnforcerAgent

**Description**: 
    Unified code enforcement with sovereignty protection.

    Consolidates:
    - CodeSSOTEnforcerAgent (SSOT sync)
    - CodeStandardsEnforcerAgent (standards)
    - PatternEnforcerAgent (patterns)
    - TypeEnforcerAgent (type hints)
    - PythonFileSovereigntyEnforcerAgent (sovereignty)

    Usage:
        enforcer = CodeEnforcerAgent()

        # Validate a file
        violations = enforcer.validate_file(Path("my_agent.py"))

        # Check sovereignty
        can_modify = enforcer.check_sovereignty("L3", Path("L5/agent.py"))

        # Sync SSOT
        enforcer.sync_ssot_registry()
    

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
**Returns**: list[CodeViolation]
**Description**: Validate a file for all enforcement types.

#### _check_standards
**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check code standards compliance.

#### _check_patterns
**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check for forbidden patterns.

#### _check_type_hints
**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check for type hint compliance.

#### _check_sovereignty_violations
**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check for sovereignty violations (cross-layer access).

#### _extract_layer
**Parameters**: self, path
**Returns**: str | None
**Description**: Extract layer from file path.

#### _extract_layer_from_import
**Parameters**: self, node
**Returns**: str | None
**Description**: Extract layer from import statement.

#### _is_sovereignty_violation
**Parameters**: self, source_layer, target_layer
**Returns**: bool
**Description**: Check if import violates sovereignty rules.

#### check_sovereignty
**Parameters**: self, source_layer, target_file, agent_id
**Returns**: tuple[bool, str]
**Description**: 
        Check if a layer can modify a target file.

        Args:
            source_layer: Layer attempting modification (e.g., "L3")
            target_file: File being modified
            agent_id: Optional agent ID for exception checking

        Returns:
            Tuple of (allowed, reason)
        

#### grant_exception
**Parameters**: self, source_layer, target_file, granted_by, reason, expires_at
**Returns**: SignedException
**Description**: Grant a signed exception for cross-layer access.

#### sync_ssot_registry
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Synchronize with SSOT registry.

#### update_ssot_registry
**Parameters**: self, updates
**Returns**: bool
**Description**: Update SSOT registry with changes.

#### get_violations
**Parameters**: self
**Returns**: list[CodeViolation]
**Description**: Get all recorded violations.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal code enforcement violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (ssot, naming, import, structure)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: create_legacy_ssot_enforcer

**Returns**: CodeEnforcerAgent
**Description**: Create enforcer for SSOT sync.



## Function: create_legacy_standards_enforcer

**Returns**: CodeEnforcerAgent
**Description**: Create enforcer for code standards.



## Function: create_legacy_sovereignty_enforcer

**Returns**: CodeEnforcerAgent
**Description**: Create enforcer for file sovereignty.



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
**Returns**: list[CodeViolation]
**Description**: Validate a file for all enforcement types.



## Function: _check_standards

**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check code standards compliance.



## Function: _check_patterns

**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check for forbidden patterns.



## Function: _check_type_hints

**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check for type hint compliance.



## Function: _check_sovereignty_violations

**Parameters**: self, file_path, content
**Returns**: list[CodeViolation]
**Description**: Check for sovereignty violations (cross-layer access).



## Function: _extract_layer

**Parameters**: self, path
**Returns**: str | None
**Description**: Extract layer from file path.



## Function: _extract_layer_from_import

**Parameters**: self, node
**Returns**: str | None
**Description**: Extract layer from import statement.



## Function: _is_sovereignty_violation

**Parameters**: self, source_layer, target_layer
**Returns**: bool
**Description**: Check if import violates sovereignty rules.



## Function: check_sovereignty

**Parameters**: self, source_layer, target_file, agent_id
**Returns**: tuple[bool, str]
**Description**: 
        Check if a layer can modify a target file.

        Args:
            source_layer: Layer attempting modification (e.g., "L3")
            target_file: File being modified
            agent_id: Optional agent ID for exception checking

        Returns:
            Tuple of (allowed, reason)
        



## Function: grant_exception

**Parameters**: self, source_layer, target_file, granted_by, reason, expires_at
**Returns**: SignedException
**Description**: Grant a signed exception for cross-layer access.



## Function: sync_ssot_registry

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Synchronize with SSOT registry.



## Function: update_ssot_registry

**Parameters**: self, updates
**Returns**: bool
**Description**: Update SSOT registry with changes.



## Function: get_violations

**Parameters**: self
**Returns**: list[CodeViolation]
**Description**: Get all recorded violations.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal code enforcement violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (ssot, naming, import, structure)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: _heal_enforcement_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Internal heal method with standard_heal decorator.



## Usage Examples

### Class Usage

```python
# Using EnforcementType
enforcementtype = EnforcementType()
```

```python
# Using ViolationSeverity
violationseverity = ViolationSeverity()
```

```python
# Using CodeViolation
codeviolation = CodeViolation()
```

### Function Usage

```python
# Using create_legacy_ssot_enforcer
result = create_legacy_ssot_enforcer()
```

```python
# Using create_legacy_standards_enforcer
result = create_legacy_standards_enforcer()
```

```python
# Using create_legacy_sovereignty_enforcer
result = create_legacy_sovereignty_enforcer()
```



---
**Generated**: 2026-03-26T09:39:05.081756
**Type**: api_reference
**Quality**: comprehensive
