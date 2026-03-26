# API Documentation: config_file_cache

**Target Audience**: developers, api_users

# config_file_cache API Documentation

**File**: `config_file_cache.py`
**Classes**: 1
**Functions**: 5

## Classes

- **ConfigFileCache**

## Functions

- **get_config_file_cache** -> ConfigFileCache
- **__init__**
- **get_or_fetch** -> dict[str, Any]
- **_compute_file_hash** -> str
- **invalidate** -> None


## Class: ConfigFileCache

**Description**: Cache for parsed YAML/JSON configuration files.

    Eliminates repeated file I/O and parsing for the same config files.
    Automatically invalidates when file content changes via content hash keying.
    

### Methods

#### __init__
**Parameters**: self, cache, ttl_seconds

#### get_or_fetch
**Parameters**: self, config_path, fetch_from_disk
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached parsed config or call *fetch_from_disk*.

        *fetch_from_disk* is a zero-argument callable that reads and parses the
        config file.  Called only on cache miss or when file content changes.

        Args:
            config_path: Path to YAML/JSON config file
            fetch_from_disk: Callable that returns parsed config dict
            replay_mode: If True, bypass cache entirely

        Returns:
            Parsed configuration dict

        Raises:
            FileNotFoundError: If config_path does not exist
        

#### _compute_file_hash
**Parameters**: self, path
**Returns**: str
**Description**: Compute SHA-256 hash of file contents for cache key.

#### invalidate
**Parameters**: self, config_path
**Returns**: None
**Description**: Invalidate cached config for specific file.

        Note: This is a no-op since cache keys are content-addressed.
        File changes automatically invalidate via different hash.
        



## Function: get_config_file_cache

**Returns**: ConfigFileCache
**Description**: Get the singleton config file cache instance.



## Function: __init__

**Parameters**: self, cache, ttl_seconds


## Function: get_or_fetch

**Parameters**: self, config_path, fetch_from_disk
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached parsed config or call *fetch_from_disk*.

        *fetch_from_disk* is a zero-argument callable that reads and parses the
        config file.  Called only on cache miss or when file content changes.

        Args:
            config_path: Path to YAML/JSON config file
            fetch_from_disk: Callable that returns parsed config dict
            replay_mode: If True, bypass cache entirely

        Returns:
            Parsed configuration dict

        Raises:
            FileNotFoundError: If config_path does not exist
        



## Function: _compute_file_hash

**Parameters**: self, path
**Returns**: str
**Description**: Compute SHA-256 hash of file contents for cache key.



## Function: invalidate

**Parameters**: self, config_path
**Returns**: None
**Description**: Invalidate cached config for specific file.

        Note: This is a no-op since cache keys are content-addressed.
        File changes automatically invalidate via different hash.
        



## Usage Examples

### Class Usage

```python
# Using ConfigFileCache
configfilecache = ConfigFileCache()
configfilecache.get_or_fetch()
configfilecache.invalidate()
```

### Function Usage

```python
# Using get_config_file_cache
result = get_config_file_cache()
```

```python
# Using __init__
result = __init__(cache, ttl_seconds)
```

```python
# Using get_or_fetch
result = get_or_fetch(config_path, fetch_from_disk)
```



---
**Generated**: 2026-03-26T09:39:04.697624
**Type**: api_reference
**Quality**: comprehensive
