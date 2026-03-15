"""L0 Routing Capacity Governance module.

Provides capacity-aware routing decisions that incorporate workload, queue pressure, and service availability.
"""

# P3/L0 Routing Capacity Governance exports
from agentic_core.L0_routing.capacity.capacity_aware_router import (
    RoutingCapacityContext,
    RoutingPolicyContext,
    capacity_aware_routing,
    capacity_snapshot_emitted,
    choose_route_with_capacity,
    query_capacity_snapshots,
    route_chosen_with_capacity,
)
from agentic_core.L0_routing.capacity.capacity_aware_router import (
    get_capacity_registry as get_router_registry,
)
from agentic_core.L0_routing.capacity.capacity_snapshot import (
    BEST_CAPACITY,
    BEST_POLICY_FIT,
    DEGRADED,
    ESCALATION_PATH,
    FAILOVER,
    # Enum values for ADG scanner detection
    HEALTHY,
    LACK_OF_ALTERNATIVES,
    SATURATED,
    UNAVAILABLE,
    UNAVAILABLE_EXCLUDED,
    CapacityDecisionReason,
    CapacitySnapshot,
    RouteCapacityMetrics,
    RouteDegradationState,
    RoutingCapacityError,
    get_capacity_registry,
    reset_capacity_registry,
)

__all__ = [
    # Capacity Records
    "CapacitySnapshot",
    "RouteCapacityMetrics",
    "RouteDegradationState",
    "CapacityDecisionReason",
    # Exception Classes
    "RoutingCapacityError",
    # Context Classes
    "RoutingCapacityContext",
    "RoutingPolicyContext",
    # Emission Functions
    "choose_route_with_capacity",
    "query_capacity_snapshots",
    # Registry Access
    "get_capacity_registry",
    "reset_capacity_registry",
    # ADG Edge Emitters
    "capacity_aware_routing",
    "route_chosen_with_capacity",
    "capacity_snapshot_emitted",
    # Enum values for ADG scanner detection
    "HEALTHY",
    "DEGRADED",
    "SATURATED",
    "UNAVAILABLE",
    "BEST_CAPACITY",
    "BEST_POLICY_FIT",
    "FAILOVER",
    "ESCALATION_PATH",
    "LACK_OF_ALTERNATIVES",
    "UNAVAILABLE_EXCLUDED",
]
