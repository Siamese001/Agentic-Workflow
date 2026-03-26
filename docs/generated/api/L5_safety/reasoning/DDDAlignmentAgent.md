# API Documentation: DDDAlignmentAgent

**Target Audience**: developers, api_users

# DDDAlignmentAgent API Documentation

**File**: `DDDAlignmentAgent.py`
**Classes**: 4
**Functions**: 12

## Classes

- **DDDViolation**
- **DDDAlignmentAgent** (inherits from SovereignBaseAgent)
- **MCPHardenedMixin**
- **SubatomicTestingMixin**

## Functions

- **validate_ddd_alignment** -> tuple[float, list[str]]
- **__str__** -> str
- **__post_init__**
- **heal** -> dict[str, Any]
- **_get_file_context** -> str | None
- **_is_allowed_import** -> bool
- **_check_file_imports** -> list[DDDViolation]
- **_should_skip_path** -> bool
- **run** -> list[DDDViolation]
- **get_alignment_score** -> float
- **get_violation_summary** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]


## Class: DDDViolation

**Description**: Structured DDD violation for reporting.

### Methods

#### __str__
**Parameters**: self
**Returns**: str



## Class: DDDAlignmentAgent

**Description**: 
    Domain-Driven Design Alignment Agent.

    Enforces bounded context boundaries to prevent cross-context coupling.

    DETECTION:
    - Scans all Python files for imports
    - Identifies the bounded context of each file
    - Detects imports from other bounded contexts
    - Allows imports from SharedContracts and interface modules

    HEALING:
    - Reports violations (no auto-fix - requires manual refactoring)
    - Suggests using dependency inversion via interfaces

    KEYS: Architectural integrity, DDD, bounded contexts
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for DDDAlignmentAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### _get_file_context
**Parameters**: self, filepath
**Returns**: str | None
**Description**: Determine which bounded context a file belongs to.

#### _is_allowed_import
**Parameters**: self, module, source_context
**Returns**: bool
**Description**: Check if an import is allowed (stdlib, same context, or interface).

#### _check_file_imports
**Parameters**: self, filepath
**Returns**: list[DDDViolation]
**Description**: Check a single file for DDD violations.

#### _should_skip_path
**Parameters**: self, path
**Returns**: bool
**Description**: Check if a path should be skipped.

#### run
**Parameters**: self, target_dir
**Returns**: list[DDDViolation]
**Description**: 
        Scan for DDD bounded context violations.

        Args:
            target_dir: Directory to scan (defaults to project_root)

        Returns:
            List of DDDViolation objects
        

#### get_alignment_score
**Parameters**: self
**Returns**: float
**Description**: Calculate DDD alignment score (0-100).

#### get_violation_summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get summary of violations by context pair.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Autonomous DDD alignment enforcement (Canon Key 51 compliance).

        NOTE: DDD violations cannot be auto-healed - they require manual
        refactoring to use dependency inversion via interfaces.

        Args:
            dry_run: If True, only report violations
            execute: If True, would apply fixes (not applicable for DDD)

        Returns:
            Dict with violation counts and recommendations
        



## Class: MCPHardenedMixin



## Class: SubatomicTestingMixin



## Function: validate_ddd_alignment

**Parameters**: target_dir
**Returns**: tuple[float, list[str]]
**Description**: 
    Convenience function for DDD validation.

    Args:
        target_dir: Directory to validate

    Returns:
        Tuple of (alignment_score, list of violation messages)
    



## Function: __str__

**Parameters**: self
**Returns**: str


## Function: __post_init__

**Parameters**: self


## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for DDDAlignmentAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: _get_file_context

**Parameters**: self, filepath
**Returns**: str | None
**Description**: Determine which bounded context a file belongs to.



## Function: _is_allowed_import

**Parameters**: self, module, source_context
**Returns**: bool
**Description**: Check if an import is allowed (stdlib, same context, or interface).



## Function: _check_file_imports

**Parameters**: self, filepath
**Returns**: list[DDDViolation]
**Description**: Check a single file for DDD violations.



## Function: _should_skip_path

**Parameters**: self, path
**Returns**: bool
**Description**: Check if a path should be skipped.



## Function: run

**Parameters**: self, target_dir
**Returns**: list[DDDViolation]
**Description**: 
        Scan for DDD bounded context violations.

        Args:
            target_dir: Directory to scan (defaults to project_root)

        Returns:
            List of DDDViolation objects
        



## Function: get_alignment_score

**Parameters**: self
**Returns**: float
**Description**: Calculate DDD alignment score (0-100).



## Function: get_violation_summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get summary of violations by context pair.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Autonomous DDD alignment enforcement (Canon Key 51 compliance).

        NOTE: DDD violations cannot be auto-healed - they require manual
        refactoring to use dependency inversion via interfaces.

        Args:
            dry_run: If True, only report violations
            execute: If True, would apply fixes (not applicable for DDD)

        Returns:
            Dict with violation counts and recommendations
        



## Usage Examples

### Class Usage

```python
# Using DDDViolation
dddviolation = DDDViolation()
```

```python
# Using DDDAlignmentAgent
dddalignmentagent = DDDAlignmentAgent()
dddalignmentagent.heal()
dddalignmentagent.run()
```

```python
# Using MCPHardenedMixin
mcphardenedmixin = MCPHardenedMixin()
```

### Function Usage

```python
# Using validate_ddd_alignment
result = validate_ddd_alignment(target_dir)
```

```python
# Using __str__
result = __str__()
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:05.119436
**Type**: api_reference
**Quality**: comprehensive
