"""L6 Observability Dashboard module.

Provides runtime telemetry aggregation into queryable operational control surfaces
that expose system health, throughput, failures, and bottlenecks across layers.
"""

# P3/L6 Observability Dashboard exports
from agentic_core.L6_observability.dashboard.dashboard_aggregate import (
    DashboardAggregate,
    DashboardAggregateError,
    DashboardSnapshot,
    HealthFlag,
)
from agentic_core.L6_observability.dashboard.dashboard_orchestrator import (
    DashboardPolicy,
    TelemetryWindow,
    aggregate_runtime_observability,
    dashboard_aggregated,
    get_bottleneck_analysis,
    get_dashboard_registry,
    get_latency_metrics,
    get_system_health_summary,
    get_throughput_metrics,
    health_computed,
    metrics_collected,
    query_dashboard_snapshots,
    query_exposed,
    reset_dashboard_registry,
    snapshot_persisted,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L6")
_emit_routes_through("p1", "__init__", "L6")
_emit_escalates_to_human("p1", "__init__", "L6")
_emit_reads_policy_state("p1", "__init__", "L6")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Dashboard Records
    "DashboardAggregate",
    "DashboardSnapshot",
    # Enums
    "HealthFlag",
    # Exception Classes
    "DashboardAggregateError",
    # Context Classes
    "TelemetryWindow",
    "DashboardPolicy",
    # Aggregation Functions
    "aggregate_runtime_observability",
    "query_dashboard_snapshots",
    "get_dashboard_registry",
    "reset_dashboard_registry",
    # Query Functions
    "get_system_health_summary",
    "get_throughput_metrics",
    "get_latency_metrics",
    "get_bottleneck_analysis",
    # ADG Edge Emitters
    "dashboard_aggregated",
    "health_computed",
    "metrics_collected",
    "snapshot_persisted",
    "query_exposed",
]
