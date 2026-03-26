# API Documentation: SprawlInspectorAgent

**Target Audience**: developers, api_users

# SprawlInspectorAgent API Documentation

**File**: `SprawlInspectorAgent.py`
**Classes**: 1
**Functions**: 5

## Classes

- **SprawlInspectorAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **inspect** -> Dict[str, Any]
- **print_summary** -> None
- **heal_repository** -> dict
- **heal** -> dict[str, Any]


## Class: SprawlInspectorAgent

**Description**: 
    Sprawl Inspector - Pre-Flight Architectural Survey.

    Identifies low-density folders and excessive breadth for consolidation.
    Implements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, target_path
**Returns**: None
**Description**: 
        Initialize sprawl inspector.

        Args:
            target_path: Root directory to inspect for sprawl violations
        

#### inspect
**Parameters**: self
**Returns**: Dict[str, Any]
**Description**: 
        Scan directory tree for sprawl violations.

        Returns:
            Report dictionary with violations and flattening candidates
        

#### print_summary
**Parameters**: self
**Returns**: None
**Description**: 
        Print human-readable summary of sprawl violations.

        Displays breadth violations and flattening candidates.
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SprawlInspectorAgent.

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
        



## Function: __init__

**Parameters**: self, target_path
**Returns**: None
**Description**: 
        Initialize sprawl inspector.

        Args:
            target_path: Root directory to inspect for sprawl violations
        



## Function: inspect

**Parameters**: self
**Returns**: Dict[str, Any]
**Description**: 
        Scan directory tree for sprawl violations.

        Returns:
            Report dictionary with violations and flattening candidates
        



## Function: print_summary

**Parameters**: self
**Returns**: None
**Description**: 
        Print human-readable summary of sprawl violations.

        Displays breadth violations and flattening candidates.
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SprawlInspectorAgent.

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
# Using SprawlInspectorAgent
sprawlinspectoragent = SprawlInspectorAgent()
sprawlinspectoragent.inspect()
sprawlinspectoragent.print_summary()
```

### Function Usage

```python
# Using __init__
result = __init__(target_path)
```

```python
# Using inspect
result = inspect()
```

```python
# Using print_summary
result = print_summary()
```



---
**Generated**: 2026-03-26T09:39:05.408403
**Type**: api_reference
**Quality**: comprehensive
