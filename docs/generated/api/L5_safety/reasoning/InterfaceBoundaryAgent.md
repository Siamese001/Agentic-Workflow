# API Documentation: InterfaceBoundaryAgent

**Target Audience**: developers, api_users

# InterfaceBoundaryAgent API Documentation

**File**: `InterfaceBoundaryAgent.py`
**Classes**: 1
**Functions**: 7

## Classes

- **InterfaceBoundaryAgent** (inherits from SovereignBaseAgent)

## Functions

- **heal_repository** -> dict[str, Any]
- **__init__** -> None
- **audit_boundaries** -> list[dict]
- **_analyze_file_complexity** -> dict
- **generate_interface_stub** -> str
- **report** -> Any
- **heal** -> dict[str, Any]


## Class: InterfaceBoundaryAgent

**Description**: 
    The Architect Agent.
    Prevents L0 utilities from polluting the upper layers by enforcing interface boundaries.
    

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
**Parameters**: self, root_dir, complexity_threshold
**Returns**: None
**Description**: Initialize the instance.

#### audit_boundaries
**Parameters**: self
**Returns**: list[dict]
**Description**: Scans L0 for complexity violations and upward leakage potential.

#### _analyze_file_complexity
**Parameters**: self, file_path
**Returns**: dict
**Description**: Uses AST to count classes and methods within a utility file.

#### generate_interface_stub
**Parameters**: self, violation
**Returns**: str
**Description**: Creates a proposed abstract base class for a 'Heavy' L0 utility.

#### report
**Parameters**: self
**Returns**: Any
**Description**: Detailed report of required structural decoupling.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by InterfaceBoundaryAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



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

**Parameters**: self, root_dir, complexity_threshold
**Returns**: None
**Description**: Initialize the instance.



## Function: audit_boundaries

**Parameters**: self
**Returns**: list[dict]
**Description**: Scans L0 for complexity violations and upward leakage potential.



## Function: _analyze_file_complexity

**Parameters**: self, file_path
**Returns**: dict
**Description**: Uses AST to count classes and methods within a utility file.



## Function: generate_interface_stub

**Parameters**: self, violation
**Returns**: str
**Description**: Creates a proposed abstract base class for a 'Heavy' L0 utility.



## Function: report

**Parameters**: self
**Returns**: Any
**Description**: Detailed report of required structural decoupling.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by InterfaceBoundaryAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Usage Examples

### Class Usage

```python
# Using InterfaceBoundaryAgent
interfaceboundaryagent = InterfaceBoundaryAgent()
interfaceboundaryagent.heal_repository()
interfaceboundaryagent.audit_boundaries()
```

### Function Usage

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using __init__
result = __init__(root_dir, complexity_threshold)
```

```python
# Using audit_boundaries
result = audit_boundaries()
```



---
**Generated**: 2026-03-26T09:39:05.285111
**Type**: api_reference
**Quality**: comprehensive
