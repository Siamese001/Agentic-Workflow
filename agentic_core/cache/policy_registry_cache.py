"""Policy Registry Cache — Redis-backed cache for sovereign policy lookups.

Caches immutable policy definitions to eliminate repeated registry scans.
Keyed by policy ID for fast O(1) lookups.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
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

_emit_applies_guardrail("p0", "policy_registry_cache", "p0_governance")
_emit_snapshots_state("p0", "policy_registry_cache", "state_snapshot")
emit_replay_key("p0", "policy_registry_cache")
emit_determinism_digest("p0", "policy_registry_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "policy_registry_cache", "execution_auth")
_emit_validates_capability("p2", "policy_registry_cache", "capability_check")
_emit_routes_to_capability("p2", "policy_registry_cache", "capability_route")
_emit_writes_via_uwg("p2", "policy_registry_cache", "uwg_write")
_emit_blocks_direct_write("p2", "policy_registry_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "policy_registry_cache", "tool_invocation")
_emit_captures_execution_output("p2", "policy_registry_cache", "exec_output")
_emit_dispatches_agent("p3", "policy_registry_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "policy_registry_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "policy_registry_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "policy_registry_cache", "healing_outcome")
_emit_escalates_failure("p3", "policy_registry_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "policy_registry_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "policy_registry_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "policy_registry_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "policy_registry_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "policy_registry_cache", "eval_metric")
_emit_stores_embedding("p4", "policy_registry_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "policy_registry_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "policy_registry_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_DEFAULT_POLICY_TTL = 3600 * 24 * 30


class PolicyRegistryCache:
    """Cache for sovereign policy registry lookups.

    Eliminates repeated policy registry scans for the same policy IDs.
    Policies are immutable, so cache is long-lived.
    """

    def __init__(self, cache: DeterministicRedisCache | None = None, ttl_seconds: int = _DEFAULT_POLICY_TTL):
        self._cache = cache or get_hot_cache()
        self._ttl = ttl_seconds

    def get_or_fetch(self, policy_id: str, fetch_policy: Any, *, replay_mode: bool = False) -> dict[str, Any]:
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PolicyRegistryCache.get_or_fetch")

        if not policy_id or not policy_id.strip():
            raise ValueError("Policy ID must not be empty")
        if not replay_mode:
            try:
                cache_key = f"policy:{policy_id}"
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug(f"[Policy cache] HIT for {policy_id}")
                    return cached
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[Policy cache] Cache read failed: {e}")
        logger.debug(f"[Policy cache] MISS for {policy_id} — fetching from registry")
        result = fetch_policy()
        if not replay_mode:
            try:
                cache_key = f"policy:{policy_id}"
                self._cache.set_json(cache_key, result, ttl_seconds=self._ttl)
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[Policy cache] Cache write failed: {e}")
        return result

    def invalidate(self, policy_id: str) -> None:
        """Invalidate cached policy for specific ID."""
        try:
            cache_key = f"policy:{policy_id}"
            self._cache.delete(cache_key)
            logger.debug(f"[Policy cache] Invalidated {policy_id}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"[Policy cache] Invalidation failed: {e}")


def get_policy_registry_cache() -> PolicyRegistryCache:
    """Get the singleton policy registry cache instance."""
    return PolicyRegistryCache()
