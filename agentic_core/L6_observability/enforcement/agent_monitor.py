"""
Unified Agent Monitor - Execution monitoring engine.

Extracted from schemas/UnifiedAgent_monitor_types.py during Schema Dissolution.
Logic components: UnifiedAgentMonitor, ExecutionTimer, get_monitor.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from agentic_core.L2_execution.determinism.execution_proof_emitter import ExecutionProofEmitter
from agentic_core.L6_observability.types.monitor_types import (
    AggregatedMetrics,
    ExecutionMetrics,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

_proof_emitter = ExecutionProofEmitter("L6.UnifiedAgentMonitor")

Logger = logging.getLogger(__name__)


class UnifiedAgentMonitor:
    """
    Monitor for unified agent consolidation.

    Tracks:
    - Execution counts and timing
    - Success/failure rates
    - Category distribution
    - Strategy usage patterns
    """

    _instance: UnifiedAgentMonitor | None = None

    def __new__(cls) -> UnifiedAgentMonitor:
        """Singleton pattern for global monitoring."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize monitor."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "UnifiedAgentMonitor.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "UnifiedAgentMonitor.__init__", "p0_governance")
        if self._initialized:
            return

        self._metrics: list[ExecutionMetrics] = []
        self._aggregated = AggregatedMetrics()
        self._start_time = datetime.utcnow()
        self._initialized = True

        Logger.info("UnifiedAgentMonitor initialized")

    def record_execution(
        self,
        agent_name: str,
        category: str,
        strategy_type: str,
        execution_time_ms: float,
        success: bool,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an execution metric."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "UnifiedAgentMonitor.record_execution"
        )

        metric = ExecutionMetrics(
            agent_name=agent_name,
            category=category,
            strategy_type=strategy_type,
            execution_time_ms=execution_time_ms,
            success=success,
            metadata=metadata or {},
        )

        self._metrics.append(metric)
        self._update_aggregated(metric)

    def record_facade_execution(
        self,
        facade_agent: str,
        strategy_type: str,
        execution_time_ms: float,
        success: bool,
    ) -> None:
        """Record a facade agent execution for migration monitoring."""
        self._aggregated.facade_executions += 1

        if facade_agent not in self._aggregated.facade_agents:
            self._aggregated.facade_agents[facade_agent] = 0
        self._aggregated.facade_agents[facade_agent] += 1

        # Also record as regular execution
        self.record_execution(
            agent_name=facade_agent,
            category="facade",
            strategy_type=strategy_type,
            execution_time_ms=execution_time_ms,
            success=success,
            metadata={"is_facade": True},
        )

    def _update_aggregated(self, metric: ExecutionMetrics) -> None:
        """Update aggregated metrics."""
        self._aggregated.total_executions += 1

        if metric.success:
            self._aggregated.successful_executions += 1
        else:
            self._aggregated.failed_executions += 1

        self._aggregated.total_execution_time_ms += metric.execution_time_ms

        if self._aggregated.total_executions > 0:
            self._aggregated.avg_execution_time_ms = (
                self._aggregated.total_execution_time_ms / self._aggregated.total_executions
            )

        self._aggregated.min_execution_time_ms = min(
            self._aggregated.min_execution_time_ms,
            metric.execution_time_ms,
        )
        self._aggregated.max_execution_time_ms = max(
            self._aggregated.max_execution_time_ms,
            metric.execution_time_ms,
        )

        # Track by category
        if metric.category not in self._aggregated.executions_by_category:
            self._aggregated.executions_by_category[metric.category] = 0
        self._aggregated.executions_by_category[metric.category] += 1

        # Track by strategy
        if metric.strategy_type not in self._aggregated.executions_by_strategy:
            self._aggregated.executions_by_strategy[metric.strategy_type] = 0
        self._aggregated.executions_by_strategy[metric.strategy_type] += 1

    def get_metrics(self) -> AggregatedMetrics:
        """Get aggregated metrics."""
        return self._aggregated

    def get_health_status(self) -> dict[str, Any]:
        """Get health status for monitoring endpoints."""
        success_rate = (
            self._aggregated.successful_executions / self._aggregated.total_executions
            if self._aggregated.total_executions > 0
            else 1.0
        )

        return {
            "status": "healthy" if success_rate >= 0.95 else "degraded",
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "total_executions": self._aggregated.total_executions,
            "success_rate": success_rate,
            "avg_execution_time_ms": self._aggregated.avg_execution_time_ms,
            "categories_active": list(self._aggregated.executions_by_category.keys()),
            "strategies_active": list(self._aggregated.executions_by_strategy.keys()),
            # Phase 4: Facade migration metrics
            "facade_executions": self._aggregated.facade_executions,
            "facade_agents_active": list(self._aggregated.facade_agents.keys()),
        }

    def get_facade_migration_status(self) -> dict[str, Any]:
        """Get facade migration status for Phase 4 monitoring."""
        converted_facades = [
            "StructureHealerAgent",
            "CodeValidatorAgent",
            "StructuralValidatorAgent",
            "LocationHealerAgent",
        ]

        facade_usage = {agent: self._aggregated.facade_agents.get(agent, 0) for agent in converted_facades}

        total_facade_calls = sum(facade_usage.values())

        return {
            "migration_phase": "Phase 4 - Monitoring",
            "converted_facades": converted_facades,
            "facade_usage": facade_usage,
            "total_facade_calls": total_facade_calls,
            "facades_with_activity": [agent for agent, count in facade_usage.items() if count > 0],
            "migration_health": (
                "healthy"
                if total_facade_calls > 0 or self._aggregated.total_executions == 0
                else "no_facade_activity"
            ),
        }

    def get_recent_metrics(self, count: int = 100) -> list[ExecutionMetrics]:
        """Get recent execution metrics."""
        return self._metrics[-count:]

    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics = []
        self._aggregated = AggregatedMetrics()
        self._start_time = datetime.utcnow()


class ExecutionTimer:
    """Context manager for timing executions."""

    def __init__(
        self,
        monitor: UnifiedAgentMonitor,
        agent_name: str,
        category: str,
        strategy_type: str,
    ) -> None:
        """Initialize timer."""
        self.monitor = monitor
        self.agent_name = agent_name
        self.category = category
        self.strategy_type = strategy_type
        self.start_time: float = 0.0
        self.success = True
        self.metadata: dict[str, Any] = {}

    def __enter__(self) -> ExecutionTimer:
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop timing and record."""
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is not None:
            self.success = False
            self.metadata["error"] = str(exc_val)

        self.monitor.record_execution(
            agent_name=self.agent_name,
            category=self.category,
            strategy_type=self.strategy_type,
            execution_time_ms=elapsed_ms,
            success=self.success,
            metadata=self.metadata,
        )


def get_monitor() -> UnifiedAgentMonitor:
    """Get the global monitor instance."""
    return UnifiedAgentMonitor()


__all__ = [
    "UnifiedAgentMonitor",
    "ExecutionTimer",
    "get_monitor",
]
