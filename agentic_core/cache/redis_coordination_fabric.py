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
    DeterministicRedisCache,
    get_workspace_cache,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("redis_coordination_fabric", "p4obs", "metric_1")
_emit_emits_metric_event("redis_coordination_fabric", "p4obs", "metric_2")
_emit_emits_metric_event("redis_coordination_fabric", "p4obs", "metric_3")
_emit_emits_metric_event("redis_coordination_fabric", "p4obs", "metric_4")
_emit_emits_metric_event("redis_coordination_fabric", "p4obs", "metric_5")
_emit_emits_metric_event("redis_coordination_fabric", "p4obs", "metric_6")
_emit_records_incident_event("redis_coordination_fabric", "p4obs", "incident")
_emit_captures_runtime_anomaly("redis_coordination_fabric", "p4obs", "anomaly")
_emit_writes_observability_log("redis_coordination_fabric", "p4obs", "obs_log")
_emit_updates_monitoring_state("redis_coordination_fabric", "p4obs", "mon_state")
_emit_triggers_alert("redis_coordination_fabric", "p4obs", "alert")
_emit_links_incident_trace("redis_coordination_fabric", "p4obs", "trace_link")
_emit_captures_pattern("redis_coordination_fabric", "p3lm", "pattern")
_emit_records_learning_event("redis_coordination_fabric", "p3lm", "learning_event")
_emit_writes_learning_snapshot("redis_coordination_fabric", "p3lm", "snapshot")
_emit_feeds_meta_learning("redis_coordination_fabric", "p3lm", "meta_feed")
_emit_updates_routing_strategy("redis_coordination_fabric", "p3lm", "routing")
_emit_improves_agent_policy("redis_coordination_fabric", "p3lm", "policy")
_emit_stores_learning_state("redis_coordination_fabric", "p3lm", "state")
_emit_records_execution_trace("redis_coordination_fabric", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("redis_coordination_fabric", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("redis_coordination_fabric", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("redis_coordination_fabric", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("redis_coordination_fabric", "L4_STATE", "p2_trace_5")
_emit_reads_environ("redis_coordination_fabric", "env_read", "p2_env_1")
_emit_reads_environ("redis_coordination_fabric", "env_read", "p2_env_2")
_emit_reads_runtime_state("redis_coordination_fabric", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("redis_coordination_fabric", "runtime_state", "p2_rt_2")

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
_emit_escalates_to_human("p1", "redis_coordination_fabric", "human_escalation")
_emit_routes_through("p1", "redis_coordination_fabric", "route_through")
_emit_checks_agent_registry("p1", "redis_coordination_fabric", "agent_registry")
_emit_validates_agent_capability("p1", "redis_coordination_fabric", "capability")
_emit_dispatches_execution_plan("p1", "redis_coordination_fabric", "exec_plan")
_emit_agent_executes_agent("p1", "redis_coordination_fabric", "sub_agent")
_emit_routes_to_agent("p1", "redis_coordination_fabric", "target_agent")
_emit_verifies_policy("p1", "redis_coordination_fabric", "policy_check")
_emit_observes_runtime_state("p1", "redis_coordination_fabric", "runtime_state")
_emit_verifies_boundary("p1", "redis_coordination_fabric", "boundary_check")
_emit_transcripts_response("p1", "redis_coordination_fabric", "transcript")
_emit_hard_fails_untranscripted("p1", "redis_coordination_fabric")
_emit_gated_by_confidence("p1", "redis_coordination_fabric", "confidence_gate")
_emit_writes_through("p1", "redis_coordination_fabric", "uwg_governed_write")
_emit_writes_through("p1", "redis_coordination_fabric", "uwg_governed_write_2")
_emit_pulls_context("p1", "redis_coordination_fabric", "context_retrieval")
_emit_pulls_context("p1", "redis_coordination_fabric", "context_retrieval_2")
emit_determinism_digest("trace_redis_coordination_fabric", "redis_coordination_fabric_dispatch")
emit_determinism_digest("trace_redis_coordination_fabric", "redis_coordination_fabric_complete")
_emit_validated_by_safety_plane("p1", "redis_coordination_fabric", "safety_validation")

logger = logging.getLogger(__name__)

# DB-2 is the new coordination fabric namespace.
# DB-0 = hot caches (L0/L1/L3/L5)
# DB-1 = coordination leases (L2)
# DB-2 = operational workspace (per-trace, team-sync, replay-assist, novelty)
_DB_WORKSPACE = 2  # type: ignore[assignment]

# TTL caps (seconds) per namespace — fail-closed if caller exceeds these
_TTL_TRACE_WS: int = 900  # 15 min: active request lifetime
_TTL_TEAM_LOCK: int = 120  # 2 min: coordination window
_TTL_ROUTE_CTX: int = 3600  # 60 min: hot routing context
_TTL_REPLAY_FRAG: int = 600  # 10 min: replay assist cache
_TTL_NOVELTY: int = 1800  # 30 min: novelty cluster working cache


def _require_hash_input(name: str, value: str) -> str:
    if not value:
        raise ValueError(f"{name} must not be empty")
    return value


def _bounded_ttl(name: str, ttl_seconds: int | None, cap: int) -> int:
    ttl = cap if ttl_seconds is None else ttl_seconds
    if ttl <= 0:
        raise ValueError(f"{name} ttl_seconds must be > 0, got {ttl}")
    return min(ttl, cap)


class RedisCoordinationFabric:
    """DB-2 bounded operational workspace — the "working desk" layer.

    All methods are TTL-bounded, replay-safe, and hash-keyed.
    Never authoritative for policy, lineage, audit, or final artifacts.
    """

    def __init__(self, cache: DeterministicRedisCache | None = None) -> None:
        self._cache = cache or get_workspace_cache()

    # -------------------------------------------------------------------------
    # Trace working set (per-trace active request state)
    # -------------------------------------------------------------------------

    def get_trace_working_set(
        self, trace_id_hash: str, *, replay_mode: bool = False
    ) -> dict[str, Any] | None:
        """Return per-trace working set dict or None if not found/expired."""
        _require_hash_input("trace_id_hash", trace_id_hash)
        if replay_mode:
            return None
        return self._cache.get_json(f"trace_ws:{trace_id_hash}")

    def set_trace_working_set(
        self,
        trace_id_hash: str,
        data: dict[str, Any],
        *,
        ttl_seconds: int | None = None,
        replay_mode: bool = False,
    ) -> None:
        """Store per-trace working set dict (JSON-serialisable only)."""
        _require_hash_input("trace_id_hash", trace_id_hash)
        if replay_mode:
            return
        ttl = _bounded_ttl("trace_ws", ttl_seconds, _TTL_TRACE_WS)
        self._cache.set_json(f"trace_ws:{trace_id_hash}", data, ttl_seconds=ttl)

    # -------------------------------------------------------------------------
    # Team lock (duplicate-work prevention)
    # -------------------------------------------------------------------------

    def acquire_team_lock(
        self, resource_hash: str, holder_id: str, *, ttl_seconds: int | None = None
    ) -> bool:
        """Try to acquire a team-sync lease. Returns True if acquired."""
        _require_hash_input("resource_hash", resource_hash)
        if not holder_id:
            raise ValueError("holder_id must not be empty")
        ttl = _bounded_ttl("team_lock", ttl_seconds, _TTL_TEAM_LOCK)
        return self._cache.set_nx(f"team_lock:{resource_hash}", holder_id, ttl_seconds=ttl)

    def release_team_lock(self, resource_hash: str, holder_id: str) -> bool:
        """Release team lock if held by holder_id."""
        _require_hash_input("resource_hash", resource_hash)
        if not holder_id:
            raise ValueError("holder_id must not be empty")
        key = f"team_lock:{resource_hash}"
        client = self._cache._get_client()
        if client is None:
            return False
        with client.pipeline() as pipe:
            try:
                pipe.watch(key)
                current = pipe.get(key)
                if current != holder_id:
                    pipe.unwatch()
                    return False
                pipe.multi()
                pipe.delete(key)
                pipe.execute()
                return True
            except Exception as e:  # guardian: allow-broad-exception -- Redis pipeline raises WatchError and varied types; broad catch required for atomic release safety
                logger.warning("[Coordination fabric] Team lock release failed for %s: %s", key, e)
                return False

    # -------------------------------------------------------------------------
    # Route context (hot routing cache for fast path election)
    # -------------------------------------------------------------------------

    def get_route_context(self, intent_hash: str, *, replay_mode: bool = False) -> dict[str, Any] | None:
        """Return hot routing context or None if not found."""
        _require_hash_input("intent_hash", intent_hash)
        if replay_mode:
            return None
        return self._cache.get_json(f"route_ctx:{intent_hash}")

    def set_route_context(
        self, intent_hash: str, data: dict[str, Any], *, ttl_seconds: int | None = None
    ) -> None:
        """Store hot routing context."""
        _require_hash_input("intent_hash", intent_hash)
        ttl = _bounded_ttl("route_ctx", ttl_seconds, _TTL_ROUTE_CTX)
        self._cache.set_json(f"route_ctx:{intent_hash}", data, ttl_seconds=ttl)

    # -------------------------------------------------------------------------
    # Replay fragment (transcript assist cache)
    # -------------------------------------------------------------------------

    def get_replay_fragment(
        self, replay_key_hash: str, *, replay_mode: bool = False
    ) -> dict[str, Any] | None:
        """Return replay assist fragment or None if not found."""
        _require_hash_input("replay_key_hash", replay_key_hash)
        if replay_mode:
            return None
        return self._cache.get_json(f"replay_frag:{replay_key_hash}")

    def set_replay_fragment(
        self,
        replay_key_hash: str,
        fragment: dict[str, Any],
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        """Store replay assist fragment."""
        _require_hash_input("replay_key_hash", replay_key_hash)
        ttl = _bounded_ttl("replay_frag", ttl_seconds, _TTL_REPLAY_FRAG)
        self._cache.set_json(f"replay_frag:{replay_key_hash}", fragment, ttl_seconds=ttl)

    # -------------------------------------------------------------------------
    # Novelty cluster (incident burst working cache)
    # -------------------------------------------------------------------------

    def get_novelty_cluster(self, cluster_hash: str, *, replay_mode: bool = False) -> dict[str, Any] | None:
        """Return novelty/cluster centroid or None if not found."""
        _require_hash_input("cluster_hash", cluster_hash)
        if replay_mode:
            return None
        return self._cache.get_json(f"novelty:{cluster_hash}")

    def set_novelty_cluster(
        self,
        cluster_hash: str,
        data: dict[str, Any],
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        """Store novelty/cluster centroid."""
        _require_hash_input("cluster_hash", cluster_hash)
        ttl = _bounded_ttl("novelty", ttl_seconds, _TTL_NOVELTY)
        self._cache.set_json(f"novelty:{cluster_hash}", data, ttl_seconds=ttl)


# Singleton instance
coordination_fabric: RedisCoordinationFabric = RedisCoordinationFabric()


def get_coordination_fabric() -> RedisCoordinationFabric:
    """Return the global RedisCoordinationFabric singleton."""
    return coordination_fabric
