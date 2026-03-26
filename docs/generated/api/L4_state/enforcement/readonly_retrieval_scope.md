# API Documentation: readonly_retrieval_scope

**Target Audience**: developers, api_users

# readonly_retrieval_scope API Documentation

**File**: `readonly_retrieval_scope.py`
**Classes**: 1
**Functions**: 4

## Classes

- **RetrievalMutationViolation** (inherits from Exception)

## Functions

- **is_read_only_retrieval_active** -> bool
- **assert_not_read_only** -> None
- **read_only_retrieval_scope** -> Generator[None, None, None]
- **__init__** -> None


## Class: RetrievalMutationViolation

**Description**: 
    Raised when a persistent mutation is attempted inside a read-only retrieval scope.

    Attributes
    ----------
    code   : str  — always "RETRIEVAL_MUTATION_BLOCKED"
    detail : str  — human-readable description of the blocked operation
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, detail
**Returns**: None



## Function: is_read_only_retrieval_active

**Returns**: bool
**Description**: Return True when a read_only_retrieval_scope() is currently active.



## Function: assert_not_read_only

**Parameters**: operation
**Returns**: None
**Description**: 
    Raise RetrievalMutationViolation if a read-only retrieval scope is active.

    Call this at the top of any persistent-write seam (Redis set/setex,
    Pinecone upsert, file write) that must be blocked during retrieval.

    Parameters
    ----------
    operation : str
        Short description of the attempted mutation (e.g., "redis.setex",
        "pinecone.upsert"). Included in the violation detail for traceability.
    



## Function: read_only_retrieval_scope

**Returns**: Generator[None, None, None]
**Description**: 
    Context manager that activates the read-only retrieval flag.

    Usage
    -----
    with read_only_retrieval_scope():
        results = l4_semantic_query(query)   # safe — read-only
        # any assert_not_read_only() call here raises RetrievalMutationViolation

    Guarantees
    ----------
    - Flag is set to True on entry.
    - Flag is restored to False on exit (even on exception).
    - Re-entrant: nested scopes are allowed (flag stays True until outermost exits).
    



## Function: __init__

**Parameters**: self, detail
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using RetrievalMutationViolation
retrievalmutationviolation = RetrievalMutationViolation()
```

### Function Usage

```python
# Using is_read_only_retrieval_active
result = is_read_only_retrieval_active()
```

```python
# Using assert_not_read_only
result = assert_not_read_only(operation)
```

```python
# Using read_only_retrieval_scope
result = read_only_retrieval_scope()
```



---
**Generated**: 2026-03-26T09:39:04.517090
**Type**: api_reference
**Quality**: comprehensive
