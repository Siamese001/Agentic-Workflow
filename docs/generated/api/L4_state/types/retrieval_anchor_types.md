# API Documentation: retrieval_anchor_types

**Target Audience**: developers, api_users

# retrieval_anchor_types API Documentation

**File**: `retrieval_anchor_types.py`
**Classes**: 3
**Functions**: 5

## Classes

- **RetrievalAnchor**
- **AnchoredResult**
- **AnchorViolationError** (inherits from Exception)

## Functions

- **enforce_anchor_coverage** -> None
- **__post_init__** -> None
- **now_utc** -> str
- **to_dict** -> dict[str, object]
- **__init__** -> None


## Class: RetrievalAnchor

**Description**: 
    Citation anchor attached to every L4 retrieval result.

    All fields are required. No optional fields — absence of any field
    indicates a retrieval implementation that has not been grounded.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### now_utc
**Returns**: str

#### to_dict
**Parameters**: self
**Returns**: dict[str, object]



## Class: AnchoredResult

**Description**: 
    A retrieval result paired with its mandatory citation anchor.
    Returned by all L4 semantic search / chunk retrieval calls.
    



## Class: AnchorViolationError

**Description**: 
    Raised by Guardian when reasoning uses retrieved content without anchors.

    Violation code: MISSING_RETRIEVAL_ANCHOR
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, message
**Returns**: None



## Function: enforce_anchor_coverage

**Parameters**: retrieval_context, anchors
**Returns**: None
**Description**: 
    Guardian enforcement: if retrieval_context is non-empty,
    anchors list must be non-empty and cover each retrieved chunk.

    Raises AnchorViolationError if the invariant is violated.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: now_utc

**Returns**: str


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, object]


## Function: __init__

**Parameters**: self, message
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using RetrievalAnchor
retrievalanchor = RetrievalAnchor()
retrievalanchor.now_utc()
retrievalanchor.to_dict()
```

```python
# Using AnchoredResult
anchoredresult = AnchoredResult()
```

```python
# Using AnchorViolationError
anchorviolationerror = AnchorViolationError()
```

### Function Usage

```python
# Using enforce_anchor_coverage
result = enforce_anchor_coverage(retrieval_context, anchors)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using now_utc
result = now_utc()
```



---
**Generated**: 2026-03-26T09:39:04.644094
**Type**: api_reference
**Quality**: comprehensive
