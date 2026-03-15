"""L0 Routing Optimization module.

Provides adaptive routing optimization that learns from historical routing outcomes
to improve efficiency and reliability.
"""

# P4/L0 Routing Optimization exports
from agentic_core.L0_routing.optimization.optimization_orchestrator import (
    OptimizationWindow,
    PolicyContext,
    RoutingHistory,
    apply_optimization_with_governance,
    get_optimization_recommendations,
    get_routing_optimization_registry,
    historical_outcomes_analyzed,
    optimize_routing_policy,
    optimizes_routing,
    query_routing_optimizations,
    route_candidate_ranked,
    routing_governance_approved,
    routing_optimization_persisted,
    routing_policy_adapted,
)
from agentic_core.L0_routing.optimization.routing_optimization import (
    RoutingOptimizationError,
    RoutingOptimizationRecord,
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
    # Routing Optimization Records
    "RoutingOptimizationRecord",
    # Exception Classes
    "RoutingOptimizationError",
    # Context Classes
    "RoutingHistory",
    "OptimizationWindow",
    "PolicyContext",
    # Optimization Functions
    "optimize_routing_policy",
    "query_routing_optimizations",
    "get_routing_optimization_registry",
    # Query Functions
    "get_optimization_recommendations",
    "apply_optimization_with_governance",
    # ADG Edge Emitters
    "optimizes_routing",
    "historical_outcomes_analyzed",
    "routing_policy_adapted",
    "routing_optimization_persisted",
    "route_candidate_ranked",
    "routing_governance_approved",
]
