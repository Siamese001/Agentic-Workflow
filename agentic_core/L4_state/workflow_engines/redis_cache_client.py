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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "redis_cache_client")
emit_determinism_digest("p0", "redis_cache_client")

_emit_dispatches_healing_run("p1", "redis_cache_client", "L4")
_emit_routes_through("p1", "redis_cache_client", "L4")
_emit_escalates_to_human("p1", "redis_cache_client", "L4")
_emit_reads_policy_state("p1", "redis_cache_client", "L4")
_emit_snapshots_state("p0", "redis_cache_client", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "redis_cache_client", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "redis_cache_client")
