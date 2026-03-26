# API Documentation: sovereign_semantic_cache

**Target Audience**: developers, api_users

# sovereign_semantic_cache API Documentation

**File**: `sovereign_semantic_cache.py`
**Classes**: 1
**Functions**: 10

## Classes

- **SovereignSemanticCache** (inherits from SovereignBaseAgent)

## Functions

- **get_redis_client**
- **__init__**
- **_cache_key** -> str
- **_extract_ast_features** -> dict
- **_calculate_depth** -> int
- **cache_file** -> None
- **invalidate** -> Any
- **query** -> list[dict]
- **heal_repository** -> dict
- **heal**


## Class: SovereignSemanticCache

**Description**: Ultra-hardened hybrid semantic cache — Redis local + InMemoryVectorStore eternal.

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, mission_id, engine

#### _cache_key
**Parameters**: self, file_path
**Returns**: str
**Description**: Mission-isolated and path-hashed key for L4 sovereignty.

#### _extract_ast_features
**Parameters**: self, code
**Returns**: dict
**Description**: Parse AST for structural signals (Key 41/42).

#### _calculate_depth
**Parameters**: self, node, current
**Returns**: int

#### cache_file
**Parameters**: self, file_path, code, metadata
**Returns**: None
**Description**: Embed and cache with dual-store synchronization.

#### invalidate
**Parameters**: self, file_path
**Returns**: Any
**Description**: Purge both stores on fission or physical move.

#### query
**Parameters**: self, text, top_k, namespace
**Returns**: list[dict]
**Description**: Semantic similarity search over the in-memory vector store.

        Embeds *text* via BGEEmbedder (BAAI/bge-m3, 1024-dim), then ranks
        all cached entries by cosine similarity.  Returns informational-only
        dicts: ``content_hash``, ``score``, ``content`` (metadata text preview).

        Falls back to empty list when the kill-switch is active or the store
        is empty.  Works with both InMemoryVectorStore (MemoryItem-backed) and
        plain-dict fallback stores.
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().

#### heal
**Parameters**: self, violation



## Function: get_redis_client

**Description**: Shim: redirect legacy callers to the canonical DeterministicRedisCache client.



## Function: __init__

**Parameters**: self, mission_id, engine


## Function: _cache_key

**Parameters**: self, file_path
**Returns**: str
**Description**: Mission-isolated and path-hashed key for L4 sovereignty.



## Function: _extract_ast_features

**Parameters**: self, code
**Returns**: dict
**Description**: Parse AST for structural signals (Key 41/42).



## Function: _calculate_depth

**Parameters**: self, node, current
**Returns**: int


## Function: cache_file

**Parameters**: self, file_path, code, metadata
**Returns**: None
**Description**: Embed and cache with dual-store synchronization.



## Function: invalidate

**Parameters**: self, file_path
**Returns**: Any
**Description**: Purge both stores on fission or physical move.



## Function: query

**Parameters**: self, text, top_k, namespace
**Returns**: list[dict]
**Description**: Semantic similarity search over the in-memory vector store.

        Embeds *text* via BGEEmbedder (BAAI/bge-m3, 1024-dim), then ranks
        all cached entries by cosine similarity.  Returns informational-only
        dicts: ``content_hash``, ``score``, ``content`` (metadata text preview).

        Falls back to empty list when the kill-switch is active or the store
        is empty.  Works with both InMemoryVectorStore (MemoryItem-backed) and
        plain-dict fallback stores.
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using SovereignSemanticCache
sovereignsemanticcache = SovereignSemanticCache()
sovereignsemanticcache.cache_file()
sovereignsemanticcache.invalidate()
```

### Function Usage

```python
# Using get_redis_client
result = get_redis_client()
```

```python
# Using __init__
result = __init__(mission_id, engine)
```

```python
# Using _cache_key
result = _cache_key(file_path)
```



---
**Generated**: 2026-03-26T09:39:04.599226
**Type**: api_reference
**Quality**: comprehensive
