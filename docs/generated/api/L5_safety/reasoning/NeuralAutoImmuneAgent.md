# API Documentation: NeuralAutoImmuneAgent

**Target Audience**: developers, api_users

# NeuralAutoImmuneAgent API Documentation

**File**: `NeuralAutoImmuneAgent.py`
**Classes**: 1
**Functions**: 3

## Classes

- **NeuralAutoImmuneAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__**
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: NeuralAutoImmuneAgent

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self

#### heal_repository
**Parameters**: self
**Returns**: dict[str, int]

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by NeuralAutoImmuneAgent.

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
        



## Function: __post_init__

**Parameters**: self


## Function: heal_repository

**Parameters**: self
**Returns**: dict[str, int]


## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by NeuralAutoImmuneAgent.

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
# Using NeuralAutoImmuneAgent
neuralautoimmuneagent = NeuralAutoImmuneAgent()
neuralautoimmuneagent.heal_repository()
neuralautoimmuneagent.heal()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using heal_repository
result = heal_repository()
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:05.335715
**Type**: api_reference
**Quality**: comprehensive
