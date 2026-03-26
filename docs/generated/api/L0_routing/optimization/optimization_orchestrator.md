# API Documentation: optimization_orchestrator

**Target Audience**: developers, api_users

# optimization_orchestrator API Documentation

**File**: `optimization_orchestrator.py`
**Classes**: 3
**Functions**: 26

## Classes

- **RoutingHistory**
- **OptimizationWindow**
- **PolicyContext**

## Functions

- **optimize_routing_policy** -> RoutingOptimizationRecord
- **_analyze_historical_routing_outcomes** -> dict[str, Any]
- **_compute_success_failure_rates** -> dict[str, float]
- **_evaluate_latency_and_cost** -> dict[str, float]
- **_rank_candidate_routes** -> dict[str, Any]
- **_produce_policy_recommendations** -> dict[str, Any]
- **_persist_optimization_record** -> RoutingOptimizationRecord
- **query_routing_optimizations** -> list[RoutingOptimizationRecord]
- **get_optimization_recommendations** -> dict[str, Any]
- **apply_optimization_with_governance** -> dict[str, Any]
- **optimize_simple_routing** -> RoutingOptimizationRecord
- **optimizes_routing** -> None
- **historical_outcomes_analyzed** -> None
- **routing_policy_adapted** -> None
- **routing_optimization_persisted** -> None
- **route_candidate_ranked** -> None
- **routing_governance_approved** -> None
- **create** -> RoutingHistory
- **create** -> OptimizationWindow
- **create** -> PolicyContext
- **optimizes_routing** -> None
- **historical_outcomes_analyzed** -> None
- **routing_policy_adapted** -> None
- **routing_optimization_persisted** -> None
- **route_candidate_ranked** -> None
- **routing_governance_approved** -> None


## Class: RoutingHistory

**Description**: Context for routing history data.

### Methods

#### create
**Parameters**: cls, routing_events, execution_traces, failure_classifications, queue_depth_history, window_start_tick, window_end_tick
**Returns**: RoutingHistory



## Class: OptimizationWindow

**Description**: Context for optimization window.

### Methods

#### create
**Parameters**: cls, window_start_tick, window_end_tick, min_sample_size
**Returns**: OptimizationWindow



## Class: PolicyContext

**Description**: Context for routing policy adaptation.

### Methods

#### create
**Parameters**: cls, current_policy_version, policy_constraints, route_registry, governance_required, adaptation_allowed
**Returns**: PolicyContext



## Function: optimize_routing_policy

**Parameters**: routing_history, optimization_window, policy_context
**Returns**: RoutingOptimizationRecord
**Description**: Mandatory entrypoint for routing optimization policy adaptation — P4/L0 spec §3.

    Steps (in order, all mandatory):
      1. analyze historical routing outcomes
      2. compute success and failure rates
      3. evaluate latency and cost
      4. rank candidate routes
      5. produce policy recommendations
      6. persist optimization record

    Args:
        routing_history: Historical routing data for analysis
        optimization_window: Time window for optimization
        policy_context: Current policy context and constraints
        registry: RoutingOptimizationRegistry to use (uses global if None)

    Returns:
        RoutingOptimizationRecord — the created and persisted optimization record

    Raises:
        RoutingOptimizationError: If optimization fails (Gate A/E)
    



## Function: _analyze_historical_routing_outcomes

**Parameters**: routing_history, optimization_window
**Returns**: dict[str, Any]
**Description**: Analyze historical routing outcomes.



## Function: _compute_success_failure_rates

**Parameters**: historical_analysis
**Returns**: dict[str, float]
**Description**: Compute success and failure rates from historical analysis.



## Function: _evaluate_latency_and_cost

**Parameters**: historical_analysis
**Returns**: dict[str, float]
**Description**: Evaluate latency and cost from historical analysis.



## Function: _rank_candidate_routes

**Parameters**: success_failure_rates, latency_cost_analysis, policy_context
**Returns**: dict[str, Any]
**Description**: Rank candidate routes based on performance metrics.



## Function: _produce_policy_recommendations

**Parameters**: route_rankings, policy_context
**Returns**: dict[str, Any]
**Description**: Produce policy recommendations based on route rankings.



## Function: _persist_optimization_record

**Parameters**: optimization_window, route_rankings, policy_recommendations, registry
**Returns**: RoutingOptimizationRecord
**Description**: Persist optimization record to registry.



## Function: query_routing_optimizations

**Parameters**: start_tick, end_tick, route_hash, rank
**Returns**: list[RoutingOptimizationRecord]
**Description**: Query routing optimizations with optional filters.



## Function: get_optimization_recommendations

**Parameters**: optimization_id
**Returns**: dict[str, Any]
**Description**: Get optimization recommendations for operators.



## Function: apply_optimization_with_governance

**Parameters**: optimization_id, governance_approval
**Returns**: dict[str, Any]
**Description**: Apply optimization with governance approval.



## Function: optimize_simple_routing

**Parameters**: window_duration_seconds
**Returns**: RoutingOptimizationRecord
**Description**: Convenience wrapper for simple routing optimization.



## Function: optimizes_routing

**Parameters**: optimization_id, window_start, route_hash
**Returns**: None
**Description**: ADG edge emitter for optimizes_routing.



## Function: historical_outcomes_analyzed

**Parameters**: event_count, window_start
**Returns**: None
**Description**: ADG edge emitter for historical_outcomes_analyzed.



## Function: routing_policy_adapted

**Parameters**: old_version, new_version, optimization_id
**Returns**: None
**Description**: ADG edge emitter for routing_policy_adapted.



## Function: routing_optimization_persisted

**Parameters**: optimization_id, window_end
**Returns**: None
**Description**: ADG edge emitter for routing_optimization_persisted.



## Function: route_candidate_ranked

**Parameters**: route_hash, rank, optimization_id
**Returns**: None
**Description**: ADG edge emitter for route_candidate_ranked.



## Function: routing_governance_approved

**Parameters**: optimization_id, approved
**Returns**: None
**Description**: ADG edge emitter for routing_governance_approved.



## Function: create

**Parameters**: cls, routing_events, execution_traces, failure_classifications, queue_depth_history, window_start_tick, window_end_tick
**Returns**: RoutingHistory


## Function: create

**Parameters**: cls, window_start_tick, window_end_tick, min_sample_size
**Returns**: OptimizationWindow


## Function: create

**Parameters**: cls, current_policy_version, policy_constraints, route_registry, governance_required, adaptation_allowed
**Returns**: PolicyContext


## Function: optimizes_routing

**Parameters**: optimization_id, window_start, route_hash
**Returns**: None
**Description**: ADG edge emitter for optimizes_routing.



## Function: historical_outcomes_analyzed

**Parameters**: event_count, window_start
**Returns**: None
**Description**: ADG edge emitter for historical_outcomes_analyzed.



## Function: routing_policy_adapted

**Parameters**: old_version, new_version, optimization_id
**Returns**: None
**Description**: ADG edge emitter for routing_policy_adapted.



## Function: routing_optimization_persisted

**Parameters**: optimization_id, window_end
**Returns**: None
**Description**: ADG edge emitter for routing_optimization_persisted.



## Function: route_candidate_ranked

**Parameters**: route_hash, rank, optimization_id
**Returns**: None
**Description**: ADG edge emitter for route_candidate_ranked.



## Function: routing_governance_approved

**Parameters**: optimization_id, approved
**Returns**: None
**Description**: ADG edge emitter for routing_governance_approved.



## Usage Examples

### Class Usage

```python
# Using RoutingHistory
routinghistory = RoutingHistory()
routinghistory.create()
```

```python
# Using OptimizationWindow
optimizationwindow = OptimizationWindow()
optimizationwindow.create()
```

```python
# Using PolicyContext
policycontext = PolicyContext()
policycontext.create()
```

### Function Usage

```python
# Using optimize_routing_policy
result = optimize_routing_policy(routing_history, optimization_window)
```

```python
# Using _analyze_historical_routing_outcomes
result = _analyze_historical_routing_outcomes(routing_history, optimization_window)
```

```python
# Using _compute_success_failure_rates
result = _compute_success_failure_rates(historical_analysis)
```



---
**Generated**: 2026-03-26T09:39:02.697992
**Type**: api_reference
**Quality**: comprehensive
