# API Documentation: error_context_preserver

**Target Audience**: developers, api_users

# error_context_preserver API Documentation

**File**: `error_context_preserver.py`
**Classes**: 2
**Functions**: 4

## Classes

- **PreservationResult** (inherits from NamedTuple)
- **ErrorContext**

## Functions

- **preserve_error_context** -> PreservationResult
- **__post_init__**
- **_canonical_bytes** -> bytes
- **with_chain** -> ErrorContext


## Class: PreservationResult

**Description**: The result of preserving an error context in L4.

**Inherits from**: NamedTuple



## Class: ErrorContext

**Description**: A structured, versioned representation of an error and its context.

### Methods

#### __post_init__
**Parameters**: self

#### _canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Computes the canonical byte representation of the context for hashing.

#### with_chain
**Parameters**: self, prev_hash
**Returns**: ErrorContext
**Description**: Attaches the previous hash to form a chain, returning a new instance.



## Function: preserve_error_context

**Parameters**: error, agent_state, execution_trace, prev_hash
**Returns**: PreservationResult
**Description**: 
    Preserves the full error context in L4 with content-hash chaining.

    This function enforces Guarantee #5 (Don't lose data on error) by creating a
    versioned, auditable record of the system's state at the time of failure.
    The hash chain ensures the integrity of the historical record.

    Args:
        error: The exception that was raised.
        agent_state: The complete state of the agent at the time of error.
        execution_trace: The execution trace leading up to the error.
        prev_hash: The hash of the previous record in the L4 state ledger.

    Returns:
        A PreservationResult with the new context hash and storage path.
    



## Function: __post_init__

**Parameters**: self


## Function: _canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Computes the canonical byte representation of the context for hashing.



## Function: with_chain

**Parameters**: self, prev_hash
**Returns**: ErrorContext
**Description**: Attaches the previous hash to form a chain, returning a new instance.



## Usage Examples

### Class Usage

```python
# Using PreservationResult
preservationresult = PreservationResult()
```

```python
# Using ErrorContext
errorcontext = ErrorContext()
errorcontext.with_chain()
```

### Function Usage

```python
# Using preserve_error_context
result = preserve_error_context(error, agent_state)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _canonical_bytes
result = _canonical_bytes()
```



---
**Generated**: 2026-03-26T09:39:04.531845
**Type**: api_reference
**Quality**: comprehensive
