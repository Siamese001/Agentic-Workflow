# API Documentation: routing_optimization

**Target Audience**: developers, api_users

# routing_optimization API Documentation

**File**: `routing_optimization.py`
**Classes**: 3
**Functions**: 22

## Classes

- **RoutingOptimizationError** (inherits from Exception)
- **RoutingOptimizationRecord**
- **RoutingOptimizationRegistry**

## Functions

- **get_routing_optimization_registry** -> RoutingOptimizationRegistry
- **reset_routing_optimization_registry** -> None
- **create** -> RoutingOptimizationRecord
- **has_historical_data_window** -> bool
- **has_versioned_policy_mutation** -> bool
- **has_registry_routes** -> bool
- **has_reasoning_metadata** -> bool
- **has_governance_approval** -> bool
- **__init__** -> None
- **get_instance** -> RoutingOptimizationRegistry
- **persist_optimization** -> None
- **query_optimization_by_id** -> RoutingOptimizationRecord | None
- **query_optimizations_by_time_window** -> list[RoutingOptimizationRecord]
- **query_optimizations_by_route_hash** -> list[RoutingOptimizationRecord]
- **query_optimizations_by_rank** -> list[RoutingOptimizationRecord]
- **get_latest_optimization** -> RoutingOptimizationRecord | None
- **get_optimization_count** -> int
- **verify_historical_data_window** -> bool
- **verify_versioned_policy_mutation** -> bool
- **verify_registry_routes** -> bool
- **verify_reasoning_metadata** -> bool
- **verify_governance_approval** -> bool


## Class: RoutingOptimizationError

**Description**: Raised when routing optimization fails (Gate A/E).

**Inherits from**: Exception



## Class: RoutingOptimizationRecord

**Description**: Immutable routing optimization record for adaptive routing (11 required fields).

### Methods

#### create
**Parameters**: cls, routing_optimization_id, optimization_window_start, optimization_window_end, route_candidate_hash, historical_success_rate, historical_failure_rate, median_latency_ms, p95_latency_ms, cost_estimate, recommended_route_rank, optimization_reason_hash
**Returns**: RoutingOptimizationRecord
**Description**: Factory to create RoutingOptimizationRecord with default values.

#### has_historical_data_window
**Parameters**: self
**Returns**: bool
**Description**: Check if optimization has historical data window (Gate A).

#### has_versioned_policy_mutation
**Parameters**: self
**Returns**: bool
**Description**: Check if optimization supports versioned policy mutation (Gate B).

#### has_registry_routes
**Parameters**: self
**Returns**: bool
**Description**: Check if optimization recommends routes from registry (Gate C).

#### has_reasoning_metadata
**Parameters**: self
**Returns**: bool
**Description**: Check if optimization has reasoning metadata (Gate D).

#### has_governance_approval
**Parameters**: self
**Returns**: bool
**Description**: Check if optimization bypasses governance approval (Gate E).



## Class: RoutingOptimizationRegistry

**Description**: Thread-safe registry for routing optimization records.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: RoutingOptimizationRegistry
**Description**: Singleton accessor.

#### persist_optimization
**Parameters**: self, optimization
**Returns**: None
**Description**: Persist a routing optimization record.

#### query_optimization_by_id
**Parameters**: self, optimization_id
**Returns**: RoutingOptimizationRecord | None
**Description**: Query routing optimization by ID.

#### query_optimizations_by_time_window
**Parameters**: self, start_tick, end_tick
**Returns**: list[RoutingOptimizationRecord]
**Description**: Query routing optimizations by time window.

#### query_optimizations_by_route_hash
**Parameters**: self, route_hash
**Returns**: list[RoutingOptimizationRecord]
**Description**: Query routing optimizations by route hash.

#### query_optimizations_by_rank
**Parameters**: self, rank
**Returns**: list[RoutingOptimizationRecord]
**Description**: Query routing optimizations by rank.

#### get_latest_optimization
**Parameters**: self
**Returns**: RoutingOptimizationRecord | None
**Description**: Get the latest routing optimization.

#### get_optimization_count
**Parameters**: self
**Returns**: int
**Description**: Get count of routing optimizations.

#### verify_historical_data_window
**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization has historical data window (Gate A).

#### verify_versioned_policy_mutation
**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization supports versioned policy mutation (Gate B).

#### verify_registry_routes
**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization recommends routes from registry (Gate C).

#### verify_reasoning_metadata
**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization has reasoning metadata (Gate D).

#### verify_governance_approval
**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization has governance approval (Gate E).



## Function: get_routing_optimization_registry

**Returns**: RoutingOptimizationRegistry
**Description**: Get the singleton RoutingOptimizationRegistry instance.



## Function: reset_routing_optimization_registry

**Returns**: None
**Description**: Reset the singleton RoutingOptimizationRegistry (for testing).



## Function: create

**Parameters**: cls, routing_optimization_id, optimization_window_start, optimization_window_end, route_candidate_hash, historical_success_rate, historical_failure_rate, median_latency_ms, p95_latency_ms, cost_estimate, recommended_route_rank, optimization_reason_hash
**Returns**: RoutingOptimizationRecord
**Description**: Factory to create RoutingOptimizationRecord with default values.



## Function: has_historical_data_window

**Parameters**: self
**Returns**: bool
**Description**: Check if optimization has historical data window (Gate A).



## Function: has_versioned_policy_mutation

**Parameters**: self
**Returns**: bool
**Description**: Check if optimization supports versioned policy mutation (Gate B).



## Function: has_registry_routes

**Parameters**: self
**Returns**: bool
**Description**: Check if optimization recommends routes from registry (Gate C).



## Function: has_reasoning_metadata

**Parameters**: self
**Returns**: bool
**Description**: Check if optimization has reasoning metadata (Gate D).



## Function: has_governance_approval

**Parameters**: self
**Returns**: bool
**Description**: Check if optimization bypasses governance approval (Gate E).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: RoutingOptimizationRegistry
**Description**: Singleton accessor.



## Function: persist_optimization

**Parameters**: self, optimization
**Returns**: None
**Description**: Persist a routing optimization record.



## Function: query_optimization_by_id

**Parameters**: self, optimization_id
**Returns**: RoutingOptimizationRecord | None
**Description**: Query routing optimization by ID.



## Function: query_optimizations_by_time_window

**Parameters**: self, start_tick, end_tick
**Returns**: list[RoutingOptimizationRecord]
**Description**: Query routing optimizations by time window.



## Function: query_optimizations_by_route_hash

**Parameters**: self, route_hash
**Returns**: list[RoutingOptimizationRecord]
**Description**: Query routing optimizations by route hash.



## Function: query_optimizations_by_rank

**Parameters**: self, rank
**Returns**: list[RoutingOptimizationRecord]
**Description**: Query routing optimizations by rank.



## Function: get_latest_optimization

**Parameters**: self
**Returns**: RoutingOptimizationRecord | None
**Description**: Get the latest routing optimization.



## Function: get_optimization_count

**Parameters**: self
**Returns**: int
**Description**: Get count of routing optimizations.



## Function: verify_historical_data_window

**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization has historical data window (Gate A).



## Function: verify_versioned_policy_mutation

**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization supports versioned policy mutation (Gate B).



## Function: verify_registry_routes

**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization recommends routes from registry (Gate C).



## Function: verify_reasoning_metadata

**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization has reasoning metadata (Gate D).



## Function: verify_governance_approval

**Parameters**: self, optimization_id
**Returns**: bool
**Description**: Verify optimization has governance approval (Gate E).



## Usage Examples

### Class Usage

```python
# Using RoutingOptimizationError
routingoptimizationerror = RoutingOptimizationError()
```

```python
# Using RoutingOptimizationRecord
routingoptimizationrecord = RoutingOptimizationRecord()
routingoptimizationrecord.create()
routingoptimizationrecord.has_historical_data_window()
```

```python
# Using RoutingOptimizationRegistry
routingoptimizationregistry = RoutingOptimizationRegistry()
routingoptimizationregistry.get_instance()
routingoptimizationregistry.persist_optimization()
```

### Function Usage

```python
# Using get_routing_optimization_registry
result = get_routing_optimization_registry()
```

```python
# Using reset_routing_optimization_registry
result = reset_routing_optimization_registry()
```

```python
# Using create
result = create(cls, routing_optimization_id)
```



---
**Generated**: 2026-03-26T09:39:02.701748
**Type**: api_reference
**Quality**: comprehensive
