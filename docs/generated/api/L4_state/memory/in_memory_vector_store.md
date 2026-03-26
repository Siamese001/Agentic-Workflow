# API Documentation: in_memory_vector_store

**Target Audience**: developers, api_users

# in_memory_vector_store API Documentation

**File**: `in_memory_vector_store.py`
**Classes**: 1
**Functions**: 4

## Classes

- **InMemoryVectorStore** (inherits from BaseVectorStore)

## Functions

- **_faiss_available** -> bool
- **__init__**
- **_reset_faiss** -> None
- **_rebuild_faiss** -> None


## Class: InMemoryVectorStore

**Inherits from**: BaseVectorStore

### Methods

#### __init__
**Parameters**: self

#### _reset_faiss
**Parameters**: self
**Returns**: None

#### _rebuild_faiss
**Parameters**: self
**Returns**: None



## Function: _faiss_available

**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: _reset_faiss

**Parameters**: self
**Returns**: None


## Function: _rebuild_faiss

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using InMemoryVectorStore
inmemoryvectorstore = InMemoryVectorStore()
```

### Function Usage

```python
# Using _faiss_available
result = _faiss_available()
```

```python
# Using __init__
result = __init__()
```

```python
# Using _reset_faiss
result = _reset_faiss()
```



---
**Generated**: 2026-03-26T09:39:04.577876
**Type**: api_reference
**Quality**: comprehensive
