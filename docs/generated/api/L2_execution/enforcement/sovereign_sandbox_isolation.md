# API Documentation: sovereign_sandbox_isolation

**Target Audience**: developers, api_users

# sovereign_sandbox_isolation API Documentation

**File**: `sovereign_sandbox_isolation.py`
**Classes**: 2
**Functions**: 2

## Classes

- **ReplayNondeterminismViolation** (inherits from Exception)
- **SandboxResult** (inherits from NamedTuple)

## Functions

- **execute_in_sandbox** -> SandboxResult
- **__init__**


## Class: ReplayNondeterminismViolation

**Description**: Raised when a replay operation deviates from the execution transcript.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, message, expected, actual



## Class: SandboxResult

**Description**: The result of a sandboxed operation.

**Inherits from**: NamedTuple



## Function: execute_in_sandbox

**Parameters**: operation, args, kwargs, replay_mode, transcript
**Returns**: SandboxResult
**Description**: 
    Executes an operation within a sovereign sandbox, enforcing replay determinism.

    This function is the core of Guarantee #6. It ensures that in replay mode,
    all operations produce results identical to the original execution transcript.
    Any deviation results in a `ReplayNondeterminismViolation`.

    In a real implementation, this would be integrated into the UWG and would
    also prevent direct filesystem/network access by patching modules like `os`
    and `socket` within its execution context.

    Args:
        operation: The function or method to execute.
        args: Positional arguments for the operation.
        kwargs: Keyword arguments for the operation.
        replay_mode: If True, enforces strict transcript matching.
        transcript: The execution transcript to validate against in replay mode.

    Returns:
        A SandboxResult indicating the outcome of the operation.
    



## Function: __init__

**Parameters**: self, message, expected, actual


## Usage Examples

### Class Usage

```python
# Using ReplayNondeterminismViolation
replaynondeterminismviolation = ReplayNondeterminismViolation()
```

```python
# Using SandboxResult
sandboxresult = SandboxResult()
```

### Function Usage

```python
# Using execute_in_sandbox
result = execute_in_sandbox(operation, args)
```

```python
# Using __init__
result = __init__(message, expected)
```



---
**Generated**: 2026-03-26T09:39:03.737358
**Type**: api_reference
**Quality**: comprehensive
