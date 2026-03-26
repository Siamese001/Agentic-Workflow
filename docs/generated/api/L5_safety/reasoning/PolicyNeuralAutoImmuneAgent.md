# API Documentation: PolicyNeuralAutoImmuneAgent

**Target Audience**: developers, api_users

# PolicyNeuralAutoImmuneAgent API Documentation

**File**: `PolicyNeuralAutoImmuneAgent.py`
**Classes**: 1
**Functions**: 4

## Classes

- **PolicyNeuralAutoImmuneAgent** (inherits from NeuralAutoImmuneAgent, SovereignBaseAgent)

## Functions

- **__init__** -> None
- **detect_breaches** -> Any
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: PolicyNeuralAutoImmuneAgent

**Description**: PolicyNeuralAutoImmuneAgent agent for autonomous operations.

**Inherits from**: NeuralAutoImmuneAgent, SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.

#### detect_breaches
**Parameters**: self
**Returns**: Any
**Description**: Execute detect_breaches operation.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by PolicyNeuralAutoImmuneAgent.

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

**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.



## Function: detect_breaches

**Parameters**: self
**Returns**: Any
**Description**: Execute detect_breaches operation.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by PolicyNeuralAutoImmuneAgent.

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
# Using PolicyNeuralAutoImmuneAgent
policyneuralautoimmuneagent = PolicyNeuralAutoImmuneAgent()
policyneuralautoimmuneagent.detect_breaches()
policyneuralautoimmuneagent.heal_repository()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using detect_breaches
result = detect_breaches()
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:05.345596
**Type**: api_reference
**Quality**: comprehensive
