# API Documentation: GravityLeakRepairAgent

**Target Audience**: developers, api_users

# GravityLeakRepairAgent API Documentation

**File**: `GravityLeakRepairAgent.py`
**Classes**: 4
**Functions**: 21

## Classes

- **GravityRepairProhibitedError** (inherits from Exception)
- **GravityFix**
- **GravityLeakRepairAgent** (inherits from PromptRenderingMixin, SovereignBaseAgent)
- **_UsageChecker** (inherits from <ast.Attribute object at 0x000001CBFAE40DD0>)

## Functions

- **get_GravityLeakRepairAgent** -> GravityLeakRepairAgent
- **__init__** -> None
- **__init__** -> None
- **analyze_violation** -> GravityFix
- **_build_deferred_import** -> str
- **_suggest_utils_import** -> str
- **generate_fix_report** -> list[GravityFix]
- **_check_prohibition_circuit_breaker** -> None
- **_emit_plan_only** -> dict[str, Any]
- **_apply_deferred_import** -> bool
- **_apply_import_replacement_ast** -> bool
- **apply_fix** -> dict[str, Any]
- **heal_violations** -> dict
- **heal_repository** -> dict[str, Any]
- **heal** -> dict
- **_heal_gravity_violation** -> dict
- **__init__** -> None
- **visit_FunctionDef** -> None
- **visit_ClassDef** -> None
- **visit_Name** -> None
- **_in_sovereign_scope** -> bool


## Class: GravityRepairProhibitedError

**Description**: Raised when mutation prohibition blocks a gravity fix after one retry.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, file_path, layer, op
**Returns**: None



## Class: GravityFix

**Description**: Represents a gravity violation fix.



## Class: GravityLeakRepairAgent

**Description**: 
    [L5 HEALER] Automated gravity violation repair agent.

    Works in tandem with StructureEnforcerAgent to automatically fix
    upward imports and architectural violations.

    Healing Strategies:
    1. RELOCATE: Move shared code to utils/ or appropriate layer
    2. ABSTRACT: Create abstraction layer for cross-layer dependencies
    3. INJECT: Use dependency injection instead of direct imports
    4. REMOVE: Remove unnecessary imports
    

**Inherits from**: PromptRenderingMixin, SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### analyze_violation
**Parameters**: self, file_path, import_statement, file_layer, import_layer
**Returns**: GravityFix
**Description**: 
        Analyze a gravity violation and recommend a fix.

        [META-LEARNING] Enhanced with caching and pattern recall:
        - Caches AST analysis results to prevent redundant parsing
        - Recalls successful fix strategies for similar violations
        - Stores successful patterns for future use

        Args:
            file_path: File with the violation
            import_statement: The problematic import
            file_layer: Layer of the file
            import_layer: Layer being imported

        Returns:
            GravityFix with recommended solution
        

#### _build_deferred_import
**Parameters**: self, import_statement
**Returns**: str
**Description**: Return a 4-space-indented version of the import for placement inside a function body.

        The caller is responsible for finding the first function that uses the
        imported name and inserting this line at the top of that function body.
        When used via _apply_deferred_import_ast, the top-level import line is
        removed and the indented form is inserted.
        

#### _suggest_utils_import
**Parameters**: self, import_statement
**Returns**: str
**Description**: 
        Suggest a utils/ import path for relocated code.

        Args:
            import_statement: Original import statement

        Returns:
            Suggested new import path
        

#### generate_fix_report
**Parameters**: self, violations
**Returns**: list[GravityFix]
**Description**: 
        Generate fix recommendations for all violations.

        Args:
            violations: List of gravity violations from StructureEnforcerAgent

        Returns:
            List of GravityFix recommendations
        

#### _check_prohibition_circuit_breaker
**Parameters**: self, file_path, op
**Returns**: None
**Description**: Increment hit counter; raise GravityRepairProhibitedError on second hit.

#### _emit_plan_only
**Parameters**: self, fix
**Returns**: dict[str, Any]
**Description**: Emit a PLAN-ONLY artifact without attempting any write.

#### _apply_deferred_import
**Parameters**: self, file_path, import_stmt
**Returns**: bool
**Description**: Move a top-level import to inside the first function/method body that follows it.

        Uses AST to:
          1. Find the import node at module level.
          2. Collect the names it introduces.
          3. Verify ALL usages of those names are inside function/method bodies
             (not at module level) — abort if any module-level usage found.
          4. Find the first function definition that follows the import.
          5. Determine insertion line = first statement line of that function body.
          6. Rewrite file: remove original import line, insert indented import.

        Returns True if the transformation was applied, False otherwise.
        Raises ValueError on catastrophic-replace guard.
        

#### _apply_import_replacement_ast
**Parameters**: self, file_path, old_import, new_import
**Returns**: bool
**Description**: Replace exactly the matching import line(s) using line-level comparison.

        Returns True if any replacement was made, False otherwise.
        Raises ValueError if old_import is empty or a single character (catastrophic replace guard).
        

#### apply_fix
**Parameters**: self, fix, dry_run, privileged_mutation_context
**Returns**: dict[str, Any]
**Description**: 
        Apply a gravity fix to a file using Atomic Write Safety.
        Includes circuit breaker for mutation prohibition and catastrophic-replace guard.

        Wave 2: privileged_mutation_context=True bypasses L0 prohibition for approved callers
        (e.g. ops_scripts/, scripts/ that are not sovereign agents).
        

#### heal_violations
**Parameters**: self, violations
**Returns**: dict
**Description**: Pure healer: fix pre-computed gravity violations without re-scanning.

        Called by gravity_leak_healer (HEALER_REGISTRY) after GravityValidatorAgent
        has already performed the StructuralValidatorAgent scan.  This eliminates
        the duplicate scan that heal_repository() previously did internally.

        Args:
            violations: List of violation objects from StructuralValidatorAgent.
            dry_run: If True, only report fixes without applying them.

        Returns:
            Dictionary with violations_found, violations_fixed, fix_summary, status.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Canon Key 51 compliance: Detect and fix gravity violations.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking

        Returns:
            Dictionary with healing summary
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal gravity leak violations using meta-learning enhanced pattern.

        [META-LEARNING] Uses ml_enhanced_heal for:
        - Pattern recall from successful gravity fixes
        - Depth tracking to prevent infinite loops
        - Storage of successful patterns for future use

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, upward_import)
                - path: Path to the violating file
                - import_statement: The problematic import
                - file_layer: Layer of the file
                - import_layer: Layer being imported

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Class: _UsageChecker

**Inherits from**: _ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### visit_FunctionDef
**Parameters**: self, node
**Returns**: None

#### visit_ClassDef
**Parameters**: self, node
**Returns**: None

#### visit_Name
**Parameters**: self, node
**Returns**: None



## Function: get_GravityLeakRepairAgent

**Parameters**: project_root
**Returns**: GravityLeakRepairAgent
**Description**: Factory function for GravityLeakRepairAgent.



## Function: __init__

**Parameters**: self, file_path, layer, op
**Returns**: None


## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: analyze_violation

**Parameters**: self, file_path, import_statement, file_layer, import_layer
**Returns**: GravityFix
**Description**: 
        Analyze a gravity violation and recommend a fix.

        [META-LEARNING] Enhanced with caching and pattern recall:
        - Caches AST analysis results to prevent redundant parsing
        - Recalls successful fix strategies for similar violations
        - Stores successful patterns for future use

        Args:
            file_path: File with the violation
            import_statement: The problematic import
            file_layer: Layer of the file
            import_layer: Layer being imported

        Returns:
            GravityFix with recommended solution
        



## Function: _build_deferred_import

**Parameters**: self, import_statement
**Returns**: str
**Description**: Return a 4-space-indented version of the import for placement inside a function body.

        The caller is responsible for finding the first function that uses the
        imported name and inserting this line at the top of that function body.
        When used via _apply_deferred_import_ast, the top-level import line is
        removed and the indented form is inserted.
        



## Function: _suggest_utils_import

**Parameters**: self, import_statement
**Returns**: str
**Description**: 
        Suggest a utils/ import path for relocated code.

        Args:
            import_statement: Original import statement

        Returns:
            Suggested new import path
        



## Function: generate_fix_report

**Parameters**: self, violations
**Returns**: list[GravityFix]
**Description**: 
        Generate fix recommendations for all violations.

        Args:
            violations: List of gravity violations from StructureEnforcerAgent

        Returns:
            List of GravityFix recommendations
        



## Function: _check_prohibition_circuit_breaker

**Parameters**: self, file_path, op
**Returns**: None
**Description**: Increment hit counter; raise GravityRepairProhibitedError on second hit.



## Function: _emit_plan_only

**Parameters**: self, fix
**Returns**: dict[str, Any]
**Description**: Emit a PLAN-ONLY artifact without attempting any write.



## Function: _apply_deferred_import

**Parameters**: self, file_path, import_stmt
**Returns**: bool
**Description**: Move a top-level import to inside the first function/method body that follows it.

        Uses AST to:
          1. Find the import node at module level.
          2. Collect the names it introduces.
          3. Verify ALL usages of those names are inside function/method bodies
             (not at module level) — abort if any module-level usage found.
          4. Find the first function definition that follows the import.
          5. Determine insertion line = first statement line of that function body.
          6. Rewrite file: remove original import line, insert indented import.

        Returns True if the transformation was applied, False otherwise.
        Raises ValueError on catastrophic-replace guard.
        



## Function: _apply_import_replacement_ast

**Parameters**: self, file_path, old_import, new_import
**Returns**: bool
**Description**: Replace exactly the matching import line(s) using line-level comparison.

        Returns True if any replacement was made, False otherwise.
        Raises ValueError if old_import is empty or a single character (catastrophic replace guard).
        



## Function: apply_fix

**Parameters**: self, fix, dry_run, privileged_mutation_context
**Returns**: dict[str, Any]
**Description**: 
        Apply a gravity fix to a file using Atomic Write Safety.
        Includes circuit breaker for mutation prohibition and catastrophic-replace guard.

        Wave 2: privileged_mutation_context=True bypasses L0 prohibition for approved callers
        (e.g. ops_scripts/, scripts/ that are not sovereign agents).
        



## Function: heal_violations

**Parameters**: self, violations
**Returns**: dict
**Description**: Pure healer: fix pre-computed gravity violations without re-scanning.

        Called by gravity_leak_healer (HEALER_REGISTRY) after GravityValidatorAgent
        has already performed the StructuralValidatorAgent scan.  This eliminates
        the duplicate scan that heal_repository() previously did internally.

        Args:
            violations: List of violation objects from StructuralValidatorAgent.
            dry_run: If True, only report fixes without applying them.

        Returns:
            Dictionary with violations_found, violations_fixed, fix_summary, status.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Canon Key 51 compliance: Detect and fix gravity violations.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking

        Returns:
            Dictionary with healing summary
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal gravity leak violations using meta-learning enhanced pattern.

        [META-LEARNING] Uses ml_enhanced_heal for:
        - Pattern recall from successful gravity fixes
        - Depth tracking to prevent infinite loops
        - Storage of successful patterns for future use

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, upward_import)
                - path: Path to the violating file
                - import_statement: The problematic import
                - file_layer: Layer of the file
                - import_layer: Layer being imported

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: _heal_gravity_violation

**Parameters**: violation
**Returns**: dict


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: visit_FunctionDef

**Parameters**: self, node
**Returns**: None


## Function: visit_ClassDef

**Parameters**: self, node
**Returns**: None


## Function: visit_Name

**Parameters**: self, node
**Returns**: None


## Function: _in_sovereign_scope

**Parameters**: v
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using GravityRepairProhibitedError
gravityrepairprohibitederror = GravityRepairProhibitedError()
```

```python
# Using GravityFix
gravityfix = GravityFix()
```

```python
# Using GravityLeakRepairAgent
gravityleakrepairagent = GravityLeakRepairAgent()
gravityleakrepairagent.analyze_violation()
gravityleakrepairagent.generate_fix_report()
```

### Function Usage

```python
# Using get_GravityLeakRepairAgent
result = get_GravityLeakRepairAgent(project_root)
```

```python
# Using __init__
result = __init__(file_path, layer)
```

```python
# Using __init__
result = __init__(project_root)
```



---
**Generated**: 2026-03-26T09:39:05.243513
**Type**: api_reference
**Quality**: comprehensive
