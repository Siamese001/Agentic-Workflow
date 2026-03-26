# API Documentation: bm25_store

**Target Audience**: developers, api_users

# bm25_store API Documentation

**File**: `bm25_store.py`
**Classes**: 1
**Functions**: 5

## Classes

- **Bm25Store**

## Functions

- **get_bm25_store** -> Bm25Store
- **__init__**
- **add_documents** -> None
- **_build_index** -> None
- **query** -> list[dict]


## Class: Bm25Store

**Description**: In-memory BM25 index for fast keyword retrieval.

### Methods

#### __init__
**Parameters**: self

#### add_documents
**Parameters**: self, docs
**Returns**: None
**Description**: Add or update documents.

#### _build_index
**Parameters**: self
**Returns**: None

#### query
**Parameters**: self, query, top_k
**Returns**: list[dict]
**Description**: BM25 keyword search.



## Function: get_bm25_store

**Returns**: Bm25Store
**Description**: Get the singleton BM25 store instance for hybrid search operations.



## Function: __init__

**Parameters**: self


## Function: add_documents

**Parameters**: self, docs
**Returns**: None
**Description**: Add or update documents.



## Function: _build_index

**Parameters**: self
**Returns**: None


## Function: query

**Parameters**: self, query, top_k
**Returns**: list[dict]
**Description**: BM25 keyword search.



## Usage Examples

### Class Usage

```python
# Using Bm25Store
bm25store = Bm25Store()
bm25store.add_documents()
bm25store.query()
```

### Function Usage

```python
# Using get_bm25_store
result = get_bm25_store()
```

```python
# Using __init__
result = __init__()
```

```python
# Using add_documents
result = add_documents(docs)
```



---
**Generated**: 2026-03-26T09:39:04.561853
**Type**: api_reference
**Quality**: comprehensive
