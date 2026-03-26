# API Documentation: schema_validator_cache

**Target Audience**: developers, api_users

# schema_validator_cache API Documentation

**File**: `schema_validator_cache.py`
**Classes**: 1
**Functions**: 5

## Classes

- **SchemaValidatorCache**

## Functions

- **get_schema_validator_cache** -> SchemaValidatorCache
- **__init__**
- **get_or_fetch** -> Any
- **_compute_schema_hash** -> str
- **invalidate** -> None


## Class: SchemaValidatorCache

**Description**: Cache for compiled JSON schema validators.

    Eliminates repeated schema compilation for the same schema definitions.
    Automatically invalidates when schema changes via content hash keying.
    

### Methods

#### __init__
**Parameters**: self, cache, ttl_seconds

#### get_or_fetch
**Parameters**: self, schema, fetch_validator
**Returns**: Any
**Description**: Read-through helper: return cached validator result or call *fetch_validator*.

        *fetch_validator* is a zero-argument callable that compiles and returns
        a validator function or validation result.  Called only on cache miss.

        Args:
            schema: JSON schema dict to validate against
            fetch_validator: Callable that returns compiled validator or validation result
            replay_mode: If True, bypass cache entirely

        Returns:
            Compiled validator or validation result

        Raises:
            ValueError: If schema is empty
        

#### _compute_schema_hash
**Parameters**: self, schema
**Returns**: str
**Description**: Compute deterministic hash of schema for cache key.

#### invalidate
**Parameters**: self, schema
**Returns**: None
**Description**: Invalidate cached validator for specific schema.

        Note: This is a no-op since cache keys are content-addressed.
        Schema changes automatically invalidate via different hash.
        



## Function: get_schema_validator_cache

**Returns**: SchemaValidatorCache
**Description**: Get the singleton schema validator cache instance.



## Function: __init__

**Parameters**: self, cache, ttl_seconds


## Function: get_or_fetch

**Parameters**: self, schema, fetch_validator
**Returns**: Any
**Description**: Read-through helper: return cached validator result or call *fetch_validator*.

        *fetch_validator* is a zero-argument callable that compiles and returns
        a validator function or validation result.  Called only on cache miss.

        Args:
            schema: JSON schema dict to validate against
            fetch_validator: Callable that returns compiled validator or validation result
            replay_mode: If True, bypass cache entirely

        Returns:
            Compiled validator or validation result

        Raises:
            ValueError: If schema is empty
        



## Function: _compute_schema_hash

**Parameters**: self, schema
**Returns**: str
**Description**: Compute deterministic hash of schema for cache key.



## Function: invalidate

**Parameters**: self, schema
**Returns**: None
**Description**: Invalidate cached validator for specific schema.

        Note: This is a no-op since cache keys are content-addressed.
        Schema changes automatically invalidate via different hash.
        



## Usage Examples

### Class Usage

```python
# Using SchemaValidatorCache
schemavalidatorcache = SchemaValidatorCache()
schemavalidatorcache.get_or_fetch()
schemavalidatorcache.invalidate()
```

### Function Usage

```python
# Using get_schema_validator_cache
result = get_schema_validator_cache()
```

```python
# Using __init__
result = __init__(cache, ttl_seconds)
```

```python
# Using get_or_fetch
result = get_or_fetch(schema, fetch_validator)
```



---
**Generated**: 2026-03-26T09:39:04.705859
**Type**: api_reference
**Quality**: comprehensive
