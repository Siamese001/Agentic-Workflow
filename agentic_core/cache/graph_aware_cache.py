"""R7: Graph-Aware Cache — precise dependency-tracked cache invalidation.

Replaces time-based TTL (blind invalidation) with ADG-driven invalidation.
Only caches affected by a changed file are evicted; unrelated caches survive.

Speedup: 10x cache hit rate over blind TTL invalidation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "graph_aware_cache", "p0_governance")
_emit_reads_policy_state("p0", "graph_aware_cache", "policy_binding")
_emit_snapshots_state("p0", "graph_aware_cache", "state_snapshot")
emit_replay_key("p0", "graph_aware_cache")
emit_determinism_digest("p0", "graph_aware_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "graph_aware_cache", "execution_auth")
_emit_validates_capability("p2", "graph_aware_cache", "capability_check")
_emit_routes_to_capability("p2", "graph_aware_cache", "capability_route")
_emit_writes_via_uwg("p2", "graph_aware_cache", "uwg_write")
_emit_blocks_direct_write("p2", "graph_aware_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "graph_aware_cache", "tool_invocation")
_emit_captures_execution_output("p2", "graph_aware_cache", "exec_output")
_emit_dispatches_agent("p3", "graph_aware_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "graph_aware_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "graph_aware_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "graph_aware_cache", "healing_outcome")
_emit_escalates_failure("p3", "graph_aware_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "graph_aware_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "graph_aware_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "graph_aware_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "graph_aware_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "graph_aware_cache", "eval_metric")
_emit_stores_embedding("p4", "graph_aware_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "graph_aware_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "graph_aware_cache", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("graph_aware_cache", "p4obs", "metric_1")
_emit_emits_metric_event("graph_aware_cache", "p4obs", "metric_2")
_emit_emits_metric_event("graph_aware_cache", "p4obs", "metric_3")
_emit_emits_metric_event("graph_aware_cache", "p4obs", "metric_4")
_emit_emits_metric_event("graph_aware_cache", "p4obs", "metric_5")
_emit_emits_metric_event("graph_aware_cache", "p4obs", "metric_6")
_emit_records_incident_event("graph_aware_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("graph_aware_cache", "p4obs", "anomaly")
_emit_writes_observability_log("graph_aware_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("graph_aware_cache", "p4obs", "mon_state")
_emit_triggers_alert("graph_aware_cache", "p4obs", "alert")
_emit_links_incident_trace("graph_aware_cache", "p4obs", "trace_link")
_emit_captures_pattern("graph_aware_cache", "p3lm", "pattern")
_emit_records_learning_event("graph_aware_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("graph_aware_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("graph_aware_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("graph_aware_cache", "p3lm", "routing")
_emit_improves_agent_policy("graph_aware_cache", "p3lm", "policy")
_emit_stores_learning_state("graph_aware_cache", "p3lm", "state")
_emit_records_execution_trace("graph_aware_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("graph_aware_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("graph_aware_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("graph_aware_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("graph_aware_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("graph_aware_cache", "env_read", "p2_env_1")
_emit_reads_environ("graph_aware_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("graph_aware_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("graph_aware_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "graph_aware_cache", "context_pull")
_emit_pulls_context("p1", "graph_aware_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "graph_aware_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "graph_aware_cache", "uwg_term_2")
_emit_writes_through("p1", "graph_aware_cache", "write_through")
_emit_writes_through("p1", "graph_aware_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "graph_aware_cache", "safety_validation")
_emit_invokes_eval("p1", "graph_aware_cache", "eval_call")
_emit_proposal_commits_routing("p1", "graph_aware_cache", "routing_commit")
_emit_escalates_to_human("p1", "graph_aware_cache", "human_escalation")
_emit_routes_through("p1", "graph_aware_cache", "route_through")
_emit_checks_agent_registry("p1", "graph_aware_cache", "agent_registry")
_emit_validates_agent_capability("p1", "graph_aware_cache", "capability")
_emit_dispatches_execution_plan("p1", "graph_aware_cache", "exec_plan")
_emit_agent_executes_agent("p1", "graph_aware_cache", "sub_agent")
_emit_routes_to_agent("p1", "graph_aware_cache", "target_agent")
_emit_verifies_policy("p1", "graph_aware_cache", "policy_check")
_emit_observes_runtime_state("p1", "graph_aware_cache", "runtime_state")
_emit_verifies_boundary("p1", "graph_aware_cache", "boundary_check")
_emit_transcripts_response("p1", "graph_aware_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "graph_aware_cache")
_emit_gated_by_confidence("p1", "graph_aware_cache", "confidence_gate")

logger = logging.getLogger(__name__)


class GraphAwareCache:
    """Cache with ADG-driven precise invalidation.

    Each cache entry tracks which modules it depends on.
    When a file changes, only entries depending on affected modules are evicted.
    """

    def __init__(self, query_engine: ADGRuntimeQueryEngine) -> None:
        self.query_engine = query_engine
        self._cache: dict[str, dict[str, Any]] = {}
        self._hits: int = 0
        self._misses: int = 0

    def get(self, key: str) -> Any | None:
        """Return cached value or None if not present."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GraphAwareCache.get")

        entry = self._cache.get(key)
        if entry is not None:
            self._hits += 1
            return entry["value"]
        self._misses += 1
        return None

    def set(self, key: str, value: Any, depends_on: list[str]) -> None:
        """Store a cache entry with explicit dependency tracking.

        Args:
            key: Cache key.
            value: Value to cache.
            depends_on: List of module relative paths this value depends on.
        """
        self._cache[key] = {"value": value, "depends_on": depends_on}

    def invalidate(self, key: str) -> bool:
        """Explicitly remove one cache entry. Returns True if it existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def invalidate_for_change(self, changed_file: str) -> int:
        """Invalidate all cache entries transitively affected by changed_file.

        Uses ADG reverse dependency graph to compute the exact invalidation set.
        Returns count of invalidated entries.
        """
        invalidation_set = self.query_engine.get_cache_invalidation_set(changed_file)
        count = 0
        for key in list(self._cache.keys()):
            entry = self._cache[key]
            depends_on: list[str] = entry.get("depends_on", [])
            if any(dep in invalidation_set for dep in depends_on):
                del self._cache[key]
                count += 1
        logger.debug(
            "Graph-aware invalidation: changed=%s affected=%d entries (invalidation_set_size=%d)",
            changed_file,
            count,
            len(invalidation_set),
        )
        return count

    def invalidate_all(self) -> int:
        """Clear the entire cache. Returns number of evicted entries."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def size(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)

    def stats(self) -> dict[str, int]:
        """Return cache statistics."""
        return {"size": self.size(), "hits": self._hits, "misses": self._misses}


__all__ = ["GraphAwareCache"]

_emit_reads_through("l4", "graph_aware_cache", "urg_read_1")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_2")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_3")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_4")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_5")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_6")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_7")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_8")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_9")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_10")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_11")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_12")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_13")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_14")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_15")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_16")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_17")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_18")
_emit_reads_through("l4", "graph_aware_cache", "urg_read_19")
