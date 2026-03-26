# API Documentation: discovery_cache

**Target Audience**: developers, api_users

# discovery_cache API Documentation

**File**: `discovery_cache.py`
**Classes**: 1
**Functions**: 5

## Classes

- **AgentDiscoveryCache**

## Functions

- **get_agent_discovery_cache** -> AgentDiscoveryCache
- **__init__**
- **get_or_fetch** -> list[dict[str, Any]]
- **_compute_file_hash** -> str
- **invalidate_all** -> None


## Class: AgentDiscoveryCache

**Description**: Cache for agent discovery JSON parsing.

    Eliminates repeated file I/O and JSON parsing for agent_discovery_full.json.
    Automatically invalidates when file content changes via content hash keying.
    

### Methods

#### __init__
**Parameters**: self, cache, ttl_seconds

#### get_or_fetch
**Parameters**: self, discovery_path, fetch_from_disk
**Returns**: list[dict[str, Any]]
**Description**: Read-through helper: return cached parsed agents or call *fetch_from_disk*.

        *fetch_from_disk* is a zero-argument callable that reads and parses the
        discovery JSON file.  Called only on cache miss or when file content changes.

        Args:
            discovery_path: Path to agent_discovery_full.json
            fetch_from_disk: Callable that returns list[dict] of agent records
            replay_mode: If True, bypass cache entirely

        Returns:
            List of agent discovery records

        Raises:
            FileNotFoundError: If discovery_path does not exist
        

#### _compute_file_hash
**Parameters**: self, path
**Returns**: str
**Description**: Compute SHA-256 hash of file contents for cache key.

#### invalidate_all
**Parameters**: self
**Returns**: None
**Description**: Invalidate all cached discovery data.

        Note: This is a no-op since cache keys are content-addressed.
        File changes automatically invalidate via different hash.
        



## Function: get_agent_discovery_cache

**Returns**: AgentDiscoveryCache
**Description**: Get the singleton agent discovery cache instance.



## Function: __init__

**Parameters**: self, cache, ttl_seconds


## Function: get_or_fetch

**Parameters**: self, discovery_path, fetch_from_disk
**Returns**: list[dict[str, Any]]
**Description**: Read-through helper: return cached parsed agents or call *fetch_from_disk*.

        *fetch_from_disk* is a zero-argument callable that reads and parses the
        discovery JSON file.  Called only on cache miss or when file content changes.

        Args:
            discovery_path: Path to agent_discovery_full.json
            fetch_from_disk: Callable that returns list[dict] of agent records
            replay_mode: If True, bypass cache entirely

        Returns:
            List of agent discovery records

        Raises:
            FileNotFoundError: If discovery_path does not exist
        



## Function: _compute_file_hash

**Parameters**: self, path
**Returns**: str
**Description**: Compute SHA-256 hash of file contents for cache key.



## Function: invalidate_all

**Parameters**: self
**Returns**: None
**Description**: Invalidate all cached discovery data.

        Note: This is a no-op since cache keys are content-addressed.
        File changes automatically invalidate via different hash.
        



## Usage Examples

### Class Usage

```python
# Using AgentDiscoveryCache
agentdiscoverycache = AgentDiscoveryCache()
agentdiscoverycache.get_or_fetch()
agentdiscoverycache.invalidate_all()
```

### Function Usage

```python
# Using get_agent_discovery_cache
result = get_agent_discovery_cache()
```

```python
# Using __init__
result = __init__(cache, ttl_seconds)
```

```python
# Using get_or_fetch
result = get_or_fetch(discovery_path, fetch_from_disk)
```



---
**Generated**: 2026-03-26T09:39:04.700266
**Type**: api_reference
**Quality**: comprehensive
