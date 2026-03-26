# API Documentation: embedding_sovereignty_guard

**Target Audience**: developers, api_users

# embedding_sovereignty_guard API Documentation

**File**: `embedding_sovereignty_guard.py`
**Classes**: 2
**Functions**: 3

## Classes

- **EmbeddingResult**
- **EmbeddingInfluenceViolation** (inherits from Exception)

## Functions

- **guard_embedding_influence** -> None
- **__init__**
- **_scan_for_embedding_result** -> None


## Class: EmbeddingResult

**Description**: A placeholder for the result of an embedding retrieval operation.



## Class: EmbeddingInfluenceViolation

**Description**: Raised when an embedding artifact is detected influencing a sovereign decision.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, decision_type, found_in



## Function: guard_embedding_influence

**Returns**: None
**Description**: 
    A sovereign runtime guard that prevents embedding results from influencing decisions.

    This function enforces Guarantee #21 by recursively scanning the arguments of
    critical decision-making functions (like `route_healing_tier` or safety
    classifiers) to ensure no `EmbeddingResult` objects are present. This prevents
    both direct and indirect leakage.

    This guard must be placed at the entry point of all sovereign decision boundaries.

    Args:
        decision_type: A string identifying the type of decision being made.
        *args: The positional arguments passed to the decision function.
        **kwargs: The keyword arguments passed to the decision function.

    Raises:
        EmbeddingInfluenceViolation: If an `EmbeddingResult` is found in the arguments.
    



## Function: __init__

**Parameters**: self, decision_type, found_in


## Function: _scan_for_embedding_result

**Parameters**: obj, path
**Returns**: None
**Description**: 
        Recursively scans an object for instances of EmbeddingResult.
        



## Usage Examples

### Class Usage

```python
# Using EmbeddingResult
embeddingresult = EmbeddingResult()
```

```python
# Using EmbeddingInfluenceViolation
embeddinginfluenceviolation = EmbeddingInfluenceViolation()
```

### Function Usage

```python
# Using guard_embedding_influence
result = guard_embedding_influence()
```

```python
# Using __init__
result = __init__(decision_type, found_in)
```

```python
# Using _scan_for_embedding_result
result = _scan_for_embedding_result(obj, path)
```



---
**Generated**: 2026-03-26T09:39:04.490800
**Type**: api_reference
**Quality**: comprehensive
