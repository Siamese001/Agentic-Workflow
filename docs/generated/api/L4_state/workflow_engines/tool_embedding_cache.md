# API Documentation: tool_embedding_cache

**Target Audience**: developers, api_users

# tool_embedding_cache API Documentation

**File**: `tool_embedding_cache.py`
**Classes**: 1
**Functions**: 5

## Classes

- **ToolEmbeddingCache**

## Functions

- **get_tool_embedding_cache** -> ToolEmbeddingCache
- **__init__**
- **get_or_fetch** -> tuple[list[list[float]], list[str]]
- **_compute_tool_fingerprint** -> str
- **invalidate_all** -> None


## Class: ToolEmbeddingCache

**Description**: Cache for tool registry embedding matrices.

    Eliminates repeated expensive embedding computations for the same tool set.
    Automatically invalidates when tool set changes via fingerprint keying.
    

### Methods

#### __init__
**Parameters**: self, cache, ttl_seconds

#### get_or_fetch
**Parameters**: self, tool_definitions, fetch_embeddings
**Returns**: tuple[list[list[float]], list[str]]
**Description**: Read-through helper: return cached embeddings or call *fetch_embeddings*.

        *fetch_embeddings* is a zero-argument callable that computes and returns
        (embedding_matrix, tool_names) tuple.  Called only on cache miss.

        Args:
            tool_definitions: List of tool definition dicts (name, description, tags)
            fetch_embeddings: Callable that returns (embeddings, tool_names) tuple
            replay_mode: If True, bypass cache entirely

        Returns:
            Tuple of (embedding_matrix, tool_names)

        Raises:
            ValueError: If tool_definitions is empty
        

#### _compute_tool_fingerprint
**Parameters**: self, tool_definitions
**Returns**: str
**Description**: Compute deterministic fingerprint of tool set for cache key.

#### invalidate_all
**Parameters**: self
**Returns**: None
**Description**: Invalidate all cached embeddings.

        Note: This is a no-op since cache keys are fingerprint-addressed.
        Tool set changes automatically invalidate via different fingerprint.
        



## Function: get_tool_embedding_cache

**Returns**: ToolEmbeddingCache
**Description**: Get the singleton tool embedding cache instance.



## Function: __init__

**Parameters**: self, cache, ttl_seconds


## Function: get_or_fetch

**Parameters**: self, tool_definitions, fetch_embeddings
**Returns**: tuple[list[list[float]], list[str]]
**Description**: Read-through helper: return cached embeddings or call *fetch_embeddings*.

        *fetch_embeddings* is a zero-argument callable that computes and returns
        (embedding_matrix, tool_names) tuple.  Called only on cache miss.

        Args:
            tool_definitions: List of tool definition dicts (name, description, tags)
            fetch_embeddings: Callable that returns (embeddings, tool_names) tuple
            replay_mode: If True, bypass cache entirely

        Returns:
            Tuple of (embedding_matrix, tool_names)

        Raises:
            ValueError: If tool_definitions is empty
        



## Function: _compute_tool_fingerprint

**Parameters**: self, tool_definitions
**Returns**: str
**Description**: Compute deterministic fingerprint of tool set for cache key.



## Function: invalidate_all

**Parameters**: self
**Returns**: None
**Description**: Invalidate all cached embeddings.

        Note: This is a no-op since cache keys are fingerprint-addressed.
        Tool set changes automatically invalidate via different fingerprint.
        



## Usage Examples

### Class Usage

```python
# Using ToolEmbeddingCache
toolembeddingcache = ToolEmbeddingCache()
toolembeddingcache.get_or_fetch()
toolembeddingcache.invalidate_all()
```

### Function Usage

```python
# Using get_tool_embedding_cache
result = get_tool_embedding_cache()
```

```python
# Using __init__
result = __init__(cache, ttl_seconds)
```

```python
# Using get_or_fetch
result = get_or_fetch(tool_definitions, fetch_embeddings)
```



---
**Generated**: 2026-03-26T09:39:04.708480
**Type**: api_reference
**Quality**: comprehensive
