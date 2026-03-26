# API Documentation: reasoning_pattern_validator

**Target Audience**: developers, api_users

# reasoning_pattern_validator API Documentation

**File**: `reasoning_pattern_validator.py`
**Classes**: 1
**Functions**: 1

## Classes

- **BaseReasoningPattern** (inherits from ABC)

## Functions

- **get_confidence_score** -> float


## Class: BaseReasoningPattern

**Description**: 
    Defines how the agent converts State -> Next Action.
    

**Inherits from**: ABC

### Methods

#### get_confidence_score
**Parameters**: self, state
**Returns**: float
**Description**: 
        Return confidence score for current reasoning state.

        Args:
            state: Current agent state

        Returns:
            Confidence score between 0.0 and 1.0
        



## Function: get_confidence_score

**Parameters**: self, state
**Returns**: float
**Description**: 
        Return confidence score for current reasoning state.

        Args:
            state: Current agent state

        Returns:
            Confidence score between 0.0 and 1.0
        



## Usage Examples

### Class Usage

```python
# Using BaseReasoningPattern
basereasoningpattern = BaseReasoningPattern()
basereasoningpattern.get_confidence_score()
```

### Function Usage

```python
# Using get_confidence_score
result = get_confidence_score(state)
```



---
**Generated**: 2026-03-26T09:39:05.864426
**Type**: api_reference
**Quality**: comprehensive
