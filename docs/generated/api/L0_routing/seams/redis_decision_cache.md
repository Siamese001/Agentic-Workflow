# API Documentation: redis_decision_cache

**Target Audience**: developers, api_users

# redis_decision_cache API Documentation

**File**: `redis_decision_cache.py`
**Classes**: 3
**Functions**: 18

## Classes

- **RouteDecisionCache**
- **RoutingRuleSurfaceCache**
- **CapabilityRegistryCache**

## Functions

- **get_route_decision_cache** -> RouteDecisionCache
- **get_routing_rule_surface_cache** -> RoutingRuleSurfaceCache
- **get_cap_registry_cache** -> CapabilityRegistryCache
- **__init__** -> None
- **get** -> dict[str, Any] | None
- **set** -> None
- **get_or_fetch** -> dict[str, Any]
- **invalidate** -> None
- **__init__** -> None
- **get** -> dict[str, Any] | None
- **set** -> None
- **get_or_fetch** -> dict[str, Any]
- **invalidate** -> None
- **__init__** -> None
- **get** -> dict[str, Any] | None
- **set** -> None
- **get_or_fetch** -> dict[str, Any]
- **invalidate** -> None


## Class: RouteDecisionCache

**Description**: Memoises ``RouteDecisionArtifact`` JSON for identical L0 inputs.

    The value stored is the canonical JSON representation of the artifact's
    serialisable fields.  Callers are responsible for deserialising back to
    the typed artifact.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    

### Methods

#### __init__
**Parameters**: self, ttl_seconds, cache
**Returns**: None

#### get
**Parameters**: self, intent_hash, policy_hash, routing_state_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached route-decision dict or ``None`` on miss/bypass.

#### set
**Parameters**: self, intent_hash, policy_hash, routing_state_hash, artifact_dict
**Returns**: None
**Description**: Cache *artifact_dict* under the deterministic key.

        ``artifact_dict`` must be the canonical JSON-serialisable
        representation of a ``RouteDecisionArtifact`` — callers must
        produce it from the typed artifact before calling this method.
        

#### get_or_fetch
**Parameters**: self, intent_hash, policy_hash, routing_state_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached result or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the
        ``RouteDecisionArtifact`` dict by re-deriving it from L4.  It is
        called **only** on a cache miss.  The result is stored before return.

        This is the canonical wiring point for L0 routing engines.  Engines
        should call this instead of calling ``get()`` and L4 separately.

        Parameters
        ----------
        intent_hash, policy_hash, routing_state_hash:
            Hash inputs that fully determine the routing decision.
        fetch_from_l4:
            Zero-argument callable returning ``dict[str, Any]``.
        replay_mode:
            Pass ``True`` during replay to force re-derivation from L4.
        

#### invalidate
**Parameters**: self, intent_hash, policy_hash, routing_state_hash
**Returns**: None
**Description**: Explicitly evict a cached decision.



## Class: RoutingRuleSurfaceCache

**Description**: Read-only mirror of the active routing-ruleset snapshot from L4.

    This cache is NEVER a source of truth.  The ruleset is fetched from L4
    on every miss; on a hit the cached bytes are returned as a convenience.

    Parameters
    ----------
    ttl_seconds:
        TTL applied when the L4 snapshot is written into Redis.
    cache:
        Override the shared hot-cache instance (useful for testing).
    

### Methods

#### __init__
**Parameters**: self, ttl_seconds, cache
**Returns**: None

#### get
**Parameters**: self, routing_state_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached ruleset dict or ``None`` on miss/bypass.

#### set
**Parameters**: self, routing_state_hash, ruleset
**Returns**: None
**Description**: Write *ruleset* (a canonical JSON dict from L4) into the mirror.

#### get_or_fetch
**Parameters**: self, routing_state_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached ruleset or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        ruleset dict from L4.  Called only on a cache miss; result is stored.
        

#### invalidate
**Parameters**: self, routing_state_hash
**Returns**: None
**Description**: Evict the cached ruleset.



## Class: CapabilityRegistryCache

**Description**: Mirrors the tool-inventory / capability-registry snapshot from L4.

    Value holds allowlists, tool availability booleans, and rate-limit
    envelopes.  This cache is informational — routing decisions that depend
    on capability availability must re-verify against L4 when this cache is
    cold.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied when a registry snapshot is stored.
    cache:
        Override the shared hot-cache instance (useful for testing).
    

### Methods

#### __init__
**Parameters**: self, ttl_seconds, cache
**Returns**: None

#### get
**Parameters**: self, cap_registry_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached capability registry or ``None`` on miss/bypass.

#### set
**Parameters**: self, cap_registry_hash, registry
**Returns**: None
**Description**: Store *registry* (canonical JSON dict from L4) in the mirror.

#### get_or_fetch
**Parameters**: self, cap_registry_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached registry or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        capability registry dict from L4.  Called only on a cache miss.
        

#### invalidate
**Parameters**: self, cap_registry_hash
**Returns**: None
**Description**: Evict the cached registry snapshot.



## Function: get_route_decision_cache

**Returns**: RouteDecisionCache


## Function: get_routing_rule_surface_cache

**Returns**: RoutingRuleSurfaceCache


## Function: get_cap_registry_cache

**Returns**: CapabilityRegistryCache


## Function: __init__

**Parameters**: self, ttl_seconds, cache
**Returns**: None


## Function: get

**Parameters**: self, intent_hash, policy_hash, routing_state_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached route-decision dict or ``None`` on miss/bypass.



## Function: set

**Parameters**: self, intent_hash, policy_hash, routing_state_hash, artifact_dict
**Returns**: None
**Description**: Cache *artifact_dict* under the deterministic key.

        ``artifact_dict`` must be the canonical JSON-serialisable
        representation of a ``RouteDecisionArtifact`` — callers must
        produce it from the typed artifact before calling this method.
        



## Function: get_or_fetch

**Parameters**: self, intent_hash, policy_hash, routing_state_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached result or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the
        ``RouteDecisionArtifact`` dict by re-deriving it from L4.  It is
        called **only** on a cache miss.  The result is stored before return.

        This is the canonical wiring point for L0 routing engines.  Engines
        should call this instead of calling ``get()`` and L4 separately.

        Parameters
        ----------
        intent_hash, policy_hash, routing_state_hash:
            Hash inputs that fully determine the routing decision.
        fetch_from_l4:
            Zero-argument callable returning ``dict[str, Any]``.
        replay_mode:
            Pass ``True`` during replay to force re-derivation from L4.
        



## Function: invalidate

**Parameters**: self, intent_hash, policy_hash, routing_state_hash
**Returns**: None
**Description**: Explicitly evict a cached decision.



## Function: __init__

**Parameters**: self, ttl_seconds, cache
**Returns**: None


## Function: get

**Parameters**: self, routing_state_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached ruleset dict or ``None`` on miss/bypass.



## Function: set

**Parameters**: self, routing_state_hash, ruleset
**Returns**: None
**Description**: Write *ruleset* (a canonical JSON dict from L4) into the mirror.



## Function: get_or_fetch

**Parameters**: self, routing_state_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached ruleset or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        ruleset dict from L4.  Called only on a cache miss; result is stored.
        



## Function: invalidate

**Parameters**: self, routing_state_hash
**Returns**: None
**Description**: Evict the cached ruleset.



## Function: __init__

**Parameters**: self, ttl_seconds, cache
**Returns**: None


## Function: get

**Parameters**: self, cap_registry_hash
**Returns**: dict[str, Any] | None
**Description**: Return the cached capability registry or ``None`` on miss/bypass.



## Function: set

**Parameters**: self, cap_registry_hash, registry
**Returns**: None
**Description**: Store *registry* (canonical JSON dict from L4) in the mirror.



## Function: get_or_fetch

**Parameters**: self, cap_registry_hash, fetch_from_l4
**Returns**: dict[str, Any]
**Description**: Read-through helper: return cached registry or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        capability registry dict from L4.  Called only on a cache miss.
        



## Function: invalidate

**Parameters**: self, cap_registry_hash
**Returns**: None
**Description**: Evict the cached registry snapshot.



## Usage Examples

### Class Usage

```python
# Using RouteDecisionCache
routedecisioncache = RouteDecisionCache()
routedecisioncache.get()
routedecisioncache.set()
```

```python
# Using RoutingRuleSurfaceCache
routingrulesurfacecache = RoutingRuleSurfaceCache()
routingrulesurfacecache.get()
routingrulesurfacecache.set()
```

```python
# Using CapabilityRegistryCache
capabilityregistrycache = CapabilityRegistryCache()
capabilityregistrycache.get()
capabilityregistrycache.set()
```

### Function Usage

```python
# Using get_route_decision_cache
result = get_route_decision_cache()
```

```python
# Using get_routing_rule_surface_cache
result = get_routing_rule_surface_cache()
```

```python
# Using get_cap_registry_cache
result = get_cap_registry_cache()
```



---
**Generated**: 2026-03-26T09:39:03.406054
**Type**: api_reference
**Quality**: comprehensive
