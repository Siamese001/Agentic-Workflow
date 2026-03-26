# API Documentation: DependencyPruningAgent

**Target Audience**: developers, api_users

# DependencyPruningAgent API Documentation

**File**: `DependencyPruningAgent.py`
**Classes**: 1
**Functions**: 5

## Classes

- **DependencyPruningAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **_find_unused_deptry** -> list[str]
- **_remove_from_requirements_txt** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **heal** -> dict


## Class: DependencyPruningAgent

**Description**: L5 Safety agent that detects and removes unused Python dependencies.

    This batch agent uses 'deptry' for accurate AST-based detection of unused
    dependencies and can remove them from requirements.txt.

    Attributes:
        project_root: Root directory of the project.
        ctx: Execution context with reporting capabilities.
        dry_run: If True, only report what would be removed (default: True).
        requirements_path: Path to requirements.txt file.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: Initialize the dependency pruning agent.

        Args:
            project_root: Root directory of the project.
            ctx: Execution context with optional report() method.
        

#### _find_unused_deptry
**Parameters**: self
**Returns**: list[str]
**Description**: Use deptry to find unused dependencies via AST analysis.

        Returns:
            List of unused package names, empty if deptry fails or not installed.
        

#### _remove_from_requirements_txt
**Parameters**: self, unused
**Returns**: dict[str, Any]
**Description**: Remove unused packages from requirements.txt.

        Args:
            unused: List of package names to remove.

        Returns:
            Dictionary with removal results:
                - removed: Count of packages removed
                - file: Name of the modified file
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal dependency pruning violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (unused_dependency)
                - package: Name of the unused package
                - path: Path to requirements.txt

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __init__

**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: Initialize the dependency pruning agent.

        Args:
            project_root: Root directory of the project.
            ctx: Execution context with optional report() method.
        



## Function: _find_unused_deptry

**Parameters**: self
**Returns**: list[str]
**Description**: Use deptry to find unused dependencies via AST analysis.

        Returns:
            List of unused package names, empty if deptry fails or not installed.
        



## Function: _remove_from_requirements_txt

**Parameters**: self, unused
**Returns**: dict[str, Any]
**Description**: Remove unused packages from requirements.txt.

        Args:
            unused: List of package names to remove.

        Returns:
            Dictionary with removal results:
                - removed: Count of packages removed
                - file: Name of the modified file
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal dependency pruning violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (unused_dependency)
                - package: Name of the unused package
                - path: Path to requirements.txt

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using DependencyPruningAgent
dependencypruningagent = DependencyPruningAgent()
dependencypruningagent.heal_repository()
dependencypruningagent.heal()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, ctx)
```

```python
# Using _find_unused_deptry
result = _find_unused_deptry()
```

```python
# Using _remove_from_requirements_txt
result = _remove_from_requirements_txt(unused)
```



---
**Generated**: 2026-03-26T09:39:05.123046
**Type**: api_reference
**Quality**: comprehensive
