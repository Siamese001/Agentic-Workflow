# API Documentation: ml_write_intent_types

**Target Audience**: developers, api_users

# ml_write_intent_types API Documentation

**File**: `ml_write_intent_types.py`
**Classes**: 3
**Functions**: 9

## Classes

- **MLWriteEnvelopeViolation** (inherits from Exception)
- **MLWriteIntent**
- **MLWriteIntentExecutor**

## Functions

- **is_commit_sandbox_active** -> bool
- **execute_ml_write_intent_outside_sandbox** -> None
- **__init__** -> None
- **__post_init__** -> None
- **_compute_hash** -> str
- **canonical_bytes** -> bytes
- **__enter__** -> MLWriteIntentExecutor
- **__exit__** -> None
- **execute** -> dict[str, Any]


## Class: MLWriteEnvelopeViolation

**Description**: 
    Raised when an MLWriteIntent is executed outside the L2.2 commit sandbox.

    Violation code: ML_WRITE_OUTSIDE_SANDBOX
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, message
**Returns**: None



## Class: MLWriteIntent

**Description**: 
    Declarative ML write intent.

    Fields:
        kind        — "pattern_store" or "cache_set"
        payload     — serializable dict of write parameters
        requires_commit — always True; enforced in __post_init__
        intent_hash — sha256 of canonical_bytes() (computed on construction)
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### _compute_hash
**Parameters**: self
**Returns**: str

#### canonical_bytes
**Parameters**: self
**Returns**: bytes



## Class: MLWriteIntentExecutor

**Description**: 
    L2.2 commit sandbox for executing MLWriteIntents.

    Usage (context manager):
        with MLWriteIntentExecutor() as executor:
            executor.execute(intent)

    Attempting to call execute() outside the context manager raises
    MLWriteEnvelopeViolation.
    

### Methods

#### __enter__
**Parameters**: self
**Returns**: MLWriteIntentExecutor

#### __exit__
**Parameters**: self
**Returns**: None

#### execute
**Parameters**: self, intent
**Returns**: dict[str, Any]
**Description**: 
        Execute an MLWriteIntent inside the L2.2 sandbox.
        



## Function: is_commit_sandbox_active

**Returns**: bool
**Description**: Return True if the L2.2 commit sandbox is currently active.



## Function: execute_ml_write_intent_outside_sandbox

**Parameters**: intent
**Returns**: None
**Description**: 
    Attempt to execute an MLWriteIntent outside the sandbox.
    Always raises MLWriteEnvelopeViolation.

    This function exists to make the enforcement contract explicit and testable.
    



## Function: __init__

**Parameters**: self, message
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: _compute_hash

**Parameters**: self
**Returns**: str


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes


## Function: __enter__

**Parameters**: self
**Returns**: MLWriteIntentExecutor


## Function: __exit__

**Parameters**: self
**Returns**: None


## Function: execute

**Parameters**: self, intent
**Returns**: dict[str, Any]
**Description**: 
        Execute an MLWriteIntent inside the L2.2 sandbox.
        



## Usage Examples

### Class Usage

```python
# Using MLWriteEnvelopeViolation
mlwriteenvelopeviolation = MLWriteEnvelopeViolation()
```

```python
# Using MLWriteIntent
mlwriteintent = MLWriteIntent()
mlwriteintent.canonical_bytes()
```

```python
# Using MLWriteIntentExecutor
mlwriteintentexecutor = MLWriteIntentExecutor()
mlwriteintentexecutor.execute()
```

### Function Usage

```python
# Using is_commit_sandbox_active
result = is_commit_sandbox_active()
```

```python
# Using execute_ml_write_intent_outside_sandbox
result = execute_ml_write_intent_outside_sandbox(intent)
```

```python
# Using __init__
result = __init__(message)
```



---
**Generated**: 2026-03-26T09:39:03.993717
**Type**: api_reference
**Quality**: comprehensive
