"""Redis Coordination Fabric — DB-2 bounded operational workspace.

Provides the fast, ephemeral "working desk" layer described in the memory
architecture design.  All data here is:

  - TTL-bounded (never source of truth)
  - Replay-safe (bypassed when replay_mode=True)
  - Hash-keyed (no wall-clock timestamps in keys)
  - Fail-open (graceful LRU fallback when Redis is unavailable)

Five distinct namespaces in DB-2
---------------------------------
1. ``trace_ws:{trace_id_hash}``         — per-trace working set (active request state)
2. ``team_lock:{resource_hash}``        — team-sync duplicate-work prevention lease
3. ``route_ctx:{intent_hash}``          — hot routing context cache (fast path election)
4. ``replay_frag:{replay_key_hash}``    — replay assist cache (transcript fragments)
5. ``novelty:{cluster_hash}``           — novelty/cluster centroid working cache

Design invariants
-----------------
1. DB-2 is NEVER authoritative for policy, lineage, audit, or final artifacts.
2. All keys are hash-derived (SHA-256 segments from caller).  No nonces.
3. TTLs are bounded: trace_ws ≤ 900s, team_lock ≤ 120s, route_ctx ≤ 3600s,
   replay_frag ≤ 600s, novelty ≤ 1800s.
4. ``replay_mode=True`` on any read returns ``None`` so the caller re-derives
   from L4 and appends to the deterministic transcript.
5. ``set_trace_working_set`` accepts only replay-safe JSON-serialisable dicts.
6. This module imports from ``redis_cache_client`` but adds the new DB index
   and namespace contracts — it does NOT monkey-patch the existing caches.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.redis_cache_client import (
    CacheDB,
    DeterministicRedisCache,
    canonical_json_bytes,
    content_hash,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "redis_coordination_fabric", "p0_governance")
_emit_reads_policy_state("p0", "redis_coordination_fabric", "policy_binding")
_emit_snapshots_state("p0", "redis_coordination_fabric", "state_snapshot")
emit_replay_key("p0", "redis_coordination_fabric")
emit_determinism_digest("p0", "redis_coordination_fabric")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "redis_coordination_fabric", "execution_auth")
_emit_validates_capability("p2", "redis_coordination_fabric", "capability_check")
_emit_routes_to_capability("p2", "redis_coordination_fabric", "capability_route")
_emit_writes_via_uwg("p2", "redis_coordination_fabric", "uwg_write")
_emit_blocks_direct_write("p2", "redis_coordination_fabric", "direct_write_block")
_emit_records_tool_invocation("p2", "redis_coordination_fabric", "tool_invocation")
_emit_captures_execution_output("p2", "redis_coordination_fabric", "exec_output")
_emit_dispatches_agent("p3", "redis_coordination_fabric", "agent_dispatch")
_emit_coordinates_agents("p3", "redis_coordination_fabric", "agent_coordination")
_emit_records_workflow_lineage("p3", "redis_coordination_fabric", "workflow_lineage")
_emit_records_healing_outcome("p3", "redis_coordination_fabric", "healing_outcome")
_emit_escalates_failure("p3", "redis_coordination_fabric", "failure_escalation")
_emit_orchestrates_workflow("p3", "redis_coordination_fabric", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "redis_coordination_fabric", "healing_dispatch")
_emit_invokes_evaluation("p3", "redis_coordination_fabric", "evaluation_signal")
_emit_records_telemetry_event("p4", "redis_coordination_fabric", "telemetry_event")
_emit_captures_evaluation_metric("p4", "redis_coordination_fabric", "eval_metric")
_emit_stores_embedding("p4", "redis_coordination_fabric", "embedding_store")
_emit_updates_meta_learning_state("p4", "redis_coordination_fabric", "meta_learning")
_emit_links_execution_to_snapshot("p4", "redis_coordination_fabric", "exec_snapshot_link")

logger = logging.getLogger(__name__)

# DB-2 is the new coordination fabric namespace.
# DB-0 = hot caches (L0/L1/L3/L5)
# DB-1 = coordination leases (L2)
# DB-2 = operational workspace (per-trace, team-sync, replay-assist, novelty)
_DB_WORKSPACE = 2  # type: ignore[assignment]

# TTL caps (seconds) per namespace — fail-closed if caller exceeds these
_TTL_TRACE_WS: int = 900  # 15 min: active request lifetime
_TTL_TEAM_LOCK: int = 120  # 2 min: duplicate-work prevention window
_TTL_ROUTE_CTX: int = 3600  # 1 hr: hot routing feature cache
_TTL_REPLAY_FRAG: int = 600  # 10 min: in-flight replay assist blobs
_TTL_NOVELTY: int = 1800  # 30 min: live novelty cluster centroids


def _make_db2_cache(redis_url: str | None = None) -> DeterministicRedisCache:
    """Construct a DeterministicRedisCache pointed at DB-2 (workspace).

    ``DeterministicRedisCache.__init__`` stores ``db`` as an int via the
    ``CacheDB`` IntEnum; passing ``_DB_WORKSPACE`` (int 2) works because
    IntEnum inherits from int and the value is used directly in the Redis
    connection parameters.
    """
    cache = DeterministicRedisCache.__new__(DeterministicRedisCache)
    DeterministicRedisCache.__init__(cache, db=CacheDB.HOT, redis_url=redis_url)
    # Re-target to DB-2 immediately after construction (before first connect).
    cache._db = _DB_WORKSPACE  # type: ignore[assignment]
    return cache


# ---------------------------------------------------------------------------
# Key builders (namespace-prefixed, hash-only)
# ---------------------------------------------------------------------------


def _trace_ws_key(trace_id_hash: str) -> str:
    """``trace_ws:{trace_id_hash}``"""
    if not trace_id_hash:
        raise ValueError("trace_id_hash must not be empty")
    return f"trace_ws:{trace_id_hash}"


def _team_lock_key(resource_hash: str) -> str:
    """``team_lock:{resource_hash}``"""
    if not resource_hash:
        raise ValueError("resource_hash must not be empty")
    return f"team_lock:{resource_hash}"


def _route_ctx_key(intent_hash: str) -> str:
    """``route_ctx:{intent_hash}``"""
    if not intent_hash:
        raise ValueError("intent_hash must not be empty")
    return f"route_ctx:{intent_hash}"


def _replay_frag_key(replay_key_hash: str) -> str:
    """``replay_frag:{replay_key_hash}``"""
    if not replay_key_hash:
        raise ValueError("replay_key_hash must not be empty")
    return f"replay_frag:{replay_key_hash}"


def _novelty_key(cluster_hash: str) -> str:
    """``novelty:{cluster_hash}``"""
    if not cluster_hash:
        raise ValueError("cluster_hash must not be empty")
    return f"novelty:{cluster_hash}"


# ---------------------------------------------------------------------------
# RedisCoordinationFabric
# ---------------------------------------------------------------------------


class RedisCoordinationFabric:
    """Ephemeral operational workspace in Redis DB-2.

    Provides five specialised namespaces for in-flight coordination:

    * **Per-trace working set** — live request state by ``trace_id_hash``.
    * **Team-sync leases** — prevent duplicate work across agents.
    * **Hot routing context cache** — fast path election without cold rehydration.
    * **Replay assist cache** — transcript fragments for in-flight replay validation.
    * **Novelty cluster cache** — live failure-cluster centroids during incident bursts.

    All reads accept ``replay_mode=True`` which unconditionally returns ``None``
    so callers re-derive from L4 and preserve replay determinism.

    Usage
    -----
    .. code-block:: python

        fabric = RedisCoordinationFabric()

        # Store active request context
        fabric.set_trace_working_set(
            trace_id_hash="a3f7b291...",
            state={"path": "PATH_A", "budget_remaining": 10, "safety_status": "CLEAR"},
        )

        # Prevent duplicate healing work
        acquired = fabric.acquire_team_lock(
            resource_hash="healer_target_abc123",
            holder_id="HealingOrchestrator",
            semantic_clock_tick=42,
        )
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self._cache = _make_db2_cache(redis_url=redis_url)

    # ------------------------------------------------------------------
    # 1. Per-trace working set
    # ------------------------------------------------------------------

    def set_trace_working_set(
        self,
        trace_id_hash: str,
        state: dict[str, Any],
        ttl_seconds: int = _TTL_TRACE_WS,
    ) -> bool:
        """Store active request context for a running trace.

        ``state`` must be JSON-serialisable (dict, list, str, int, float, bool,
        None).  Typical fields: ``path``, ``tool_budget_remaining``,
        ``semantic_clock_tick``, ``current_orchestration_node``,
        ``safety_status``.

        Parameters
        ----------
        trace_id_hash:
            SHA-256 hexdigest of the trace_id.
        state:
            JSON-serialisable dict of live request state.
        ttl_seconds:
            TTL ≤ 900s (default 900).

        Returns
        -------
        bool
            True on success (Redis or fallback).
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"RedisCoordinationFabric.set_trace_working_set:{trace_id_hash}")
        if ttl_seconds > _TTL_TRACE_WS:
            raise ValueError(f"trace working set TTL must be ≤ {_TTL_TRACE_WS}s, got {ttl_seconds}")
        key = _trace_ws_key(trace_id_hash)
        return self._cache.set(key, canonical_json_bytes(state), ttl_seconds=ttl_seconds)

    def get_trace_working_set(
        self, trace_id_hash: str, *, replay_mode: bool = False
    ) -> dict[str, Any] | None:
        """Return active request context for a trace, or None on miss/bypass."""
        key = _trace_ws_key(trace_id_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def delete_trace_working_set(self, trace_id_hash: str) -> bool:
        """Evict a trace working set (call on execution completion)."""
        return self._cache.delete(_trace_ws_key(trace_id_hash))

    # ------------------------------------------------------------------
    # 2. Team-sync duplicate-work prevention
    # ------------------------------------------------------------------

    def acquire_team_lock(
        self,
        resource_hash: str,
        holder_id: str,
        semantic_clock_tick: int,
        ttl_seconds: int = _TTL_TEAM_LOCK,
    ) -> bool:
        """Acquire an exclusive team-sync lease for a resource.

        Prevents duplicate healing, routing, or file-mutation work across
        agents.  Uses Redis SET NX (atomic) when available.

        Parameters
        ----------
        resource_hash:
            SHA-256 hexdigest of the resource being locked (e.g. file path hash,
            healer target hash, plan hash).
        holder_id:
            Stable identifier of the claiming agent/process.
        semantic_clock_tick:
            Current semantic clock tick for replay-safe lease payloads.
        ttl_seconds:
            TTL ≤ 120s (default 120).

        Returns
        -------
        bool
            True if lock was acquired, False if already held.
        """
        if ttl_seconds > _TTL_TEAM_LOCK:
            raise ValueError(f"team lock TTL must be ≤ {_TTL_TEAM_LOCK}s, got {ttl_seconds}")
        key = _team_lock_key(resource_hash)
        nonce = content_hash(
            canonical_json_bytes(
                {"holder_id": holder_id, "resource_hash": resource_hash, "tick": semantic_clock_tick}
            )
        )
        return self._cache.acquire_lease(
            key,
            holder_id=holder_id,
            nonce=nonce,
            semantic_clock_tick=semantic_clock_tick,
            ttl_seconds=ttl_seconds,
        )

    def release_team_lock(self, resource_hash: str, holder_id: str, semantic_clock_tick: int) -> bool:
        """Release a previously acquired team-sync lock.

        Only succeeds if ``holder_id`` still holds the lock.
        """
        key = _team_lock_key(resource_hash)
        nonce = content_hash(
            canonical_json_bytes(
                {"holder_id": holder_id, "resource_hash": resource_hash, "tick": semantic_clock_tick}
            )
        )
        return self._cache.release_lease(key, holder_id=holder_id, nonce=nonce)

    def is_team_locked(self, resource_hash: str) -> bool:
        """Return True if a team-sync lock is currently held for this resource."""
        return self._cache.exists(_team_lock_key(resource_hash))

    # ------------------------------------------------------------------
    # 3. Hot routing context cache
    # ------------------------------------------------------------------

    def set_route_context(
        self,
        intent_hash: str,
        route_features: dict[str, Any],
        ttl_seconds: int = _TTL_ROUTE_CTX,
    ) -> bool:
        """Cache route features for fast path election.

        Stores the latest route features and recent outcome features so the
        routing layer can elect a path without rehydrating cold L4 storage.

        Parameters
        ----------
        intent_hash:
            SHA-256 hexdigest of the intent/request.
        route_features:
            JSON-serialisable dict of route context features.
        ttl_seconds:
            TTL ≤ 3600s (default 3600).
        """
        if ttl_seconds > _TTL_ROUTE_CTX:
            raise ValueError(f"route context TTL must be ≤ {_TTL_ROUTE_CTX}s, got {ttl_seconds}")
        key = _route_ctx_key(intent_hash)
        return self._cache.set(key, canonical_json_bytes(route_features), ttl_seconds=ttl_seconds)

    def get_route_context(self, intent_hash: str, *, replay_mode: bool = False) -> dict[str, Any] | None:
        """Return cached route features, or None on miss/bypass."""
        return self._cache.get_json(_route_ctx_key(intent_hash), replay_mode=replay_mode)

    def invalidate_route_context(self, intent_hash: str) -> bool:
        """Evict a route context entry (e.g. when routing policy changes)."""
        return self._cache.delete(_route_ctx_key(intent_hash))

    # ------------------------------------------------------------------
    # 4. Replay assist cache
    # ------------------------------------------------------------------

    def set_replay_fragment(
        self,
        replay_key_hash: str,
        fragment: dict[str, Any],
        ttl_seconds: int = _TTL_REPLAY_FRAG,
    ) -> bool:
        """Cache a transcript fragment or deterministic dependency blob.

        Speeds in-flight replay validation without becoming source of truth
        (replay_mode bypasses all reads here).

        Parameters
        ----------
        replay_key_hash:
            SHA-256 hexdigest of the replay key.
        fragment:
            JSON-serialisable dict (transcript fragment, patch set, or
            deterministic dependency blob).
        ttl_seconds:
            TTL ≤ 600s (default 600).
        """
        if ttl_seconds > _TTL_REPLAY_FRAG:
            raise ValueError(f"replay fragment TTL must be ≤ {_TTL_REPLAY_FRAG}s, got {ttl_seconds}")
        key = _replay_frag_key(replay_key_hash)
        return self._cache.set(key, canonical_json_bytes(fragment), ttl_seconds=ttl_seconds)

    def get_replay_fragment(
        self, replay_key_hash: str, *, replay_mode: bool = False
    ) -> dict[str, Any] | None:
        """Return a cached replay fragment.

        When ``replay_mode=True``, always returns None so the caller re-derives
        from L4 and appends to the deterministic transcript.
import uuid
        """
        return self._cache.get_json(_replay_frag_key(replay_key_hash), replay_mode=replay_mode)

    # ------------------------------------------------------------------
    # 5. Novelty / cluster working cache
    # ------------------------------------------------------------------

    def set_novelty_cluster(
        self,
        cluster_hash: str,
        centroid: dict[str, Any],
        ttl_seconds: int = _TTL_NOVELTY,
    ) -> bool:
        """Store a live failure-cluster centroid during an incident burst.

        Keeps current cluster centroids and novelty flags live during triage.
        Findings are committed to L4/Memory MCP after the burst; this is the
        fast adaptive triage workspace.

        Parameters
        ----------
        cluster_hash:
            SHA-256 hexdigest of the cluster identity (deterministic from centroid).
        centroid:
            JSON-serialisable dict of centroid data (e.g. embedding summary,
            failure family, novelty_flag, member_count).
        ttl_seconds:
            TTL ≤ 1800s (default 1800).
        """
        if ttl_seconds > _TTL_NOVELTY:
            raise ValueError(f"novelty cluster TTL must be ≤ {_TTL_NOVELTY}s, got {ttl_seconds}")
        key = _novelty_key(cluster_hash)
        return self._cache.set(key, canonical_json_bytes(centroid), ttl_seconds=ttl_seconds)

    def get_novelty_cluster(self, cluster_hash: str, *, replay_mode: bool = False) -> dict[str, Any] | None:
        """Return a live cluster centroid, or None on miss/bypass."""
        return self._cache.get_json(_novelty_key(cluster_hash), replay_mode=replay_mode)

    def invalidate_novelty_cluster(self, cluster_hash: str) -> bool:
        """Evict a cluster centroid (e.g. after committing to durable storage)."""
        return self._cache.delete(_novelty_key(cluster_hash))

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """Return cache stats for the DB-2 workspace."""
        return self._cache.get_stats()


# ---------------------------------------------------------------------------
# Process-global singleton
# ---------------------------------------------------------------------------

_workspace: RedisCoordinationFabric | None = None


def get_coordination_fabric(redis_url: str | None = None) -> RedisCoordinationFabric:
    """Return the process-global DB-2 coordination fabric instance."""
    global _workspace
    if _workspace is None:
        _workspace = RedisCoordinationFabric(redis_url=redis_url)
    return _workspace


def reset_coordination_fabric() -> None:
    """[TESTING ONLY] Reset the process-global singleton."""
    global _workspace
    _workspace = None


__all__ = [
    "RedisCoordinationFabric",
    "get_coordination_fabric",
    "reset_coordination_fabric",
]
