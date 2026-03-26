# API Documentation: PascalSovereigntyAgent

**Target Audience**: developers, api_users

# PascalSovereigntyAgent API Documentation

**File**: `PascalSovereigntyAgent.py`
**Classes**: 1
**Functions**: 14

## Classes

- **PascalSovereigntyAgent** (inherits from SovereignBaseAgent)

## Functions

- **get_python_files_fast** -> list[Path]
- **main**
- **__post_init__**
- **run** -> dict[str, Any]
- **_orchestrate_audit** -> int
- **classify_file** -> FileType
- **update_imports** -> int
- **verify_environment** -> bool
- **resolve_collision_and_rename** -> bool
- **get_compliant_name** -> str | None
- **heal** -> dict
- **heal_repository** -> dict[str, int]
- **standard_heal**
- **_heal_pascal_violation** -> dict


## Class: PascalSovereigntyAgent

**Description**: 
    Enforces strict file naming conventions and resolves SSOT collisions.

    This agent canonizes the PascalSovereigntyFixer functionality as a
    first-class L5 healer agent with full orchestration capabilities.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self

#### run
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Entry point for execute_ssot.py orchestration.

#### _orchestrate_audit
**Parameters**: self, root
**Returns**: int
**Description**: Original core logic from PascalSovereigntyFixer.py.

#### classify_file
**Parameters**: self, path
**Returns**: FileType
**Description**: 
        Analyze file AST to determine architectural role with STRICT PRIORITY ORDERING.

        PRIORITY QUEUE (First Match Wins):
        1. STUB     - File contains NOT_AN_AGENT marker (MUST preempt AGENT)
        2. TEST     - Path contains tests/ OR name starts with test_
        3. PROTOCOL - Class inherits from typing.Protocol
        4. GATEWAY  - Class name contains "Gateway"
        5. ENGINE   - Path contains engines/ AND has class
        6. MIXIN    - Class name ends in "Mixin"
        7. AGENT    - Inherits *Agent OR path in agents/validators
        8. CLASS    - Any other class
        9. UTILITY  - No class definitions
        

#### update_imports
**Parameters**: self, old_name, new_name
**Returns**: int
**Description**: Refactors imports using the in-memory registry to avoid O(N²) disk hits.

#### verify_environment
**Parameters**: self
**Returns**: bool
**Description**: Checks for LongPathsEnabled on Windows.

#### resolve_collision_and_rename
**Parameters**: self, src, dest_name
**Returns**: bool
**Description**: 
        Handles renaming with intelligent collision resolution.
        Returns True if the VIOLATION was resolved (either by rename, delete, or move).
        

#### get_compliant_name
**Parameters**: self, path, file_type
**Returns**: str | None
**Description**: Calculates the target filename based on the primary class definition.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal Pascal naming violations.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, target_territory, auto_approve
**Returns**: dict[str, int]
**Description**: 
        Standard healing interface for execute_ssot.py integration.
        



## Function: get_python_files_fast

**Parameters**: root
**Returns**: list[Path]
**Description**: 
    Optimized repository scanner that prunes heavy/irrelevant directories
    before they enter the pipeline.
    



## Function: main

**Description**: Standalone execution for testing.



## Function: __post_init__

**Parameters**: self


## Function: run

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Entry point for execute_ssot.py orchestration.



## Function: _orchestrate_audit

**Parameters**: self, root
**Returns**: int
**Description**: Original core logic from PascalSovereigntyFixer.py.



## Function: classify_file

**Parameters**: self, path
**Returns**: FileType
**Description**: 
        Analyze file AST to determine architectural role with STRICT PRIORITY ORDERING.

        PRIORITY QUEUE (First Match Wins):
        1. STUB     - File contains NOT_AN_AGENT marker (MUST preempt AGENT)
        2. TEST     - Path contains tests/ OR name starts with test_
        3. PROTOCOL - Class inherits from typing.Protocol
        4. GATEWAY  - Class name contains "Gateway"
        5. ENGINE   - Path contains engines/ AND has class
        6. MIXIN    - Class name ends in "Mixin"
        7. AGENT    - Inherits *Agent OR path in agents/validators
        8. CLASS    - Any other class
        9. UTILITY  - No class definitions
        



## Function: update_imports

**Parameters**: self, old_name, new_name
**Returns**: int
**Description**: Refactors imports using the in-memory registry to avoid O(N²) disk hits.



## Function: verify_environment

**Parameters**: self
**Returns**: bool
**Description**: Checks for LongPathsEnabled on Windows.



## Function: resolve_collision_and_rename

**Parameters**: self, src, dest_name
**Returns**: bool
**Description**: 
        Handles renaming with intelligent collision resolution.
        Returns True if the VIOLATION was resolved (either by rename, delete, or move).
        



## Function: get_compliant_name

**Parameters**: self, path, file_type
**Returns**: str | None
**Description**: Calculates the target filename based on the primary class definition.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal Pascal naming violations.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, target_territory, auto_approve
**Returns**: dict[str, int]
**Description**: 
        Standard healing interface for execute_ssot.py integration.
        



## Function: standard_heal

**Parameters**: func
**Description**: Fallback decorator when full infrastructure unavailable.



## Function: _heal_pascal_violation

**Parameters**: self, violation
**Returns**: dict
**Description**: Internal heal method with standard_heal decorator.



## Usage Examples

### Class Usage

```python
# Using PascalSovereigntyAgent
pascalsovereigntyagent = PascalSovereigntyAgent()
pascalsovereigntyagent.run()
pascalsovereigntyagent.classify_file()
```

### Function Usage

```python
# Using get_python_files_fast
result = get_python_files_fast(root)
```

```python
# Using main
result = main()
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:05.343085
**Type**: api_reference
**Quality**: comprehensive
