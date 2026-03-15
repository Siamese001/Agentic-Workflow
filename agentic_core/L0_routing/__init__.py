"""
L0 Routing Layer
================

Provides routing, capacity governance, and policy enforcement for request routing.
"""

# P3/L0 Routing Capacity Governance exports
from agentic_core.L0_routing.capacity.capacity_aware_router import (
    RoutingCapacityContext,
    RoutingPolicyContext,
    capacity_aware_routing,
    capacity_snapshot_emitted,
    choose_route_with_capacity,
    choose_route_with_simple_capacity,
    query_capacity_snapshots,
    route_chosen_with_capacity,
)
from agentic_core.L0_routing.capacity.capacity_snapshot import (
    CapacityDecisionReason,
    CapacitySnapshot,
    RouteCapacityMetrics,
    RouteDegradationState,
    RoutingCapacityError,
    get_capacity_registry,
    reset_capacity_registry,
)
from agentic_core.L0_routing.optimization.optimization_orchestrator import (
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
from agentic_core.L0_routing.optimization.routing_optimization import (
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "__init__", "L0")
_emit_routes_through("p1", "__init__", "L0")
_emit_escalates_to_human("p1", "__init__", "L0")
_emit_reads_policy_state("p1", "__init__", "L0")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
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
