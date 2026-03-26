# API Documentation: in_memory_vector_cache

**Target Audience**: developers, api_users

# in_memory_vector_cache API Documentation

**File**: `in_memory_vector_cache.py`
**Classes**: 2
**Functions**: 8

## Classes

- **InMemoryVectorCache**
- **TieredVectorStore**

## Functions

- **create_memory_vector_cache** -> InMemoryVectorCache
- **create_tiered_vector_store** -> TieredVectorStore
- **__init__**
- **get_count** -> int
- **clear** -> bool
- **delete_collection** -> bool
- **get_stats** -> dict[str, Any]
- **__init__**


## Class: InMemoryVectorCache

**Description**: In-memory vector cache using ChromaDB.

    Initializes an ephemeral in-memory ChromaDB instance for ultra-fast
    similarity search without network or disk I/O overhead.
    

### Methods

#### __init__
**Parameters**: self, collection_name, max_memory_gb
**Description**: Initialize in-memory ChromaDB cache.

        Args:
            collection_name: Name of the collection to create
            max_memory_gb: Maximum memory allocation in GB (default: 8)
        

#### get_count
**Parameters**: self
**Returns**: int
**Description**: Get the number of documents in the cache.

        Returns:
            Number of documents currently in cache
        

#### clear
**Parameters**: self
**Returns**: bool
**Description**: Wipe cache to free RAM.

        Returns:
            True if successful, False otherwise
        

#### delete_collection
**Parameters**: self
**Returns**: bool
**Description**: Delete the entire collection.

        Returns:
            True if successful, False otherwise
        

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics.

        Returns:
            Dictionary with cache statistics
        



## Class: TieredVectorStore

**Description**: Two-tier vector storage: hot in-memory cache + warm disk storage.

    Automatically promotes frequently accessed items to hot cache.
    

### Methods

#### __init__
**Parameters**: self, hot_cache, warm_store_url
**Description**: Initialize tiered vector store.

        Args:
            hot_cache: In-memory cache instance
            warm_store_url: URL for warm storage (Qdrant)
        



## Function: create_memory_vector_cache

**Parameters**: collection_name, max_memory_gb
**Returns**: InMemoryVectorCache
**Description**: Create an InMemoryVectorCache instance.

    Args:
        collection_name: Name of the collection
        max_memory_gb: Maximum memory allocation in GB

    Returns:
        Configured InMemoryVectorCache instance
    



## Function: create_tiered_vector_store

**Parameters**: hot_collection_name, warm_store_url
**Returns**: TieredVectorStore
**Description**: Create a TieredVectorStore instance.

    Args:
        hot_collection_name: Name for hot cache collection
        warm_store_url: URL for warm storage (Qdrant)

    Returns:
        Configured TieredVectorStore instance
    



## Function: __init__

**Parameters**: self, collection_name, max_memory_gb
**Description**: Initialize in-memory ChromaDB cache.

        Args:
            collection_name: Name of the collection to create
            max_memory_gb: Maximum memory allocation in GB (default: 8)
        



## Function: get_count

**Parameters**: self
**Returns**: int
**Description**: Get the number of documents in the cache.

        Returns:
            Number of documents currently in cache
        



## Function: clear

**Parameters**: self
**Returns**: bool
**Description**: Wipe cache to free RAM.

        Returns:
            True if successful, False otherwise
        



## Function: delete_collection

**Parameters**: self
**Returns**: bool
**Description**: Delete the entire collection.

        Returns:
            True if successful, False otherwise
        



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics.

        Returns:
            Dictionary with cache statistics
        



## Function: __init__

**Parameters**: self, hot_cache, warm_store_url
**Description**: Initialize tiered vector store.

        Args:
            hot_cache: In-memory cache instance
            warm_store_url: URL for warm storage (Qdrant)
        



## Usage Examples

### Class Usage

```python
# Using InMemoryVectorCache
inmemoryvectorcache = InMemoryVectorCache()
inmemoryvectorcache.get_count()
inmemoryvectorcache.clear()
```

```python
# Using TieredVectorStore
tieredvectorstore = TieredVectorStore()
```

### Function Usage

```python
# Using create_memory_vector_cache
result = create_memory_vector_cache(collection_name, max_memory_gb)
```

```python
# Using create_tiered_vector_store
result = create_tiered_vector_store(hot_collection_name, warm_store_url)
```

```python
# Using __init__
result = __init__(collection_name, max_memory_gb)
```



---
**Generated**: 2026-03-26T09:39:04.575063
**Type**: api_reference
**Quality**: comprehensive
