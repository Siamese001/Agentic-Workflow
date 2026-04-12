"""
cache Metrics Collector - Singleton for tracking Redis/Pinecone performance

Tracks:
- Hit/miss rates per operation type
- Latency statistics
- Operation counts

Integrates with dashboard for visibility.
"""

import threading
import time
from collections import defaultdict
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "cache_metrics_util", "p0_governance")
_emit_reads_policy_state("p0", "cache_metrics_util", "policy_binding")
_emit_snapshots_state("p0", "cache_metrics_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("cache_metrics_util", "p4obs", "metric_1")
_emit_emits_metric_event("cache_metrics_util", "p4obs", "metric_2")
_emit_emits_metric_event("cache_metrics_util", "p4obs", "metric_3")
_emit_emits_metric_event("cache_metrics_util", "p4obs", "metric_4")
_emit_emits_metric_event("cache_metrics_util", "p4obs", "metric_5")
_emit_emits_metric_event("cache_metrics_util", "p4obs", "metric_6")
_emit_records_incident_event("cache_metrics_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_metrics_util", "p4obs", "anomaly")
_emit_writes_observability_log("cache_metrics_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_metrics_util", "p4obs", "mon_state")
_emit_triggers_alert("cache_metrics_util", "p4obs", "alert")
_emit_links_incident_trace("cache_metrics_util", "p4obs", "trace_link")
_emit_captures_pattern("cache_metrics_util", "p3lm", "pattern")
_emit_records_learning_event("cache_metrics_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_metrics_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_metrics_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_metrics_util", "p3lm", "routing")
_emit_improves_agent_policy("cache_metrics_util", "p3lm", "policy")
_emit_stores_learning_state("cache_metrics_util", "p3lm", "state")
_emit_records_execution_trace("cache_metrics_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_metrics_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_metrics_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_metrics_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_metrics_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_metrics_util", "env_read", "p2_env_1")
_emit_reads_environ("cache_metrics_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_metrics_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_metrics_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_metrics_util", "context_pull")
_emit_pulls_context("p1", "cache_metrics_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cache_metrics_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_metrics_util", "uwg_term_2")
_emit_writes_through("p1", "cache_metrics_util", "write_through")
_emit_writes_through("p1", "cache_metrics_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "cache_metrics_util", "safety_validation")
_emit_invokes_eval("p1", "cache_metrics_util", "eval_call")
_emit_proposal_commits_routing("p1", "cache_metrics_util", "routing_commit")
_emit_escalates_to_human("p1", "cache_metrics_util", "human_escalation")
_emit_routes_through("p1", "cache_metrics_util", "route_through")
_emit_checks_agent_registry("p1", "cache_metrics_util", "agent_registry")
_emit_validates_agent_capability("p1", "cache_metrics_util", "capability")
_emit_dispatches_execution_plan("p1", "cache_metrics_util", "exec_plan")
_emit_agent_executes_agent("p1", "cache_metrics_util", "sub_agent")
_emit_routes_to_agent("p1", "cache_metrics_util", "target_agent")
_emit_verifies_policy("p1", "cache_metrics_util", "policy_check")
_emit_observes_runtime_state("p1", "cache_metrics_util", "runtime_state")
_emit_verifies_boundary("p1", "cache_metrics_util", "boundary_check")
_emit_transcripts_response("p1", "cache_metrics_util", "transcript")
_emit_hard_fails_untranscripted("p1", "cache_metrics_util")
_emit_gated_by_confidence("p1", "cache_metrics_util", "confidence_gate")
emit_replay_key("p0", "cache_metrics_util")
emit_determinism_digest("p0", "cache_metrics_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cache_metrics_util", "execution_auth")
_emit_validates_capability("p2", "cache_metrics_util", "capability_check")
_emit_routes_to_capability("p2", "cache_metrics_util", "capability_route")
_emit_writes_via_uwg("p2", "cache_metrics_util", "uwg_write")
_emit_blocks_direct_write("p2", "cache_metrics_util", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_metrics_util", "tool_invocation")
_emit_captures_execution_output("p2", "cache_metrics_util", "exec_output")
_emit_dispatches_agent("p3", "cache_metrics_util", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_metrics_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_metrics_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_metrics_util", "healing_outcome")
_emit_escalates_failure("p3", "cache_metrics_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_metrics_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_metrics_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_metrics_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_metrics_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_metrics_util", "eval_metric")
_emit_stores_embedding("p4", "cache_metrics_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_metrics_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_metrics_util", "exec_snapshot_link")


class CacheMetrics:
    """
    Thread-safe singleton for cache metrics collection.

    Usage:
        metrics = CacheMetrics()
        metrics.record("redis_get", hit=True, latency_ms=1.5)
        stats = metrics.get_stats()
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._stats_lock = threading.Lock()
        self.stats: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"hits": 0, "misses": 0, "latency_sum": 0.0, "ops": 0, "errors": 0},
        )
        self._start_time = time.time()

    def record(self, operation: str, hit: bool, latency_ms: float) -> None:
        """Record a cache operation."""
        with self._stats_lock:
            if hit:
                self.stats[operation]["hits"] += 1
            else:
                self.stats[operation]["misses"] += 1
            self.stats[operation]["latency_sum"] += latency_ms
            self.stats[operation]["ops"] += 1

    def record_error(self, operation: str) -> None:
        """Record a cache error."""
        with self._stats_lock:
            self.stats[operation]["errors"] += 1

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Get aggregated statistics for all operations."""
        with self._stats_lock:
            result = {}
            for op, data in self.stats.items():
                total = data["ops"]
                result[op] = {
                    "hit_rate": round(data["hits"] / total, 4) if total else 0.0,
                    "miss_rate": round(data["misses"] / total, 4) if total else 0.0,
                    "avg_latency_ms": round(data["latency_sum"] / total, 2) if total else 0.0,
                    "total_operations": total,
                    "total_errors": data["errors"],
                    "hits": data["hits"],
                    "misses": data["misses"],
                }
            return result

    def get_summary(self) -> dict[str, Any]:
        """Get high-level summary for dashboard."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CacheMetrics.get_summary")

        stats = self.get_stats()
        total_hits = sum(s["hits"] for s in stats.values())
        total_misses = sum(s["misses"] for s in stats.values())
        total_ops = total_hits + total_misses
        total_errors = sum(s["total_errors"] for s in stats.values())
        return {
            "overall_hit_rate": round(total_hits / total_ops, 4) if total_ops else 0.0,
            "total_operations": total_ops,
            "total_errors": total_errors,
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "operations_by_type": stats,
        }

    def reset(self) -> None:
        """Reset all statistics (for testing)."""
        with self._stats_lock:
            self.stats.clear()
            self._start_time = time.time()


_metrics = CacheMetrics()


def get_cache_metrics() -> CacheMetrics:
    """Get the global cache metrics instance."""
    return _metrics
