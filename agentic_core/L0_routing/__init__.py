"""
L0 Routing Layer
================

Provides routing, capacity governance, and policy enforcement for request routing.
"""

# P1 Core exports
# P3/L0 Routing Capacity Governance exports
from agentic_core.L0_routing.reasoning.capacity_aware_router import (
    RoutingCapacityContext,
    RoutingPolicyContext,
    capacity_aware_routing,
    capacity_snapshot_emitted,
    choose_route_with_capacity,
    choose_route_with_simple_capacity,
    query_capacity_snapshots,
    route_chosen_with_capacity,
)
from agentic_core.L0_routing.reasoning.capacity_snapshot import (
    CapacityDecisionReason,
    CapacitySnapshot,
    RouteCapacityMetrics,
    RouteDegradationState,
    RoutingCapacityError,
    get_capacity_registry,
    reset_capacity_registry,
)
from agentic_core.L0_routing.reasoning.optimization_orchestrator import (
    OptimizationWindow,
    PolicyContext,
    RoutingHistory,
    apply_optimization_with_governance,
    get_optimization_recommendations,
    historical_outcomes_analyzed,
    optimize_routing_policy,
    optimizes_routing,
    query_routing_optimizations,
    route_candidate_ranked,
    routing_governance_approved,
    routing_optimization_persisted,
    routing_policy_adapted,
)

# P4/L0 Routing Optimization exports
from agentic_core.L0_routing.reasoning.routing_optimization import (
    RoutingOptimizationError,
    RoutingOptimizationRecord,
    cost_estimate,
    get_routing_optimization_registry,
    historical_failure_rate,
    historical_success_rate,
    median_latency_ms,
    optimization_reason_hash,
    optimization_window_end,
    optimization_window_start,
    p95_latency_ms,
    recommended_route_rank,
    route_candidate_hash,
    # Dataclass field exports for ADG scanner detection
    routing_optimization_id,
)
from agentic_core.L0_routing.types.p1_routing_protocol import P1Core, P1RoutingProtocol
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    # P1 Core
    "P1Core",
    "P1RoutingProtocol",
    # Capacity Records
    "CapacitySnapshot",
    "RouteCapacityMetrics",
    "RouteDegradationState",
    "CapacityDecisionReason",
    # Exception Classes
    "RoutingCapacityError",
    # Registry Access
    "get_capacity_registry",
    "reset_capacity_registry",
    # Context Classes
    "RoutingCapacityContext",
    "RoutingPolicyContext",
    # Emission Functions
    "choose_route_with_capacity",
    "query_capacity_snapshots",
    "choose_route_with_simple_capacity",
    # ADG Edge Emitters
    "capacity_aware_routing",
    "route_chosen_with_capacity",
    "capacity_snapshot_emitted",
    # Routing Optimization Records
    "RoutingOptimizationRecord",
    # Routing Optimization Exception Classes
    "RoutingOptimizationError",
    # Routing Optimization Registry Access
    "get_routing_optimization_registry",
    # Routing Optimization Context Classes
    "RoutingHistory",
    "OptimizationWindow",
    "PolicyContext",
    # Routing Optimization Functions
    "optimize_routing_policy",
    "query_routing_optimizations",
    "get_optimization_recommendations",
    "apply_optimization_with_governance",
    # Routing Optimization ADG Edge Emitters
    "optimizes_routing",
    "historical_outcomes_analyzed",
    "routing_policy_adapted",
    "routing_optimization_persisted",
    "route_candidate_ranked",
    "routing_governance_approved",
    # Routing Optimization Dataclass field exports for ADG scanner detection
    "routing_optimization_id",
    "optimization_window_start",
    "optimization_window_end",
    "route_candidate_hash",
    "historical_success_rate",
    "historical_failure_rate",
    "median_latency_ms",
    "p95_latency_ms",
    "cost_estimate",
    "recommended_route_rank",
    "optimization_reason_hash",
]
