# API Documentation: rag_provider_types

**Target Audience**: developers, api_users

# rag_provider_types API Documentation

**File**: `rag_provider_types.py`
**Classes**: 4
**Functions**: 1

## Classes

- **RagQuery**
- **RagDocument**
- **RagResult**
- **IRagProvider** (inherits from ABC)

## Functions

- **get_health** -> dict[str, Any]


## Class: RagQuery

**Description**: Standard RAG query input.



## Class: RagDocument

**Description**: Standard RAG document output.



## Class: RagResult

**Description**: Standard RAG result with telemetry.



## Class: IRagProvider

**Description**: 
    Unified RAG Provider Interface.

    All RAG implementations (L1, L3, L4, L5, apps_shared) must implement this.
    

**Inherits from**: ABC

### Methods

#### get_health
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get RAG system health status.



## Function: get_health

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get RAG system health status.



## Usage Examples

### Class Usage

```python
# Using RagQuery
ragquery = RagQuery()
```

```python
# Using RagDocument
ragdocument = RagDocument()
```

```python
# Using RagResult
ragresult = RagResult()
```

### Function Usage

```python
# Using get_health
result = get_health()
```



---
**Generated**: 2026-03-26T09:39:04.396703
**Type**: api_reference
**Quality**: comprehensive
