# API Documentation: citation_enforcement

**Target Audience**: developers, api_users

# citation_enforcement API Documentation

**File**: `citation_enforcement.py`
**Classes**: 1
**Functions**: 5

## Classes

- **CitationEnforcementViolation** (inherits from Exception)

## Functions

- **_sha256** -> str
- **_build_request_hash_from_output** -> str
- **enforce_citations_for_retrieval** -> dict[str, Any]
- **assemble_response** -> dict[str, Any]
- **__init__** -> None


## Class: CitationEnforcementViolation

**Description**: 
    Raised when retrieval was used but anchors are missing from the response.

    Attributes
    ----------
    code   : str — always "MISSING_CITATIONS"
    detail : str — human-readable description
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, detail
**Returns**: None



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: _build_request_hash_from_output

**Parameters**: output
**Returns**: str
**Description**: 
    Derive a stable request_hash from the output dict.
    Uses only non-volatile fields present in the output.
    Falls back to sha256 of the output keys if no canonical subset available.
    



## Function: enforce_citations_for_retrieval

**Parameters**: output, anchored_results, retrieval_used
**Returns**: dict[str, Any]
**Description**: 
    Enforce anchor coverage rule for retrieval-backed responses.

    Parameters
    ----------
    output           : dict  — the response artifact to attach citations to
    anchored_results : list[AnchoredResult] | None
        Retrieved content with anchors. Must be non-empty if retrieval_used=True.
    retrieval_used   : bool
        True if L4 retrieval was used to produce this response.
    request_hash     : str | None
        Optional stable hash of the retrieval request. Auto-derived if None.

    Returns
    -------
    dict — output with "citations" key containing CitationBundle.to_dict()
           (unchanged if retrieval_used=False)

    Raises
    ------
    CitationEnforcementViolation(code="MISSING_CITATIONS")
        If retrieval_used=True and anchored_results is empty or None.
    



## Function: assemble_response

**Parameters**: output, anchored_results, retrieval_used
**Returns**: dict[str, Any]
**Description**: 
    Canonical response assembly seam.

    Calls enforce_citations_for_retrieval() to attach citations before returning.
    This is the single authoritative entry point for final response construction.
    



## Function: __init__

**Parameters**: self, detail
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using CitationEnforcementViolation
citationenforcementviolation = CitationEnforcementViolation()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using _build_request_hash_from_output
result = _build_request_hash_from_output(output)
```

```python
# Using enforce_citations_for_retrieval
result = enforce_citations_for_retrieval(output, anchored_results)
```



---
**Generated**: 2026-03-26T09:39:04.490240
**Type**: api_reference
**Quality**: comprehensive
