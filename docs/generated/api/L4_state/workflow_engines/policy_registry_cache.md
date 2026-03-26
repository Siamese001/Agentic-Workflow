# API Documentation: policy_registry_cache

**Target Audience**: developers, api_users

# policy_registry_cache API Documentation

**File**: `policy_registry_cache.py`
**Classes**: 1
**Functions**: 4

## Classes

- **PolicyRegistryCache**

## Functions

- **get_policy_registry_cache** -> PolicyRegistryCache
- **__init__**
- **get_or_fetch** -> dict[str, Any]
- **invalidate** -> None


## Class: PolicyRegistryCache

**Description**: Cache for sovereign policy registry lookups.

    Eliminates repeated policy registry scans for the same policy IDs.
    Policies are immutable, so cache is long-lived.
    

### Methods

#### __init__
**Parameters**: self, cache, ttl_seconds

#### get_or_fetch
**Parameters**: self, policy_id, fetch_policy
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached policy or call *fetch_policy*.

        *fetch_policy* is a zero-argument callable that fetches the policy
        definition from the registry.  Called only on cache miss.

        Args:
            policy_id: Unique policy identifier (e.g., "GOV-001")
            fetch_policy: Callable that returns policy definition dict
            replay_mode: If True, bypass cache entirely

        Returns:
            Policy definition dict
        

#### invalidate
**Parameters**: self, policy_id
**Returns**: None
**Description**: Invalidate cached policy for specific ID.



## Function: get_policy_registry_cache

**Returns**: PolicyRegistryCache
**Description**: Get the singleton policy registry cache instance.



## Function: __init__

**Parameters**: self, cache, ttl_seconds


## Function: get_or_fetch

**Parameters**: self, policy_id, fetch_policy
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached policy or call *fetch_policy*.

        *fetch_policy* is a zero-argument callable that fetches the policy
        definition from the registry.  Called only on cache miss.

        Args:
            policy_id: Unique policy identifier (e.g., "GOV-001")
            fetch_policy: Callable that returns policy definition dict
            replay_mode: If True, bypass cache entirely

        Returns:
            Policy definition dict
        



## Function: invalidate

**Parameters**: self, policy_id
**Returns**: None
**Description**: Invalidate cached policy for specific ID.



## Usage Examples

### Class Usage

```python
# Using PolicyRegistryCache
policyregistrycache = PolicyRegistryCache()
policyregistrycache.get_or_fetch()
policyregistrycache.invalidate()
```

### Function Usage

```python
# Using get_policy_registry_cache
result = get_policy_registry_cache()
```

```python
# Using __init__
result = __init__(cache, ttl_seconds)
```

```python
# Using get_or_fetch
result = get_or_fetch(policy_id, fetch_policy)
```



---
**Generated**: 2026-03-26T09:39:04.702352
**Type**: api_reference
**Quality**: comprehensive
