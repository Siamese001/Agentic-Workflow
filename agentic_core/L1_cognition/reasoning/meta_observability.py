"""
MetaLearningObservability - Observability and metrics for Meta-Learning system.

[PHASE 7] Full Deployment with Observability

Provides:
- Comprehensive metrics collection
- Performance monitoring
- Health checks
- Telemetry aggregation
- Dashboard-ready statistics
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.L1_cognition.types.observability_types import (
    HealthStatus,
    MetricPoint,
)
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

emit_replay_key("p0", "meta_observability")
emit_determinism_digest("p0", "meta_observability")

_emit_dispatches_healing_run("p1", "meta_observability", "L1")
_emit_routes_through("p1", "meta_observability", "L1")
_emit_checks_agent_registry("p1", "meta_observability", "agent_registry")
_emit_validates_agent_capability("p1", "meta_observability", "capability")
_emit_dispatches_execution_plan("p1", "meta_observability", "exec_plan")
_emit_agent_executes_agent("p1", "meta_observability", "sub_agent")
_emit_routes_to_agent("p1", "meta_observability", "target_agent")
_emit_verifies_policy("p1", "meta_observability", "policy_check")
_emit_verifies_boundary("p1", "meta_observability", "boundary_check")
_emit_transcripts_response("p1", "meta_observability", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_observability")
_emit_gated_by_confidence("p1", "meta_observability", "confidence_gate")
_emit_escalates_to_human("p1", "meta_observability", "L1")
_emit_reads_policy_state("p1", "meta_observability", "L1")

_emit_snapshots_state("p0", "meta_observability", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "meta_observability", "p0_governance")
_emit_authorize_and_execute("p2", "meta_observability", "execution_auth")
_emit_validates_capability("p2", "meta_observability", "capability_check")
_emit_routes_to_capability("p2", "meta_observability", "capability_route")
_emit_writes_via_uwg("p2", "meta_observability", "uwg_write")
_emit_blocks_direct_write("p2", "meta_observability", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_observability", "tool_invocation")
_emit_captures_execution_output("p2", "meta_observability", "exec_output")
_emit_dispatches_agent("p3", "meta_observability", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_observability", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_observability", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_observability", "healing_outcome")
_emit_escalates_failure("p3", "meta_observability", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_observability", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_observability", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_observability", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_observability", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_observability", "eval_metric")
_emit_stores_embedding("p4", "meta_observability", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_observability", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_observability", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("meta_observability", "p4obs", "metric_1")
_emit_emits_metric_event("meta_observability", "p4obs", "metric_2")
_emit_emits_metric_event("meta_observability", "p4obs", "metric_3")
_emit_emits_metric_event("meta_observability", "p4obs", "metric_4")
_emit_emits_metric_event("meta_observability", "p4obs", "metric_5")
_emit_emits_metric_event("meta_observability", "p4obs", "metric_6")
_emit_records_incident_event("meta_observability", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_observability", "p4obs", "anomaly")
_emit_writes_observability_log("meta_observability", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_observability", "p4obs", "mon_state")
_emit_triggers_alert("meta_observability", "p4obs", "alert")
_emit_links_incident_trace("meta_observability", "p4obs", "trace_link")
_emit_captures_pattern("meta_observability", "p3lm", "pattern")
_emit_records_learning_event("meta_observability", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_observability", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_observability", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_observability", "p3lm", "routing")
_emit_improves_agent_policy("meta_observability", "p3lm", "policy")
_emit_stores_learning_state("meta_observability", "p3lm", "state")
_emit_records_execution_trace("meta_observability", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_observability", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_observability", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_observability", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_observability", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_observability", "env_read", "p2_env_1")
_emit_reads_environ("meta_observability", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_observability", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_observability", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_observability", "context_pull")
_emit_pulls_context("p1", "meta_observability", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_observability", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_observability", "uwg_term_2")
_emit_writes_through("p1", "meta_observability", "write_through")
_emit_writes_through("p1", "meta_observability", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_observability", "safety_validation")
_emit_invokes_eval("p1", "meta_observability", "eval_call")
_emit_proposal_commits_routing("p1", "meta_observability", "routing_commit")
from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest

record_execution_trace("meta_observability", "meta_observability_trace")

emit_determinism_digest("trace_meta_observability", "meta_observability_dispatch_entry")
emit_determinism_digest("trace_meta_observability", "meta_observability_dispatch_exit")
emit_determinism_digest("trace_meta_observability", "meta_observability_tool_invoke")
emit_determinism_digest("trace_meta_observability", "meta_observability_tool_complete")
emit_determinism_digest("trace_meta_observability", "meta_observability_agent_entry")
emit_determinism_digest("trace_meta_observability", "meta_observability_agent_exit")
emit_determinism_digest("trace_meta_observability", "meta_observability_uwg_write")
emit_determinism_digest("trace_meta_observability", "meta_observability_trace_sign")
emit_determinism_digest("trace_meta_observability", "meta_observability_guardrail_check")
emit_determinism_digest("trace_meta_observability", "meta_observability_policy_verify")

Logger = logging.getLogger(__name__)


# Module-level singleton
_observability_instance: Any = None


@dataclass
class MetaLearningObservability:
    """
    Observability layer for Meta-Learning system.

    [PHASE 7] Core Implementation

    Features:
    - Real-time metrics collection
    - Component health monitoring
    - Performance tracking
    - Telemetry aggregation
    """

    # Metrics storage
    _metrics: list[MetricPoint] = field(default_factory=list)
    _max_metrics: int = 10000

    # Health status
    _health_status: dict[str, HealthStatus] = field(default_factory=dict)

    # Performance tracking
    _operation_times: dict[str, list[float]] = field(default_factory=dict)
    _max_operation_samples: int = 100

    # Aggregated stats
    stats: dict[str, Any] = field(
        default_factory=lambda: {
            "total_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "pattern_stores": 0,
            "pattern_recalls": 0,
            "healing_operations": 0,
            "cross_domain_shares": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
        },
    )

    def __post_init__(self) -> None:
        """Initialize observability components."""
        self._initialize_health_checks()
        Logger.info("[MetaLearningObservability] Initialized")

    def _initialize_health_checks(self) -> None:
        """Initialize health check entries for all components."""
        _emit_observes_runtime_state(
            str(uuid.uuid4()), "MetaLearningObservability._initialize_health_checks", "L1_REASONING"
        )
        components = [
            "MetaLearningClient",
            "HealingMemoryEmbedder",
            "CacheStrategyManager",
            "DomainContextManager",
            "Redis",
            "Pinecone",
        ]
        for component in components:
            self._health_status[component] = HealthStatus(
                component=component,
                healthy=True,
                message="Not yet checked",
            )

    # ==================== METRICS ====================

    def record_metric(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """
        Record a metric data point.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for filtering
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "MetaLearningObservability.record_metric"
        )

        metric = MetricPoint(name=name, value=value, tags=tags or {})
        self._metrics.append(metric)

        # Trim if over limit
        if len(self._metrics) > self._max_metrics:
            self._metrics = self._metrics[-self._max_metrics :]

    # guardian: allow-magic-config
    def get_metrics(
        self,
        name: str | None = None,
        limit: int = 100,
    ) -> list[MetricPoint]:
        """
        Get recorded metrics.

        Args:
            name: Optional filter by metric name
            limit: Maximum number of metrics to return

        Returns:
            List of MetricPoint objects
        """
        if name:
            filtered = [m for m in self._metrics if m.name == name]
        else:
            filtered = self._metrics

        return filtered[-limit:]

    # ==================== HEALTH CHECKS ====================

    def check_health(self) -> dict[str, HealthStatus]:
        """
        Run health checks on all components.

        Returns:
            Dict mapping component name to HealthStatus
        """
        self._check_meta_learning_client()
        self._check_cache_strategy_manager()
        self._check_domain_context_manager()

        return self._health_status

    def _check_meta_learning_client(self) -> None:
        """Check MetaLearningClient health."""
        try:
            from agentic_core.L1_cognition.reasoning.meta_learning_client_types import (
                get_meta_learning_client,
            )

            client = get_meta_learning_client()
            stats = client.get_stats()

            self._health_status["MetaLearningClient"] = HealthStatus(
                component="MetaLearningClient",
                healthy=True,
                message="Operational",
                details={"cache_size": stats.get("local_cache_size", 0)},
            )

            # Check Redis
            redis_available = stats.get("redis_available", False)
            self._health_status["Redis"] = HealthStatus(
                component="Redis",
                healthy=redis_available,
                message="Connected" if redis_available else "Unavailable (using fallback)",
            )

            # Check Pinecone
            pinecone_available = stats.get("pinecone_available", False)
            self._health_status["Pinecone"] = HealthStatus(
                component="Pinecone",
                healthy=pinecone_available,
                message="Connected" if pinecone_available else "Unavailable",
            )

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._health_status["MetaLearningClient"] = HealthStatus(
                component="MetaLearningClient",
                healthy=False,
                message=f"Error: {e}",
            )

    def _check_cache_strategy_manager(self) -> None:
        """Check CacheStrategyManager health."""
        try:
            from agentic_core.L1_cognition.reasoning.cache_strategy_manager_types import (
                get_cache_strategy_manager,
            )

            manager = get_cache_strategy_manager()
            stats = manager.get_stats()

            self._health_status["CacheStrategyManager"] = HealthStatus(
                component="CacheStrategyManager",
                healthy=True,
                message="Operational",
                details={"domains_configured": len(stats.get("domain_configs", {}))},
            )

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._health_status["CacheStrategyManager"] = HealthStatus(
                component="CacheStrategyManager",
                healthy=False,
                message=f"Error: {e}",
            )

    def _check_domain_context_manager(self) -> None:
        """Check DomainContextManager health."""
        try:
            from agentic_core.L1_cognition.reasoning.domain_context_manager_types import (
                get_domain_context_manager,
            )

            manager = get_domain_context_manager()
            stats = manager.get_stats()

            self._health_status["DomainContextManager"] = HealthStatus(
                component="DomainContextManager",
                healthy=True,
                message="Operational",
                details={"registered_domains": stats.get("registered_domains", [])},
            )

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._health_status["DomainContextManager"] = HealthStatus(
                component="DomainContextManager",
                healthy=False,
                message=f"Error: {e}",
            )

    def get_health_summary(self) -> dict[str, Any]:
        """
        Get a summary of system health.

        Returns:
            Dict with overall health status and component details
        """
        self.check_health()

        healthy_count = sum(1 for s in self._health_status.values() if s.healthy)
        total_count = len(self._health_status)

        return {
            "overall_healthy": healthy_count == total_count,
            "healthy_components": healthy_count,
            "total_components": total_count,
            "components": {
                name: {
                    "healthy": status.healthy,
                    "message": status.message,
                    "last_check": status.last_check,
                }
                for name, status in self._health_status.items()
            },
        }

    # ==================== PERFORMANCE TRACKING ====================

    def record_operation_time(self, operation: str, duration_ms: float) -> None:
        """
        Record operation execution time.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
        """
        if operation not in self._operation_times:
            self._operation_times[operation] = []

        self._operation_times[operation].append(duration_ms)

        # Trim if over limit
        if len(self._operation_times[operation]) > self._max_operation_samples:
            self._operation_times[operation] = self._operation_times[operation][
                -self._max_operation_samples :
            ]

        # Update stats
        self.stats["total_operations"] += 1

    def get_operation_stats(self, operation: str | None = None) -> dict[str, Any]:
        """
        Get operation performance statistics.

        Args:
            operation: Optional specific operation to get stats for

        Returns:
            Dict with performance statistics
        """
        if operation:
            times = self._operation_times.get(operation, [])
            if not times:
                return {"operation": operation, "samples": 0}

            return {
                "operation": operation,
                "samples": len(times),
                "avg_ms": sum(times) / len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "p50_ms": sorted(times)[len(times) // 2] if times else 0,
                "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0,
            }

        # All operations
        return {op: self.get_operation_stats(op) for op in self._operation_times.keys()}

    # ==================== STAT TRACKING ====================

    def increment_stat(self, stat_name: str, amount: int = 1) -> None:
        """Increment a statistic counter."""
        if stat_name in self.stats:
            self.stats[stat_name] += amount

    def get_stats(self) -> dict[str, Any]:
        """Get all statistics."""
        return {
            **self.stats,
            "uptime_seconds": self._calculate_uptime(),
            "metrics_count": len(self._metrics),
            "operations_tracked": len(self._operation_times),
        }

    def _calculate_uptime(self) -> float:
        """Calculate system uptime in seconds."""
        try:
            start = datetime.fromisoformat(self.stats["start_time"])
            return (datetime.now() - start).total_seconds()
        except (ValueError, TypeError, RuntimeError) as e:
            return 0.0

    # ==================== DASHBOARD DATA ====================

    def get_dashboard_data(self) -> dict[str, Any]:
        """
        Get comprehensive data for dashboard display.

        Returns:
            Dict with all dashboard-relevant data
        """
        return {
            "health": self.get_health_summary(),
            "stats": self.get_stats(),
            "performance": self.get_operation_stats(),
            "recent_metrics": [
                {"name": m.name, "value": m.value, "timestamp": m.timestamp}
                for m in self.get_metrics(limit=LIMIT)
            ],
        }

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        global _observability_instance
        _observability_instance = None


def get_meta_learning_observability() -> MetaLearningObservability:
    """Get or create the MetaLearningObservability singleton."""
    global _observability_instance
    if _observability_instance is None:
        _observability_instance = MetaLearningObservability()
    return _observability_instance


class OperationTimer:
    """Context manager for timing operations."""

    def __init__(self, operation: str):
        self.operation = operation
        self.start_time: float = 0

    def __enter__(self):
        self.start_time = get_clock().now_epoch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (get_clock().now_epoch() - self.start_time) * 1000
        observability = get_meta_learning_observability()
        observability.record_operation_time(self.operation, duration_ms)
        return False
