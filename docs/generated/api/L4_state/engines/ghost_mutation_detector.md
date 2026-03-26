# API Documentation: ghost_mutation_detector

**Target Audience**: developers, api_users

# ghost_mutation_detector API Documentation

**File**: `ghost_mutation_detector.py`
**Classes**: 2
**Functions**: 3

## Classes

- **GhostMutationViolation** (inherits from Exception)
- **ReconciliationResult** (inherits from NamedTuple)

## Functions

- **_deep_diff** -> list[str]
- **detect_ghost_mutations** -> ReconciliationResult
- **__init__**


## Class: GhostMutationViolation

**Description**: Raised when a state mutation is detected that was not recorded in the transcript.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, message, diff



## Class: ReconciliationResult

**Description**: The result of a state reconciliation operation.

**Inherits from**: NamedTuple



## Function: _deep_diff

**Parameters**: before, after, path
**Returns**: list[str]
**Description**: Recursively diffs two dictionaries and returns a list of differences.



## Function: detect_ghost_mutations

**Parameters**: state_before, state_after, transcript
**Returns**: ReconciliationResult
**Description**: 
    Detects hidden state mutations by comparing before/after snapshots against a transcript.

    This function enforces Guarantee #15 by performing a deep diff between the state
    before and after an operation and ensuring that all detected changes are accounted
    for in the official execution transcript. Any un-audited change is a "ghost mutation".

    Args:
        state_before: A snapshot of the system state before the operation.
        state_after: A snapshot of the system state after the operation.
        transcript: The official record of all mutations that were supposed to happen.

    Returns:
        A ReconciliationResult indicating if the state is consistent.
    



## Function: __init__

**Parameters**: self, message, diff


## Usage Examples

### Class Usage

```python
# Using GhostMutationViolation
ghostmutationviolation = GhostMutationViolation()
```

```python
# Using ReconciliationResult
reconciliationresult = ReconciliationResult()
```

### Function Usage

```python
# Using _deep_diff
result = _deep_diff(before, after)
```

```python
# Using detect_ghost_mutations
result = detect_ghost_mutations(state_before, state_after)
```

```python
# Using __init__
result = __init__(message, diff)
```



---
**Generated**: 2026-03-26T09:39:04.536700
**Type**: api_reference
**Quality**: comprehensive
