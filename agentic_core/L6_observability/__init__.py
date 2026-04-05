"""
L6 observability
================
Monitoring, benchmarking, and observability components.
"""
from enum import Enum

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
from agentic_core.L6_observability.utils.dashboard.dashboard_aggregate import (
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
from agentic_core.L6_observability.utils.dashboard.dashboard_orchestrator import (
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

# Wave 3: Auto-Persistence Tracing Adapter
from agentic_core.L6_observability.utils.engines.auto_persistence_adapter import (
    AutoPersistenceTracingAdapter,
    get_auto_persistence_tracer,
)

# Wave 4: Meta-Learning Bridge
from agentic_core.L6_observability.utils.engines.meta_learning_bridge import (
    L6MetaLearningBridge,
    MetaLearningRecord,
    get_meta_learning_bridge,
)
from agentic_core.L6_observability.utils.engines.metrics_server import (
    MetricsServerContext,
    get_metrics_endpoint_url,
    get_server_status,
    start_metrics_server,
    stop_metrics_server,
)

# P3/L6 Observability Dashboard exports
from agentic_core.L6_observability.enforcement.mcp_drift_store import (
    MCPDriftMonitor,
    MCPL6ObservabilityStore,
    MCPL6PersistenceConfig,
)

# Wave 0: Prometheus Metrics
from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
    AGENTIC_REGISTRY,
)

# Wave 0: Performance
from agentic_core.L6_observability.utils.performance.performance_emitter import (
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
from agentic_core.L6_observability.utils.performance.performance_registry import (
    BudgetViolationError,
    PerformanceMissingError,
    PerformanceRecord,
    PerformanceRegistry,
    get_performance_registry,
    reset_performance_registry,
)

# Enhanced Observability System
from agentic_core.L6_observability.utils.enhanced_observability import (
    Alert,
    AlertSeverity,
    EnhancedObservability,
    HealthCheck,
    HealthStatus,
    SystemHealth,
    SystemMetric,
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
    # Prometheus Metrics (Wave 0)
    "AGENTIC_REGISTRY",
    "start_metrics_server",
    "stop_metrics_server",
    "MetricsServerContext",
    "get_metrics_endpoint_url",
    "get_server_status",
    # Auto-Persistence (Wave 3)
    "AutoPersistenceTracingAdapter",
    "get_auto_persistence_tracer",
    # Meta-Learning Bridge (Wave 4)
    "L6MetaLearningBridge",
    "MetaLearningRecord",
    "get_meta_learning_bridge",
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
    # Enhanced Observability System
    "EnhancedObservability",
    "Alert",
    "AlertSeverity",
    "HealthCheck",
    "HealthStatus",
    "SystemHealth",
    "SystemMetric",
    # MCP Drift Store exports
    "MCPL6ObservabilityStore",
    "MCPL6PersistenceConfig",
    "MCPDriftMonitor",
]
