# API Documentation: adaptation_orchestrator

**Target Audience**: developers, api_users

# adaptation_orchestrator API Documentation

**File**: `adaptation_orchestrator.py`
**Classes**: 3
**Functions**: 18

## Classes

- **ExecutionContext**
- **ExecutionStrategy**
- **HistoricalMetrics**

## Functions

- **choose_execution_strategy** -> ExecutionStrategy
- **_analyze_candidate_strategies** -> list[ExecutionStrategy]
- **_evaluate_historical_metrics** -> list[tuple[ExecutionStrategy, float]]
- **_rank_strategies_by_criteria** -> list[ExecutionStrategy]
- **_apply_governance_guard** -> list[ExecutionStrategy]
- **_check_policy_compliance** -> bool
- **_record_adaptation_decision** -> None
- **query_execution_adaptations** -> list[ExecutionAdaptationRecord]
- **evaluate_strategy_safety** -> dict[str, Any]
- **check_policy_compliance** -> bool
- **choose_simple_execution_strategy** -> ExecutionStrategy
- **execution_strategy_chosen** -> None
- **strategy_evaluated** -> None
- **unsafe_strategy_rejected** -> None
- **policy_compliance_checked** -> None
- **create** -> ExecutionContext
- **create** -> ExecutionStrategy
- **create** -> HistoricalMetrics


## Class: ExecutionContext

**Description**: Context for execution data.

### Methods

#### create
**Parameters**: cls, run_id, trace_id, execution_type, available_tools, constraints, policy_requirements, timestamp
**Returns**: ExecutionContext



## Class: ExecutionStrategy

**Description**: Context for execution strategy data.

### Methods

#### create
**Parameters**: cls, strategy_id, strategy_name, tool_sequence, estimated_latency, estimated_cost, safety_score, reliability_score, strategy_metadata
**Returns**: ExecutionStrategy



## Class: HistoricalMetrics

**Description**: Context for historical performance metrics.

### Methods

#### create
**Parameters**: cls, success_rate, failure_rate, average_latency, average_cost, safety_incidents, total_executions, last_execution_time
**Returns**: HistoricalMetrics



## Function: choose_execution_strategy

**Parameters**: execution_context, candidate_strategies, historical_metrics
**Returns**: ExecutionStrategy
**Description**: Mandatory entrypoint for adaptive execution strategy selection — P4/L2 spec.

    Steps (in order, all mandatory):
      1. analyze candidate strategies
      2. evaluate historical metrics
      3. rank by reliability, latency, cost, safety
      4. apply governance guard
      5. record adaptation decision
      6. return chosen strategy

    Args:
        execution_context: Execution context for strategy selection
        candidate_strategies: List of candidate execution strategies
        historical_metrics: Historical performance metrics
        registry: ExecutionAdaptationRegistry to use (uses global if None)

    Returns:
        ExecutionStrategy — the chosen execution strategy

    Raises:
        ExecutionAdaptationError: If strategy selection fails (Gate A/D)
    



## Function: _analyze_candidate_strategies

**Parameters**: strategies, execution_context
**Returns**: list[ExecutionStrategy]
**Description**: Analyze candidate strategies for compatibility.



## Function: _evaluate_historical_metrics

**Parameters**: strategies, historical_metrics
**Returns**: list[tuple[ExecutionStrategy, float]]
**Description**: Evaluate strategies against historical metrics.



## Function: _rank_strategies_by_criteria

**Parameters**: evaluated_strategies
**Returns**: list[ExecutionStrategy]
**Description**: Rank strategies by evaluation criteria.



## Function: _apply_governance_guard

**Parameters**: strategies, execution_context
**Returns**: list[ExecutionStrategy]
**Description**: Apply governance guard to ensure safety and policy compliance.



## Function: _check_policy_compliance

**Parameters**: strategy, execution_context
**Returns**: bool
**Description**: Check if strategy complies with policies.



## Function: _record_adaptation_decision

**Parameters**: strategy, execution_context, historical_metrics, registry
**Returns**: None
**Description**: Record the adaptation decision.



## Function: query_execution_adaptations

**Parameters**: run_id, trace_id, strategy_hash, min_success_rate
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations with optional filters.



## Function: evaluate_strategy_safety

**Parameters**: strategy
**Returns**: dict[str, Any]
**Description**: Evaluate strategy safety.



## Function: check_policy_compliance

**Parameters**: strategy, execution_context
**Returns**: bool
**Description**: Check policy compliance for a strategy.



## Function: choose_simple_execution_strategy

**Parameters**: run_id, trace_id, strategy_name, tool_sequence
**Returns**: ExecutionStrategy
**Description**: Convenience wrapper for simple execution strategy selection.



## Function: execution_strategy_chosen

**Parameters**: strategy_id, run_id, trace_id
**Returns**: None
**Description**: ADG edge: execution_strategy_chosen



## Function: strategy_evaluated

**Parameters**: strategy_id, score
**Returns**: None
**Description**: ADG edge: strategy_evaluated



## Function: unsafe_strategy_rejected

**Parameters**: strategy_id, reason
**Returns**: None
**Description**: ADG edge: unsafe_strategy_rejected



## Function: policy_compliance_checked

**Parameters**: strategy_id, compliant
**Returns**: None
**Description**: ADG edge: policy_compliance_checked



## Function: create

**Parameters**: cls, run_id, trace_id, execution_type, available_tools, constraints, policy_requirements, timestamp
**Returns**: ExecutionContext


## Function: create

**Parameters**: cls, strategy_id, strategy_name, tool_sequence, estimated_latency, estimated_cost, safety_score, reliability_score, strategy_metadata
**Returns**: ExecutionStrategy


## Function: create

**Parameters**: cls, success_rate, failure_rate, average_latency, average_cost, safety_incidents, total_executions, last_execution_time
**Returns**: HistoricalMetrics


## Usage Examples

### Class Usage

```python
# Using ExecutionContext
executioncontext = ExecutionContext()
executioncontext.create()
```

```python
# Using ExecutionStrategy
executionstrategy = ExecutionStrategy()
executionstrategy.create()
```

```python
# Using HistoricalMetrics
historicalmetrics = HistoricalMetrics()
historicalmetrics.create()
```

### Function Usage

```python
# Using choose_execution_strategy
result = choose_execution_strategy(execution_context, candidate_strategies)
```

```python
# Using _analyze_candidate_strategies
result = _analyze_candidate_strategies(strategies, execution_context)
```

```python
# Using _evaluate_historical_metrics
result = _evaluate_historical_metrics(strategies, historical_metrics)
```



---
**Generated**: 2026-03-26T09:39:03.598915
**Type**: api_reference
**Quality**: comprehensive
