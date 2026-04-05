"""L6 Observability Dashboard module.

Provides runtime telemetry aggregation into queryable operational control surfaces
that expose system health, throughput, failures, and bottlenecks across layers.
"""

# P3/L6 Observability Dashboard exports
from agentic_core.L6_observability.utils.dashboard.dashboard_aggregate import (
    DashboardAggregate,
    DashboardAggregateError,
    DashboardSnapshot,
    HealthFlag,
)
from agentic_core.L6_observability.utils.dashboard.analytics_dashboard import (
    AnalyticsDashboard,
    ChartData,
    DashboardConfig,
    DashboardWidget,
    get_dashboard_data,
    get_dashboard_summary,
    get_global_dashboard,
    start_analytics_dashboard,
    stop_analytics_dashboard,
)
from agentic_core.L6_observability.utils.dashboard.dashboard_orchestrator import (
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
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

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
