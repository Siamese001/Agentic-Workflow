# API Documentation: code_tool_runner_core_util

**Target Audience**: developers, api_users

# code_tool_runner_core_util API Documentation

**File**: `code_tool_runner_core_util.py`
**Classes**: 1
**Functions**: 2

## Classes

- **CodeToolRunnerCapability**

## Functions

- **heal_repository** -> dict[str, int]
- **heal** -> dict


## Class: CodeToolRunnerCapability

**Description**: Pure capability mixin for L5 code-tool-runner agents.

    Provides:
        - heal_repository() with cycle-detection and depth-limiting
        - heal() template that delegates to execute()

    Expects the consuming dataclass to provide:
        - self.project_root: Path
        - self.ctx: Any

    Subclasses MUST implement:
        - execute(file_path: str) -> dict[str, Any]
    

### Methods

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
**Description**: Heal violations using standard_heal decorator pattern.

        Delegates to execute() for the actual tool invocation.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation
                - path: Path to the violating file

        Returns:
            Dictionary with healing results following standard_heal format.
        



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
**Description**: Heal violations using standard_heal decorator pattern.

        Delegates to execute() for the actual tool invocation.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation
                - path: Path to the violating file

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using CodeToolRunnerCapability
codetoolrunnercapability = CodeToolRunnerCapability()
codetoolrunnercapability.heal_repository()
codetoolrunnercapability.heal()
```

### Function Usage

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:05.618838
**Type**: api_reference
**Quality**: comprehensive
