# API Documentation: cache_invalidation_util

**Target Audience**: developers, api_users

# cache_invalidation_util API Documentation

**File**: `cache_invalidation_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **heal_invalidate_cache**
- **invalidate_on_file_change**
- **decorator**
- **decorator**


## Function: heal_invalidate_cache

**Parameters**: pattern
**Description**: 
    Decorator to invalidate cache after successful heal operation.

    Args:
        pattern: cache key pattern to invalidate (e.g., "canon:*", "compliance:*")
                 Empty string invalidates all keys for the agent's prefix.

    Usage:
        @heal_invalidate_cache("canon:*")
        async def heal_repository(self) -> dict:
            ...
    



## Function: invalidate_on_file_change

**Parameters**: file_path_arg
**Description**: 
    Decorator to invalidate cache entries related to a specific file after modification.

    Args:
        file_path_arg: Name of the argument containing the file path

    Usage:
        @invalidate_on_file_change("file_path")
        async def modify_file(self, file_path: Path) -> dict:
            ...
    



## Function: decorator

**Parameters**: func


## Function: decorator

**Parameters**: func


## Usage Examples

### Function Usage

```python
# Using heal_invalidate_cache
result = heal_invalidate_cache(pattern)
```

```python
# Using invalidate_on_file_change
result = invalidate_on_file_change(file_path_arg)
```

```python
# Using decorator
result = decorator(func)
```



---
**Generated**: 2026-03-26T09:39:05.606252
**Type**: api_reference
**Quality**: comprehensive
