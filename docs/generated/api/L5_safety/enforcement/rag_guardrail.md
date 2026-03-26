# API Documentation: rag_guardrail

**Target Audience**: developers, api_users

# rag_guardrail API Documentation

**File**: `rag_guardrail.py`
**Classes**: 3
**Functions**: 3

## Classes

- **ExternalKnowledgeAccessViolation** (inherits from Exception)
- **CitationBundle**
- **RagGuardrail**

## Functions

- **validate_citation_custody** -> None
- **__init__**
- **_compute**


## Class: ExternalKnowledgeAccessViolation

**Description**: Raised when retrieved context is consumed without a valid CitationBundle.

    REQ-RAGX-006: ExternalKnowledgeAccessViolation MUST be emitted and wave
    aborted if context used without CitationBundle.  Fail-closed.
    

**Inherits from**: Exception



## Class: CitationBundle

**Description**: Immutable citation binding for retrieved chunks.

    Every chunk of external knowledge entering the execution pipeline MUST
    carry a CitationBundle proving provenance.  Fields mirror REQ-RAGX-003.
    



## Class: RagGuardrail

**Description**: Brief description of functionality and purpose.

### Methods

#### __init__
**Parameters**: self, reranker, reranker_available, status_message



## Function: validate_citation_custody

**Parameters**: context_chunks, citation_bundles
**Returns**: None
**Description**: Enforce that every external-knowledge chunk has a matching CitationBundle.

    Args:
        context_chunks: list of dicts representing retrieved context.  Each dict
            MUST contain at least ``chunk_id``.
        citation_bundles: corresponding CitationBundle objects.  ``None`` or
            empty list when chunks are present triggers the violation.

    Raises:
        ExternalKnowledgeAccessViolation: when context is present but citations
            are missing, empty, or do not cover every chunk_id.
    



## Function: __init__

**Parameters**: self, reranker, reranker_available, status_message


## Function: _compute



## Usage Examples

### Class Usage

```python
# Using ExternalKnowledgeAccessViolation
externalknowledgeaccessviolation = ExternalKnowledgeAccessViolation()
```

```python
# Using CitationBundle
citationbundle = CitationBundle()
```

```python
# Using RagGuardrail
ragguardrail = RagGuardrail()
```

### Function Usage

```python
# Using validate_citation_custody
result = validate_citation_custody(context_chunks, citation_bundles)
```

```python
# Using __init__
result = __init__(reranker, reranker_available)
```

```python
# Using _compute
result = _compute()
```



---
**Generated**: 2026-03-26T09:39:04.911004
**Type**: api_reference
**Quality**: comprehensive
