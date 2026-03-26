# API Documentation: DynamicSealAgent

**Target Audience**: developers, api_users

# DynamicSealAgent API Documentation

**File**: `DynamicSealAgent.py`
**Classes**: 2
**Functions**: 9

## Classes

- **SealResult**
- **DynamicSealAgent** (inherits from SovereignBaseAgent)

## Functions

- **main** -> Any
- **heal_repository** -> dict[str, Any]
- **__init__** -> None
- **heal** -> dict[str, Any]
- **execute_sprint** -> dict[str, Any]
- **_apply_seal** -> SealResult
- **_is_dynamic_import** -> bool
- **_remove_import_line** -> str
- **generate_report** -> str


## Class: SealResult

**Description**: Result of a dynamic seal operation.



## Class: DynamicSealAgent

**Description**: 
    Sovereign Agent responsible for surgical refactoring of upward dependencies.

    Capabilities:
    - Discovers import violations using UnifiedSSOTValidator
    - Applies Dynamic Seal pattern to eliminate static upward imports
    - Supports dry-run mode for safe validation
    - Provides detailed remediation reports

    Usage:
        agent = DynamicSealAgent(root_dir=".")
        results = agent.execute_sprint(target_pattern="L3 → L5", dry_run=True)
    

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
**Parameters**: self, root_dir
**Returns**: None
**Description**: Initialize the Dynamic Seal Agent.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for DynamicSealAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### execute_sprint
**Parameters**: self, target_pattern, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Execute a sprint to seal import violations.

        Args:
            target_pattern: Pattern to filter violations (e.g., "L3 → L5", "L2 → L4")
                          If None, processes all upward violations
            dry_run: If True, only reports what would be changed

        Returns:
            Dictionary with results including modified files and statistics
        

#### _apply_seal
**Parameters**: self, file_path, violations, dry_run
**Returns**: SealResult
**Description**: 
        Apply Dynamic Seal pattern to a file.

        Strategy:
        1. Identify static upward imports
        2. Remove static import lines
        3. Ensure dynamic imports exist or add lazy-loading helpers
        4. Preserve existing try/except dynamic imports
        

#### _is_dynamic_import
**Parameters**: self, content, import_line
**Returns**: bool
**Description**: Check if an import is already inside a try/except block.

#### _remove_import_line
**Parameters**: self, content, import_statement
**Returns**: str
**Description**: Remove an import statement from content.

#### generate_report
**Parameters**: self
**Returns**: str
**Description**: Generate a markdown report of sealed violations.



## Function: main

**Returns**: Any
**Description**: CLI entry point for the Dynamic Seal Agent.



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

**Parameters**: self, root_dir
**Returns**: None
**Description**: Initialize the Dynamic Seal Agent.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for DynamicSealAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: execute_sprint

**Parameters**: self, target_pattern, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Execute a sprint to seal import violations.

        Args:
            target_pattern: Pattern to filter violations (e.g., "L3 → L5", "L2 → L4")
                          If None, processes all upward violations
            dry_run: If True, only reports what would be changed

        Returns:
            Dictionary with results including modified files and statistics
        



## Function: _apply_seal

**Parameters**: self, file_path, violations, dry_run
**Returns**: SealResult
**Description**: 
        Apply Dynamic Seal pattern to a file.

        Strategy:
        1. Identify static upward imports
        2. Remove static import lines
        3. Ensure dynamic imports exist or add lazy-loading helpers
        4. Preserve existing try/except dynamic imports
        



## Function: _is_dynamic_import

**Parameters**: self, content, import_line
**Returns**: bool
**Description**: Check if an import is already inside a try/except block.



## Function: _remove_import_line

**Parameters**: self, content, import_statement
**Returns**: str
**Description**: Remove an import statement from content.



## Function: generate_report

**Parameters**: self
**Returns**: str
**Description**: Generate a markdown report of sealed violations.



## Usage Examples

### Class Usage

```python
# Using SealResult
sealresult = SealResult()
```

```python
# Using DynamicSealAgent
dynamicsealagent = DynamicSealAgent()
dynamicsealagent.heal_repository()
dynamicsealagent.heal()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using __init__
result = __init__(root_dir)
```



---
**Generated**: 2026-03-26T09:39:05.135024
**Type**: api_reference
**Quality**: comprehensive
