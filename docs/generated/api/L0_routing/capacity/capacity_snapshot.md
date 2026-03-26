# API Documentation: capacity_snapshot

**Target Audience**: developers, api_users

# capacity_snapshot API Documentation

**File**: `capacity_snapshot.py`
**Classes**: 6
**Functions**: 19

## Classes

- **RouteDegradationState** (inherits from Enum)
- **CapacityDecisionReason** (inherits from Enum)
- **RoutingCapacityError** (inherits from Exception)
- **RouteCapacityMetrics**
- **CapacitySnapshot**
- **CapacityRegistry**

## Functions

- **get_capacity_registry** -> CapacityRegistry
- **reset_capacity_registry** -> None
- **create** -> RouteCapacityMetrics
- **is_available_for_routing** -> bool
- **get_capacity_score** -> float
- **create** -> CapacitySnapshot
- **get_chosen_route_metrics** -> RouteCapacityMetrics | None
- **has_unavailable_chosen_route** -> bool
- **has_degraded_chosen_route_without_reason** -> bool
- **__init__** -> None
- **get_instance** -> CapacityRegistry
- **persist_snapshot** -> None
- **query_by_run_id** -> list[CapacitySnapshot]
- **query_by_trace_id** -> list[CapacitySnapshot]
- **query_by_router_id** -> list[CapacitySnapshot]
- **query_by_snapshot_id** -> CapacitySnapshot | None
- **get_snapshot_count** -> int
- **verify_snapshot_exists** -> bool
- **verify_capacity_metrics_present** -> bool


## Class: RouteDegradationState

**Description**: Degradation states for routing destinations.

**Inherits from**: Enum



## Class: CapacityDecisionReason

**Description**: Reasons for capacity-aware routing decisions.

**Inherits from**: Enum



## Class: RoutingCapacityError

**Description**: Raised when routing decision occurs without capacity snapshot (Gate A).

**Inherits from**: Exception



## Class: RouteCapacityMetrics

**Description**: Capacity metrics for a single routing candidate.

### Methods

#### create
**Parameters**: cls, route_name, queue_depth, in_flight_work, recent_latency_ms, failure_rate, degradation_state
**Returns**: RouteCapacityMetrics

#### is_available_for_routing
**Parameters**: self
**Returns**: bool
**Description**: Check if route is available for routing (Gate C).

#### get_capacity_score
**Parameters**: self
**Returns**: float
**Description**: Calculate capacity score (lower is better).



## Class: CapacitySnapshot

**Description**: Immutable capacity snapshot for routing decisions (13 required fields).

### Methods

#### create
**Parameters**: cls, run_id, trace_id, routing_contract_id, router_id, candidate_routes, chosen_route, capacity_metrics, decision_reason
**Returns**: CapacitySnapshot
**Description**: Factory to create CapacitySnapshot with computed fields.

#### get_chosen_route_metrics
**Parameters**: self
**Returns**: RouteCapacityMetrics | None
**Description**: Get capacity metrics for the chosen route.

#### has_unavailable_chosen_route
**Parameters**: self
**Returns**: bool
**Description**: Check if chosen route is unavailable (Gate C violation).

#### has_degraded_chosen_route_without_reason
**Parameters**: self
**Returns**: bool
**Description**: Check if degraded route chosen without decision reason (Gate D violation).



## Class: CapacityRegistry

**Description**: Thread-safe registry for capacity snapshots and queries.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: CapacityRegistry
**Description**: Singleton accessor.

#### persist_snapshot
**Parameters**: self, snapshot
**Returns**: None
**Description**: Persist a capacity snapshot.

#### query_by_run_id
**Parameters**: self, run_id
**Returns**: list[CapacitySnapshot]
**Description**: Query capacity snapshots by run_id.

#### query_by_trace_id
**Parameters**: self, trace_id
**Returns**: list[CapacitySnapshot]
**Description**: Query capacity snapshots by trace_id.

#### query_by_router_id
**Parameters**: self, router_id
**Returns**: list[CapacitySnapshot]
**Description**: Query capacity snapshots by router_id.

#### query_by_snapshot_id
**Parameters**: self, snapshot_id
**Returns**: CapacitySnapshot | None
**Description**: Query capacity snapshot by capacity_snapshot_id.

#### get_snapshot_count
**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of capacity snapshots, optionally filtered by run_id.

#### verify_snapshot_exists
**Parameters**: self, snapshot_id
**Returns**: bool
**Description**: Verify capacity snapshot exists (Gate A).

#### verify_capacity_metrics_present
**Parameters**: self, snapshot_id
**Returns**: bool
**Description**: Verify snapshot has queue depth and in-flight metrics (Gate B).



## Function: get_capacity_registry

**Returns**: CapacityRegistry
**Description**: Get the singleton CapacityRegistry instance.



## Function: reset_capacity_registry

**Returns**: None
**Description**: Reset the singleton CapacityRegistry (for testing).



## Function: create

**Parameters**: cls, route_name, queue_depth, in_flight_work, recent_latency_ms, failure_rate, degradation_state
**Returns**: RouteCapacityMetrics


## Function: is_available_for_routing

**Parameters**: self
**Returns**: bool
**Description**: Check if route is available for routing (Gate C).



## Function: get_capacity_score

**Parameters**: self
**Returns**: float
**Description**: Calculate capacity score (lower is better).



## Function: create

**Parameters**: cls, run_id, trace_id, routing_contract_id, router_id, candidate_routes, chosen_route, capacity_metrics, decision_reason
**Returns**: CapacitySnapshot
**Description**: Factory to create CapacitySnapshot with computed fields.



## Function: get_chosen_route_metrics

**Parameters**: self
**Returns**: RouteCapacityMetrics | None
**Description**: Get capacity metrics for the chosen route.



## Function: has_unavailable_chosen_route

**Parameters**: self
**Returns**: bool
**Description**: Check if chosen route is unavailable (Gate C violation).



## Function: has_degraded_chosen_route_without_reason

**Parameters**: self
**Returns**: bool
**Description**: Check if degraded route chosen without decision reason (Gate D violation).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: CapacityRegistry
**Description**: Singleton accessor.



## Function: persist_snapshot

**Parameters**: self, snapshot
**Returns**: None
**Description**: Persist a capacity snapshot.



## Function: query_by_run_id

**Parameters**: self, run_id
**Returns**: list[CapacitySnapshot]
**Description**: Query capacity snapshots by run_id.



## Function: query_by_trace_id

**Parameters**: self, trace_id
**Returns**: list[CapacitySnapshot]
**Description**: Query capacity snapshots by trace_id.



## Function: query_by_router_id

**Parameters**: self, router_id
**Returns**: list[CapacitySnapshot]
**Description**: Query capacity snapshots by router_id.



## Function: query_by_snapshot_id

**Parameters**: self, snapshot_id
**Returns**: CapacitySnapshot | None
**Description**: Query capacity snapshot by capacity_snapshot_id.



## Function: get_snapshot_count

**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of capacity snapshots, optionally filtered by run_id.



## Function: verify_snapshot_exists

**Parameters**: self, snapshot_id
**Returns**: bool
**Description**: Verify capacity snapshot exists (Gate A).



## Function: verify_capacity_metrics_present

**Parameters**: self, snapshot_id
**Returns**: bool
**Description**: Verify snapshot has queue depth and in-flight metrics (Gate B).



## Usage Examples

### Class Usage

```python
# Using RouteDegradationState
routedegradationstate = RouteDegradationState()
```

```python
# Using CapacityDecisionReason
capacitydecisionreason = CapacityDecisionReason()
```

```python
# Using RoutingCapacityError
routingcapacityerror = RoutingCapacityError()
```

### Function Usage

```python
# Using get_capacity_registry
result = get_capacity_registry()
```

```python
# Using reset_capacity_registry
result = reset_capacity_registry()
```

```python
# Using create
result = create(cls, route_name)
```



---
**Generated**: 2026-03-26T09:39:02.580963
**Type**: api_reference
**Quality**: comprehensive
