"""
TOMBSTONED — Duplicate of canonical Redis client.

This file is a duplicate of the canonical Redis cache client located at:
    agentic_core/cache/redis_cache_client.py

Having multiple Redis client implementations violates the single-client invariant:
  1. SINGLE CACHE CLIENT: Only one Redis client instance per process, owned
     by ``agentic_core/cache/``.  Duplicate clients create separate key-spaces,
     bypass the TCP pre-check, bypass the bounded LRU fallback, and bypass the
     TTL / value-size guards.

  2. L4 IS NOT A CACHE AUTHORITY: L4 is the persistence layer.  Any caching
     concern belongs at the seam layer (L0/L1/L2/L3/L5) via the typed seam
     classes in ``agentic_core/cache/``.

This file is intentionally left with no importable symbols.  If you reach
this file thinking you need a Redis client, import instead:

    from agentic_core.cache.redis_cache_client import get_hot_cache, get_coordination_cache
"""
