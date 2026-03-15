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
