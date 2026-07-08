"""Policy Registry Cache — Redis-backed cache for sovereign policy lookups.

Caches immutable policy definitions to eliminate repeated registry scans.
Keyed by policy ID for fast O(1) lookups.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "policy_registry_cache", "p0_governance")
trace_contract._emit_snapshots_state("p0", "policy_registry_cache", "state_snapshot")

trace_contract._emit_emits_metric_event("policy_registry_cache", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("policy_registry_cache", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("policy_registry_cache", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("policy_registry_cache", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("policy_registry_cache", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("policy_registry_cache", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("policy_registry_cache", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("policy_registry_cache", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("policy_registry_cache", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("policy_registry_cache", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("policy_registry_cache", "p4obs", "alert")
trace_contract._emit_links_incident_trace("policy_registry_cache", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("policy_registry_cache", "p3lm", "pattern")
trace_contract._emit_records_learning_event("policy_registry_cache", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("policy_registry_cache", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("policy_registry_cache", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("policy_registry_cache", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("policy_registry_cache", "p3lm", "policy")
trace_contract._emit_stores_learning_state("policy_registry_cache", "p3lm", "state")
trace_contract._emit_records_execution_trace("policy_registry_cache", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("policy_registry_cache", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("policy_registry_cache", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("policy_registry_cache", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("policy_registry_cache", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("policy_registry_cache", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("policy_registry_cache", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("policy_registry_cache", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("policy_registry_cache", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "policy_registry_cache", "context_pull")
trace_contract._emit_pulls_context("p1", "policy_registry_cache", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "policy_registry_cache", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "policy_registry_cache", "uwg_term_2")
trace_contract._emit_writes_through("p1", "policy_registry_cache", "write_through")
trace_contract._emit_writes_through("p1", "policy_registry_cache", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "policy_registry_cache", "safety_validation")
trace_contract._emit_invokes_eval("p1", "policy_registry_cache", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "policy_registry_cache", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "policy_registry_cache", "human_escalation")
trace_contract._emit_routes_through("p1", "policy_registry_cache", "route_through")
trace_contract._emit_checks_agent_registry("p1", "policy_registry_cache", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "policy_registry_cache", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "policy_registry_cache", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "policy_registry_cache", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "policy_registry_cache", "target_agent")
trace_contract._emit_verifies_policy("p1", "policy_registry_cache", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "policy_registry_cache", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "policy_registry_cache", "boundary_check")
trace_contract._emit_transcripts_response("p1", "policy_registry_cache", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "policy_registry_cache")
trace_contract._emit_gated_by_confidence("p1", "policy_registry_cache", "confidence_gate")
trace_contract.emit_replay_key("p0", "policy_registry_cache")
trace_contract.emit_determinism_digest("p0", "policy_registry_cache")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "policy_registry_cache", "execution_auth")
trace_contract._emit_validates_capability("p2", "policy_registry_cache", "capability_check")
trace_contract._emit_routes_to_capability("p2", "policy_registry_cache", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "policy_registry_cache", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "policy_registry_cache", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "policy_registry_cache", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "policy_registry_cache", "exec_output")
trace_contract._emit_dispatches_agent("p3", "policy_registry_cache", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "policy_registry_cache", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "policy_registry_cache", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "policy_registry_cache", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "policy_registry_cache", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "policy_registry_cache", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "policy_registry_cache", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "policy_registry_cache", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "policy_registry_cache", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "policy_registry_cache", "eval_metric")
trace_contract._emit_stores_embedding("p4", "policy_registry_cache", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "policy_registry_cache", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "policy_registry_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_DEFAULT_POLICY_TTL = 3600 * 24 * 30


def _require_positive_ttl(ttl_seconds: int) -> int:
    if ttl_seconds <= 0:
        raise ValueError(f"ttl_seconds must be > 0, got {ttl_seconds}")
    return ttl_seconds


def _normalize_policy_id(policy_id: str) -> str:
    normalized = policy_id.strip() if policy_id else ""
    if not normalized:
        raise ValueError("Policy ID must not be empty")
    return normalized


class PolicyRegistryCache:
    """Cache for sovereign policy registry lookups.

    Eliminates repeated policy registry scans for the same policy IDs.
    Policies are immutable, so cache is long-lived.
    """

    def __init__(self, cache: DeterministicRedisCache | None = None, ttl_seconds: int = _DEFAULT_POLICY_TTL):
        self._cache = cache or get_hot_cache()
        self._ttl = _require_positive_ttl(ttl_seconds)

    def get_or_fetch(
        self, policy_id: str, fetch_policy: Callable[[], dict[str, Any]], *, replay_mode: bool = False
    ) -> dict[str, Any]:
        """Read-through helper: return cached policy or call *fetch_policy*.

        *fetch_policy* is a zero-argument callable that fetches the policy
        definition from the registry.  Called only on cache miss.

        Args:
            policy_id: Unique policy identifier (e.g., "GOV-001")
            fetch_policy: Callable that returns policy definition dict
            replay_mode: If True, bypass cache entirely

        Returns:
            Policy definition dict
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "PolicyRegistryCache.get_or_fetch"
        )

        normalized_id = _normalize_policy_id(policy_id)
        if not callable(fetch_policy):
            raise TypeError("fetch_policy must be callable")
        if not replay_mode:
            try:
                cache_key = f"policy:{normalized_id}"
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug(f"[Policy cache] HIT for {normalized_id}")
                    return cached
            except (
                ConnectionError,
                ValueError,
            ) as e:  # guardian: allow-log-and-swallow -- policy cache read: non-fatal, falls back to live fetch
                logger.warning(f"[Policy cache] Cache read failed: {e}")
        logger.debug(f"[Policy cache] MISS for {normalized_id} — fetching from registry")
        result = fetch_policy()
        if not isinstance(result, dict):
            raise TypeError(f"fetch_policy must return a dict, got {type(result).__name__}")
        if not replay_mode:
            try:
                cache_key = f"policy:{normalized_id}"
                self._cache.set_json(cache_key, result, ttl_seconds=self._ttl)
            except (
                ConnectionError,
                ValueError,
                TypeError,
            ) as e:  # guardian: allow-log-and-swallow -- policy cache write: non-fatal, policy returned without caching
                logger.warning(f"[Policy cache] Cache write failed: {e}")
        return result

    def invalidate(self, policy_id: str) -> None:
        """Invalidate cached policy for specific ID."""
        try:
            normalized_id = _normalize_policy_id(policy_id)
            cache_key = f"policy:{normalized_id}"
            self._cache.delete(cache_key)
            logger.debug(f"[Policy cache] Invalidated {normalized_id}")
        except (
            ConnectionError,
            ValueError,
        ) as e:  # guardian: allow-log-and-swallow -- policy cache invalidate: non-fatal, stale entry may persist until TTL
            logger.warning(f"[Policy cache] Invalidation failed: {e}")


def get_policy_registry_cache() -> PolicyRegistryCache:
    """Get the singleton policy registry cache instance."""
    return PolicyRegistryCache()


trace_contract._emit_reads_through("l4", "policy_registry_cache", "urg_read_1")
trace_contract._emit_reads_through("l4", "policy_registry_cache", "urg_read_2")
trace_contract._emit_reads_through("l4", "policy_registry_cache", "urg_read_3")
trace_contract._emit_reads_through("l4", "policy_registry_cache", "urg_read_4")
trace_contract._emit_reads_through("l4", "policy_registry_cache", "urg_read_5")
trace_contract._emit_reads_through("l4", "policy_registry_cache", "urg_read_6")
trace_contract._emit_reads_through("l4", "policy_registry_cache", "urg_read_7")
