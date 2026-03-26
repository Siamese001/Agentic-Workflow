# API Documentation: batch_embedding_service

**Target Audience**: developers, api_users

# batch_embedding_service API Documentation

**File**: `batch_embedding_service.py`
**Classes**: 1
**Functions**: 5

## Classes

- **BatchEmbeddingService**

## Functions

- **create_batch_embedding_service** -> BatchEmbeddingService
- **__init__**
- **shutdown** -> Any
- **__enter__**
- **__exit__**


## Class: BatchEmbeddingService

**Description**: Service for parallel batch embedding generation.

    Optimized for i7-10750H (6 cores/12 threads).
    Keeps workers low to prevent context switching overhead.
    

### Methods

#### __init__
**Parameters**: self, batch_size, max_workers
**Description**: Initialize the batch embedding service.

        Args:
            batch_size: Number of texts to embed in a single batch (default: 32)
            max_workers: Number of parallel workers (default: 4 for i7-10750H)
        

#### shutdown
**Parameters**: self
**Returns**: Any
**Description**: Shutdown the thread pool executor.

#### __enter__
**Parameters**: self
**Description**: Context manager entry.

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Context manager exit.



## Function: create_batch_embedding_service

**Parameters**: batch_size, max_workers
**Returns**: BatchEmbeddingService
**Description**: Create a BatchEmbeddingService instance.

    Args:
        batch_size: Number of texts to embed in a single batch
        max_workers: Number of parallel workers

    Returns:
        Configured BatchEmbeddingService instance
    



## Function: __init__

**Parameters**: self, batch_size, max_workers
**Description**: Initialize the batch embedding service.

        Args:
            batch_size: Number of texts to embed in a single batch (default: 32)
            max_workers: Number of parallel workers (default: 4 for i7-10750H)
        



## Function: shutdown

**Parameters**: self
**Returns**: Any
**Description**: Shutdown the thread pool executor.



## Function: __enter__

**Parameters**: self
**Description**: Context manager entry.



## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Context manager exit.



## Usage Examples

### Class Usage

```python
# Using BatchEmbeddingService
batchembeddingservice = BatchEmbeddingService()
batchembeddingservice.shutdown()
```

### Function Usage

```python
# Using create_batch_embedding_service
result = create_batch_embedding_service(batch_size, max_workers)
```

```python
# Using __init__
result = __init__(batch_size, max_workers)
```

```python
# Using shutdown
result = shutdown()
```



---
**Generated**: 2026-03-26T09:39:03.757379
**Type**: api_reference
**Quality**: comprehensive
