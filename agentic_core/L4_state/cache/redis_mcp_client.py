"""
TOMBSTONED — L4 must not own its own Redis client.

All caching must go through ``agentic_core.cache.DeterministicRedisCache``
(``get_hot_cache()`` / ``get_coordination_cache()``).  Having a second
independent Redis connection inside L4 violates two architectural invariants:

  1. SINGLE CACHE CLIENT: Only one Redis client instance per process, owned
     by ``agentic_core/cache/``.  Duplicate clients create separate key-spaces,
     bypass the TCP pre-check, bypass the bounded LRU fallback, and bypass the
     TTL / value-size guards.

  2. L4 IS NOT A CACHE AUTHORITY: L4 is the persistence layer.  Any caching
     concern belongs at the seam layer (L0/L1/L2/L3/L5) via the typed seam
     classes in ``agentic_core/cache/``.

This file is intentionally left with no importable symbols.  If you reach
this file thinking you need a Redis client, import instead:

    from agentic_core.cache import get_hot_cache, get_coordination_cache
"""

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "redis_mcp_client")
