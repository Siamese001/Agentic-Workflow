# API Documentation: capacity_aware_router

**Target Audience**: developers, api_users

# capacity_aware_router API Documentation

**File**: `capacity_aware_router.py`
**Classes**: 2
**Functions**: 14

## Classes

- **RoutingCapacityContext**
- **RoutingPolicyContext**

## Functions

- **capacity_aware_routing** -> None
- **route_chosen_with_capacity** -> None
- **capacity_snapshot_emitted** -> None
- **choose_route_with_capacity** -> tuple[str, CapacitySnapshot]
- **_load_capacity_metrics** -> dict[str, RouteCapacityMetrics]
- **_filter_by_policy_constraints** -> list[str]
- **_select_route_by_capacity** -> str
- **_attach_to_routing_trace** -> None
- **query_capacity_snapshots** -> list[CapacitySnapshot]
- **choose_route_with_simple_capacity** -> tuple[str, CapacitySnapshot]
- **create** -> RoutingCapacityContext
- **create** -> RoutingPolicyContext
- **capacity_aware_routing** -> None
- **route_chosen_with_capacity** -> None


## Class: RoutingCapacityContext

**Description**: Context for capacity-aware routing.

### Methods

#### create
**Parameters**: cls, run_id, trace_id, routing_contract_id, router_id
**Returns**: RoutingCapacityContext



## Class: RoutingPolicyContext

**Description**: Policy constraints for routing decisions.

### Methods

#### create
**Parameters**: cls, allow_degraded, allow_saturated, require_capacity_aware, max_queue_depth, max_failure_rate
**Returns**: RoutingPolicyContext



## Function: capacity_aware_routing

**Parameters**: snapshot_id, router_id, candidates, chosen, reason
**Returns**: None
**Description**: ADG edge emitter for capacity_aware_routing.



## Function: route_chosen_with_capacity

**Parameters**: snapshot_id, chosen_route, capacity_score, degradation
**Returns**: None
**Description**: ADG edge emitter for route_chosen_with_capacity.



## Function: capacity_snapshot_emitted

**Parameters**: snapshot_id, run_id, trace_id, router_id, candidates, chosen
**Returns**: None
**Description**: ADG edge emitter for capacity_snapshot_emitted.



## Function: choose_route_with_capacity

**Parameters**: routing_context, candidate_routes, capacity_snapshot, policy_context
**Returns**: tuple[str, CapacitySnapshot]
**Description**: Mandatory entrypoint for capacity-aware routing — P3/L0 spec §3.

    Steps (in order, all mandatory):
      1. resolve candidate routes
      2. load capacity metrics for each candidate
      3. attach queue depth and in-flight workload
      4. compare against routing policy constraints
      5. choose route with explicit capacity rationale
      6. persist capacity-aware routing decision
      7. attach decision to routing trace

    Args:
        routing_context: RoutingCapacityContext with run_id, trace_id, etc.
        candidate_routes: List of candidate route names
        capacity_snapshot: Optional existing CapacitySnapshot (for updates)
        policy_context: Policy constraints for routing decisions
        registry: CapacityRegistry to use (uses global if None)

    Returns:
        (chosen_route, capacity_snapshot) — selected route and persisted snapshot

    Raises:
        RoutingCapacityError: If capacity governance is required but missing (Gate A)
    



## Function: _load_capacity_metrics

**Parameters**: candidate_routes
**Returns**: dict[str, RouteCapacityMetrics]
**Description**: Load capacity metrics for candidate routes.



## Function: _filter_by_policy_constraints

**Parameters**: candidate_routes, capacity_metrics, policy_context
**Returns**: list[str]
**Description**: Filter routes by policy constraints.



## Function: _select_route_by_capacity

**Parameters**: available_routes, capacity_metrics, decision_reason
**Returns**: str
**Description**: Select best route by capacity metrics.



## Function: _attach_to_routing_trace

**Parameters**: routing_context, snapshot
**Returns**: None
**Description**: Attach capacity decision to routing trace.



## Function: query_capacity_snapshots

**Parameters**: run_id, trace_id, router_id, snapshot_id
**Returns**: list[CapacitySnapshot]
**Description**: Query capacity snapshots.



## Function: choose_route_with_simple_capacity

**Parameters**: run_id, trace_id, routing_contract_id, router_id, candidate_routes
**Returns**: tuple[str, CapacitySnapshot]
**Description**: Convenience wrapper for simple capacity-aware routing.



## Function: create

**Parameters**: cls, run_id, trace_id, routing_contract_id, router_id
**Returns**: RoutingCapacityContext


## Function: create

**Parameters**: cls, allow_degraded, allow_saturated, require_capacity_aware, max_queue_depth, max_failure_rate
**Returns**: RoutingPolicyContext


## Function: capacity_aware_routing

**Parameters**: snapshot_id, router_id, candidates, chosen, reason
**Returns**: None
**Description**: ADG edge emitter for capacity_aware_routing.



## Function: route_chosen_with_capacity

**Parameters**: snapshot_id, chosen_route, capacity_score, degradation
**Returns**: None
**Description**: ADG edge emitter for route_chosen_with_capacity.



## Usage Examples

### Class Usage

```python
# Using RoutingCapacityContext
routingcapacitycontext = RoutingCapacityContext()
routingcapacitycontext.create()
```

```python
# Using RoutingPolicyContext
routingpolicycontext = RoutingPolicyContext()
routingpolicycontext.create()
```

### Function Usage

```python
# Using capacity_aware_routing
result = capacity_aware_routing(snapshot_id, router_id)
```

```python
# Using route_chosen_with_capacity
result = route_chosen_with_capacity(snapshot_id, chosen_route)
```

```python
# Using capacity_snapshot_emitted
result = capacity_snapshot_emitted(snapshot_id, run_id)
```



---
**Generated**: 2026-03-26T09:39:02.575380
**Type**: api_reference
**Quality**: comprehensive
