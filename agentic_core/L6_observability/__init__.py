"""
L6 observability
================
Monitoring, benchmarking, and observability components.
"""

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

# P3/L6 Observability Dashboard exports
from agentic_core.L6_observability.dashboard.dashboard_aggregate import (
    CRITICAL,
    DEGRADED,
    # Enum values for ADG scanner detection
    HEALTHY,
    UNKNOWN,
    DashboardAggregate,
    DashboardAggregateError,
    DashboardSnapshot,
    HealthFlag,
    active_run_count,
    # Dataclass field exports for ADG scanner detection
    dashboard_snapshot_id,
    degraded_component_flags,
    execution_failure_rate,
    execution_success_rate,
    get_dashboard_registry,
    human_escalation_rate,
    median_latency_by_stage,
    p95_latency_by_stage,
    policy_block_rate,
    queue_depth_summary,
    reasoning_throughput,
    reset_dashboard_registry,
    routing_throughput,
    snapshot_tick,
)
from agentic_core.L6_observability.dashboard.dashboard_orchestrator import (
    DashboardPolicy,
    TelemetryWindow,
    aggregate_runtime_observability,
    dashboard_aggregated,
    get_bottleneck_analysis,
    get_latency_metrics,
    get_system_health_summary,
    get_throughput_metrics,
    health_computed,
    metrics_collected,
    query_dashboard_snapshots,
    query_exposed,
    snapshot_persisted,
)
from agentic_core.L6_observability.performance.performance_emitter import (
    LatencyBudget,
    PerformanceContext,
    StageOwner,
    measure_stage_timing,
    performance_record_emitted,
    query_performance_records,
    record_execution_performance,
    record_reasoning_performance,
    record_routing_performance,
    record_stage_performance,
)

# P2/L6 Performance Observability exports
from agentic_core.L6_observability.performance.performance_registry import (
    BudgetViolationError,
    PerformanceMissingError,
    PerformanceRecord,
    PerformanceRegistry,
    get_performance_registry,
    reset_performance_registry,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    "SovereignBaseAgent",
    "BATCH_SIZE",
    "BUFFER_SIZE",
    "DEFAULT_SLEEP",
    "DEFAULT_TIMEOUT",
    "MAX_DEPTH",
    "MAX_FILES",
    "MAX_RETRIES",
    "THRESHOLD",
    # Performance Records
    "PerformanceRecord",
    "PerformanceRegistry",
    # Exception Classes
    "PerformanceMissingError",
    "BudgetViolationError",
    # Registry Access
    "get_performance_registry",
    "reset_performance_registry",
    # Context Classes
    "PerformanceContext",
    "StageOwner",
    "LatencyBudget",
    # Emission Functions
    "record_stage_performance",
    "query_performance_records",
    "measure_stage_timing",
    "record_routing_performance",
    "record_reasoning_performance",
    "record_execution_performance",
    # ADG Edge Emitters
    "performance_record_emitted",
    # Dashboard Records
    "DashboardSnapshot",
    "DashboardAggregate",
    # Dashboard Enums
    "HealthFlag",
    # Dashboard Exception Classes
    "DashboardAggregateError",
    # Dashboard Registry Access
    "get_dashboard_registry",
    "reset_dashboard_registry",
    # Dashboard Context Classes
    "TelemetryWindow",
    "DashboardPolicy",
    # Dashboard Aggregation Functions
    "aggregate_runtime_observability",
    "query_dashboard_snapshots",
    "get_system_health_summary",
    "get_throughput_metrics",
    "get_latency_metrics",
    "get_bottleneck_analysis",
    # Dashboard ADG Edge Emitters
    "dashboard_aggregated",
    "health_computed",
    "metrics_collected",
    "snapshot_persisted",
    "query_exposed",
    # Dashboard Enum values for ADG scanner detection
    "HEALTHY",
    "DEGRADED",
    "CRITICAL",
    "UNKNOWN",
    # Dashboard Dataclass field exports for ADG scanner detection
    "dashboard_snapshot_id",
    "snapshot_tick",
    "active_run_count",
    "routing_throughput",
    "reasoning_throughput",
    "execution_success_rate",
    "execution_failure_rate",
    "policy_block_rate",
    "human_escalation_rate",
    "queue_depth_summary",
    "median_latency_by_stage",
    "p95_latency_by_stage",
    "degraded_component_flags",
]
