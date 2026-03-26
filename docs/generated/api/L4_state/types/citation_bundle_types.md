# API Documentation: citation_bundle_types

**Target Audience**: developers, api_users

# citation_bundle_types API Documentation

**File**: `citation_bundle_types.py`
**Classes**: 1
**Functions**: 6

## Classes

- **CitationBundle**

## Functions

- **_sha256** -> str
- **_anchor_sort_key** -> tuple[str, str, int]
- **build_citation_bundle** -> CitationBundle
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **to_dict** -> dict[str, Any]


## Class: CitationBundle

**Description**: 
    Deterministic citation artifact attached to retrieval-backed responses.

    Fields
    ------
    schema_version : int              — bumped on breaking changes
    request_hash   : str              — sha256 of canonical retrieval request
    anchors        : list[RetrievalAnchor] — sorted by (source_doc_id, chunk_id, char_start)
    citation_hash  : str              — sha256(canonical_bytes); auto-computed
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding citation_hash (self-referential).
        Anchors sorted by (source_doc_id, chunk_id, char_start).
        Volatile fields (retrieved_at_utc) excluded from hash computation.
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: _anchor_sort_key

**Parameters**: a
**Returns**: tuple[str, str, int]


## Function: build_citation_bundle

**Parameters**: request_hash, anchors
**Returns**: CitationBundle
**Description**: Factory: build a CitationBundle from a request hash and anchor list.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding citation_hash (self-referential).
        Anchors sorted by (source_doc_id, chunk_id, char_start).
        Volatile fields (retrieved_at_utc) excluded from hash computation.
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using CitationBundle
citationbundle = CitationBundle()
citationbundle.canonical_bytes()
citationbundle.to_dict()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using _anchor_sort_key
result = _anchor_sort_key(a)
```

```python
# Using build_citation_bundle
result = build_citation_bundle(request_hash, anchors)
```



---
**Generated**: 2026-03-26T09:39:04.627658
**Type**: api_reference
**Quality**: comprehensive
