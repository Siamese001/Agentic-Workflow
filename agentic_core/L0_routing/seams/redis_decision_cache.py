"""L0 Routing — Redis decision-acceleration cache seam.

Provides three non-authoritative, hash-keyed read-through helpers:

  RouteDecisionCache
      Memoises ``RouteDecisionArtifact`` outputs keyed by
      ``(intent_hash, policy_hash, routing_state_hash)``.

  RoutingRuleSurfaceCache
      Mirrors the active routing-ruleset snapshot from L4 keyed by
      ``routing_state_hash``.  Read-only — never written to by L0.

  CapabilityRegistryCache
      Mirrors tool-inventory / allowlist envelopes from L4 keyed by
      ``cap_registry_hash``.

Determinism contract
--------------------
* All keys are composed from hashes already present in existing L0
  contracts (``policy_config_hash``, ``routing_state_hash``, etc.).
* No wall-clock timestamps.  No random nonces.
* ``replay_mode=True`` causes every ``get`` to return ``None`` so the
  caller re-derives the value from L4 and records it in the transcript.
* Writing to this cache does NOT modify any L4 state.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import (
    build_cap_registry_key,
    build_route_decision_key,
    build_routing_rule_surface_key,
)
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_hot_cache,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "redis_decision_cache", "L0")
_emit_routes_through("p1", "redis_decision_cache", "L0")
_emit_checks_agent_registry("p1", "redis_decision_cache", "agent_registry")
_emit_validates_agent_capability("p1", "redis_decision_cache", "capability")
_emit_dispatches_execution_plan("p1", "redis_decision_cache", "exec_plan")
_emit_agent_executes_agent("p1", "redis_decision_cache", "sub_agent")
_emit_routes_to_agent("p1", "redis_decision_cache", "target_agent")
_emit_verifies_policy("p1", "redis_decision_cache", "policy_check")
_emit_observes_runtime_state("p1", "redis_decision_cache", "runtime_state")
_emit_verifies_boundary("p1", "redis_decision_cache", "boundary_check")
_emit_transcripts_response("p1", "redis_decision_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "redis_decision_cache")
_emit_gated_by_confidence("p1", "redis_decision_cache", "confidence_gate")
_emit_escalates_to_human("p1", "redis_decision_cache", "L0")
_emit_reads_policy_state("p1", "redis_decision_cache", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "redis_decision_cache", "p0_governance")
_emit_snapshots_state("p0", "redis_decision_cache", "state_snapshot")
_emit_authorize_and_execute("p2", "redis_decision_cache", "execution_auth")
_emit_validates_capability("p2", "redis_decision_cache", "capability_check")
_emit_routes_to_capability("p2", "redis_decision_cache", "capability_route")
_emit_writes_via_uwg("p2", "redis_decision_cache", "uwg_write")
_emit_blocks_direct_write("p2", "redis_decision_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "redis_decision_cache", "tool_invocation")
_emit_captures_execution_output("p2", "redis_decision_cache", "exec_output")
_emit_dispatches_agent("p3", "redis_decision_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "redis_decision_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "redis_decision_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "redis_decision_cache", "healing_outcome")
_emit_escalates_failure("p3", "redis_decision_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "redis_decision_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "redis_decision_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "redis_decision_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "redis_decision_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "redis_decision_cache", "eval_metric")
_emit_stores_embedding("p4", "redis_decision_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "redis_decision_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "redis_decision_cache", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("redis_decision_cache", "p4obs", "metric_1")
_emit_emits_metric_event("redis_decision_cache", "p4obs", "metric_2")
_emit_emits_metric_event("redis_decision_cache", "p4obs", "metric_3")
_emit_emits_metric_event("redis_decision_cache", "p4obs", "metric_4")
_emit_emits_metric_event("redis_decision_cache", "p4obs", "metric_5")
_emit_emits_metric_event("redis_decision_cache", "p4obs", "metric_6")
_emit_records_incident_event("redis_decision_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("redis_decision_cache", "p4obs", "anomaly")
_emit_writes_observability_log("redis_decision_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("redis_decision_cache", "p4obs", "mon_state")
_emit_triggers_alert("redis_decision_cache", "p4obs", "alert")
_emit_links_incident_trace("redis_decision_cache", "p4obs", "trace_link")
_emit_captures_pattern("redis_decision_cache", "p3lm", "pattern")
_emit_records_learning_event("redis_decision_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("redis_decision_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("redis_decision_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("redis_decision_cache", "p3lm", "routing")
_emit_improves_agent_policy("redis_decision_cache", "p3lm", "policy")
_emit_stores_learning_state("redis_decision_cache", "p3lm", "state")
_emit_records_execution_trace("redis_decision_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("redis_decision_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("redis_decision_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("redis_decision_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("redis_decision_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("redis_decision_cache", "env_read", "p2_env_1")
_emit_reads_environ("redis_decision_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("redis_decision_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("redis_decision_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "redis_decision_cache", "context_pull")
_emit_pulls_context("p1", "redis_decision_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "redis_decision_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "redis_decision_cache", "uwg_term_2")
_emit_writes_through("p1", "redis_decision_cache", "write_through")
_emit_writes_through("p1", "redis_decision_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "redis_decision_cache", "safety_validation")
_emit_invokes_eval("p1", "redis_decision_cache", "eval_call")
_emit_proposal_commits_routing("p1", "redis_decision_cache", "routing_commit")

logger = logging.getLogger(__name__)

_DEFAULT_RULE_SURFACE_TTL: int = 3600  # 1 hour
_DEFAULT_ROUTE_DECISION_TTL: int = 1800  # 30 minutes
_DEFAULT_CAP_REGISTRY_TTL: int = 3600  # 1 hour


class RouteDecisionCache:
    """Memoises ``RouteDecisionArtifact`` JSON for identical L0 inputs.

    The value stored is the canonical JSON representation of the artifact's
    serialisable fields.  Callers are responsible for deserialising back to
    the typed artifact.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_ROUTE_DECISION_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached route-decision dict or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RouteDecisionCache.get")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        key = build_route_decision_key(intent_hash, policy_hash, routing_state_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
        artifact_dict: dict[str, Any],
    ) -> None:
        """Cache *artifact_dict* under the deterministic key.

        ``artifact_dict`` must be the canonical JSON-serialisable
        representation of a ``RouteDecisionArtifact`` — callers must
        produce it from the typed artifact before calling this method.
        """
        key = build_route_decision_key(intent_hash, policy_hash, routing_state_hash)
        self._cache.set_json(key, artifact_dict, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached result or call *fetch_from_l4*.

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
        """
        if not replay_mode:
            cached = self.get(intent_hash, policy_hash, routing_state_hash)
            if cached is not None:
                logger.debug("[L0 cache] route_decision HIT")
                return cached
        logger.debug("[L0 cache] route_decision MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(intent_hash, policy_hash, routing_state_hash, result)
        return result

    def invalidate(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
    ) -> None:
        """Explicitly evict a cached decision."""
        key = build_route_decision_key(intent_hash, policy_hash, routing_state_hash)
        self._cache.delete(key)


class RoutingRuleSurfaceCache:
    """Read-only mirror of the active routing-ruleset snapshot from L4.

    This cache is NEVER a source of truth.  The ruleset is fetched from L4
    on every miss; on a hit the cached bytes are returned as a convenience.

    Parameters
    ----------
    ttl_seconds:
        TTL applied when the L4 snapshot is written into Redis.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_RULE_SURFACE_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        routing_state_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached ruleset dict or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RoutingRuleSurfaceCache.get")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        key = build_routing_rule_surface_key(routing_state_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        routing_state_hash: str,
        ruleset: dict[str, Any],
    ) -> None:
        """Write *ruleset* (a canonical JSON dict from L4) into the mirror."""
        key = build_routing_rule_surface_key(routing_state_hash)
        self._cache.set_json(key, ruleset, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        routing_state_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached ruleset or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        ruleset dict from L4.  Called only on a cache miss; result is stored.
        """
        if not replay_mode:
            cached = self.get(routing_state_hash)
            if cached is not None:
                logger.debug("[L0 cache] rule_surface HIT")
                return cached
        logger.debug("[L0 cache] rule_surface MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(routing_state_hash, result)
        return result

    def invalidate(self, routing_state_hash: str) -> None:
        """Evict the cached ruleset."""
        key = build_routing_rule_surface_key(routing_state_hash)
        self._cache.delete(key)


class CapabilityRegistryCache:
    """Mirrors the tool-inventory / capability-registry snapshot from L4.

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
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_CAP_REGISTRY_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        cap_registry_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached capability registry or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "CapabilityRegistryCache.get")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        key = build_cap_registry_key(cap_registry_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        cap_registry_hash: str,
        registry: dict[str, Any],
    ) -> None:
        """Store *registry* (canonical JSON dict from L4) in the mirror."""
        key = build_cap_registry_key(cap_registry_hash)
        self._cache.set_json(key, registry, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        cap_registry_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached registry or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        capability registry dict from L4.  Called only on a cache miss.
        """
        if not replay_mode:
            cached = self.get(cap_registry_hash)
            if cached is not None:
                logger.debug("[L0 cache] cap_registry HIT")
                return cached
        logger.debug("[L0 cache] cap_registry MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(cap_registry_hash, result)
        return result

    def invalidate(self, cap_registry_hash: str) -> None:
        """Evict the cached registry snapshot."""
        key = build_cap_registry_key(cap_registry_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singletons
# ---------------------------------------------------------------------------

_route_decision_cache: RouteDecisionCache | None = None
_rule_surface_cache: RoutingRuleSurfaceCache | None = None
_cap_registry_cache: CapabilityRegistryCache | None = None


def get_route_decision_cache() -> RouteDecisionCache:
    global _route_decision_cache
    if _route_decision_cache is None:
        _route_decision_cache = RouteDecisionCache()
    return _route_decision_cache


def get_routing_rule_surface_cache() -> RoutingRuleSurfaceCache:
    global _rule_surface_cache
    if _rule_surface_cache is None:
        _rule_surface_cache = RoutingRuleSurfaceCache()
    return _rule_surface_cache


def get_cap_registry_cache() -> CapabilityRegistryCache:
    global _cap_registry_cache
    if _cap_registry_cache is None:
        _cap_registry_cache = CapabilityRegistryCache()
    return _cap_registry_cache
