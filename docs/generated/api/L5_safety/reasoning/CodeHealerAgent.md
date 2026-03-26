# API Documentation: CodeHealerAgent

**Target Audience**: developers, api_users

# CodeHealerAgent API Documentation

**File**: `CodeHealerAgent.py`
**Classes**: 5
**Functions**: 18

## Classes

- **CodeHealingStrategy** (inherits from HealingStrategy)
- **HealingType** (inherits from Enum)
- **HealingAction**
- **HealerConfig**
- **CodeHealerAgent** (inherits from PromptRenderingMixin, CircuitBreakerMixin, SurgicalCSTHealerMixin, SovereignBaseAgent)

## Functions

- **create_legacy_canon_healer** -> CodeHealerAgent
- **create_legacy_import_healer** -> CodeHealerAgent
- **__init__** -> None
- **__init__**
- **heal_repository** -> dict[str, Any]
- **atomic_write** -> bool
- **heal_all** -> list[HealingAction]
- **heal_imports** -> list[HealingAction]
- **heal_canon** -> list[HealingAction]
- **heal_structural** -> list[HealingAction]
- **_backup_file** -> Path | None
- **get_actions** -> list[HealingAction]
- **heal** -> dict
- **_heal_canon_violation** -> dict
- **_heal_import_violation** -> dict
- **_heal_structural_violation** -> dict
- **_heal_syntax_violation** -> dict
- **_heal_code_violation** -> dict


## Class: CodeHealingStrategy

**Description**: 
    Code-specific healing strategy preserving original CodeHealerAgent logic.

    FACADE PATTERN: Encapsulates the complex code healing logic while delegating
    to the unified strategy pattern.
    

**Inherits from**: HealingStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with code healing configuration.



## Class: HealingType

**Description**: Types of code healing.

**Inherits from**: Enum



## Class: HealingAction

**Description**: Represents a healing action taken.



## Class: HealerConfig

**Description**: configuration for code healing.



## Class: CodeHealerAgent

**Description**: 
    Unified code healer for canon, imports, and structure.

    V10 Refactored: Now inherits from AtomicExecutionMixin for rollback capability
    and CircuitBreakerMixin for failure isolation.

    MRO: CodeHealerAgent -> AtomicExecutionMixin -> CircuitBreakerMixin ->
         SovereignBaseAgent -> SurgicalCSTHealerMixin -> ...

    FACADE SHELL: Delegates to UnifiedAgent with CodeHealingStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.

    Consolidates:
    - CanonHealerAgent
    - ImportHealerAgent
    - StructuralHealerAgent

    Usage:
        healer = CodeHealerAgent()

        # Heal imports in a file
        actions = healer.heal_imports(Path("my_agent.py"))

        # Heal all issues
        actions = healer.heal_all(Path("my_agent.py"))
    

**Inherits from**: PromptRenderingMixin, CircuitBreakerMixin, SurgicalCSTHealerMixin, SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, agent_config

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Wraps heal_all to provide the standard Sovereign interface.
        

#### atomic_write
**Parameters**: self, file_path, new_content
**Returns**: bool
**Description**: 
        [ATOMIC SAFETY] Writes file safely using temp-swap pattern.
        

#### heal_all
**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Run all enabled healing on a file.

#### heal_imports
**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Fix broken and unused imports using CST-based surgical healing.

#### heal_canon
**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Fix canon compliance issues using CST-based surgical healing.

#### heal_structural
**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Fix structural issues using CST-based surgical healing.

#### _backup_file
**Parameters**: self, file_path
**Returns**: Path | None
**Description**: Create backup before healing.

#### get_actions
**Parameters**: self
**Returns**: list[HealingAction]
**Description**: Get all recorded healing actions.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal code violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (canon, import, structural, syntax)
                - path: Path to the violating file
                - severity: Severity level of the violation
                - line_number: Line number of the violation (if applicable)

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        

#### _heal_canon_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal canon compliance violations.

#### _heal_import_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal import violations.

#### _heal_structural_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structural violations.

#### _heal_syntax_violation
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal syntax violations.



## Function: create_legacy_canon_healer

**Returns**: CodeHealerAgent
**Description**: Create healer for canon compliance only.



## Function: create_legacy_import_healer

**Returns**: CodeHealerAgent
**Description**: Create healer for imports only.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with code healing configuration.



## Function: __init__

**Parameters**: self, project_root, agent_config


## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Wraps heal_all to provide the standard Sovereign interface.
        



## Function: atomic_write

**Parameters**: self, file_path, new_content
**Returns**: bool
**Description**: 
        [ATOMIC SAFETY] Writes file safely using temp-swap pattern.
        



## Function: heal_all

**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Run all enabled healing on a file.



## Function: heal_imports

**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Fix broken and unused imports using CST-based surgical healing.



## Function: heal_canon

**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Fix canon compliance issues using CST-based surgical healing.



## Function: heal_structural

**Parameters**: self, file_path
**Returns**: list[HealingAction]
**Description**: Fix structural issues using CST-based surgical healing.



## Function: _backup_file

**Parameters**: self, file_path
**Returns**: Path | None
**Description**: Create backup before healing.



## Function: get_actions

**Parameters**: self
**Returns**: list[HealingAction]
**Description**: Get all recorded healing actions.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal code violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (canon, import, structural, syntax)
                - path: Path to the violating file
                - severity: Severity level of the violation
                - line_number: Line number of the violation (if applicable)

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: _heal_canon_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal canon compliance violations.



## Function: _heal_import_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal import violations.



## Function: _heal_structural_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal structural violations.



## Function: _heal_syntax_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal syntax violations.



## Function: _heal_code_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Internal heal method with standard_heal decorator.



## Usage Examples

### Class Usage

```python
# Using CodeHealingStrategy
codehealingstrategy = CodeHealingStrategy()
```

```python
# Using HealingType
healingtype = HealingType()
```

```python
# Using HealingAction
healingaction = HealingAction()
```

### Function Usage

```python
# Using create_legacy_canon_healer
result = create_legacy_canon_healer()
```

```python
# Using create_legacy_import_healer
result = create_legacy_import_healer()
```

```python
# Using __init__
result = __init__(config)
```



---
**Generated**: 2026-03-26T09:39:05.090579
**Type**: api_reference
**Quality**: comprehensive
