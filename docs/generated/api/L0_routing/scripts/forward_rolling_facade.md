# API Documentation: forward_rolling_facade

**Target Audience**: developers, api_users

# forward_rolling_facade API Documentation

**File**: `forward_rolling_facade.py`
**Classes**: 3
**Functions**: 20

## Classes

- **ForwardRollingResult**
- **OptimizationMetrics**
- **ForwardRollingFacade**

## Functions

- **to_dict** -> dict[str, Any]
- **__init__**
- **execute** -> ForwardRollingResult
- **_execute_forward_rolling** -> ForwardRollingResult
- **_execute_static_dag** -> ForwardRollingResult
- **_update_metrics** -> None
- **_cache_result** -> None
- **spawn_successor** -> AgentResult
- **set_rollout_stage** -> None
- **emergency_disable** -> None
- **rollback** -> bool
- **get_health_status** -> HealthStatus
- **get_metrics** -> dict[str, Any]
- **clear_cache** -> int
- **set_cache_enabled** -> None
- **reset** -> None
- **is_forward_rolling_enabled** -> bool
- **get_rollout_percentage** -> int
- **set_feature_flag** -> None
- **is_feature_enabled** -> bool


## Class: ForwardRollingResult

**Description**: Result from Forward-Rolling execution.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: OptimizationMetrics

**Description**: Metrics for optimization tracking.



## Class: ForwardRollingFacade

**Description**: 
    Unified facade for Forward-Rolling Recursion system.

    Integrates:
    - RecursiveOrchestrator: Core recursion logic
    - ContextPruningStrategy: Memory management
    - AdaptiveDepthManager: Dynamic depth control
    - RecursionMonitor: Production monitoring
    - ForwardRollingConfig: Feature flags and rollout

    Usage:
        facade = ForwardRollingFacade()
        result = facade.execute("agent_name", context)
    

### Methods

#### __init__
**Parameters**: self, initial_stage, max_depth, enable_pruning, enable_adaptive_depth, enable_monitoring
**Description**: 
        Initialize Forward-Rolling Facade.

        Args:
            initial_stage: Initial rollout stage
            max_depth: Maximum recursion depth
            enable_pruning: Enable context pruning
            enable_adaptive_depth: Enable adaptive depth management
            enable_monitoring: Enable production monitoring
        

#### execute
**Parameters**: self, agent_name, context, mission_id, use_cache
**Returns**: ForwardRollingResult
**Description**: 
        Execute an agent using optimal execution mode.

        Automatically selects between Forward-Rolling and Static DAG
        based on configuration and rollout settings.

        Args:
            agent_name: Name of agent to execute
            context: Optional execution context
            mission_id: Optional mission identifier
            use_cache: Whether to use result caching

        Returns:
            ForwardRollingResult with execution details
        

#### _execute_forward_rolling
**Parameters**: self, agent_name, context
**Returns**: ForwardRollingResult
**Description**: Execute using Forward-Rolling Recursion.

#### _execute_static_dag
**Parameters**: self, agent_name, context
**Returns**: ForwardRollingResult
**Description**: Execute using Static DAG (fallback mode).

#### _update_metrics
**Parameters**: self, result, duration_ms
**Returns**: None
**Description**: Update optimization metrics.

#### _cache_result
**Parameters**: self, key, result
**Returns**: None
**Description**: Cache a result with size management.

#### spawn_successor
**Parameters**: self, current_agent, successor_name, context
**Returns**: AgentResult
**Description**: 
        Spawn a successor agent.

        Convenience method for direct successor spawning.

        Args:
            current_agent: Current agent name
            successor_name: Successor agent to spawn
            context: Current execution context

        Returns:
            AgentResult from successor execution
        

#### set_rollout_stage
**Parameters**: self, stage
**Returns**: None
**Description**: Set rollout stage.

#### emergency_disable
**Parameters**: self
**Returns**: None
**Description**: Emergency disable Forward-Rolling.

#### rollback
**Parameters**: self
**Returns**: bool
**Description**: Rollback to previous configuration.

#### get_health_status
**Parameters**: self
**Returns**: HealthStatus
**Description**: Get current health status.

#### get_metrics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get comprehensive metrics from all components.

#### clear_cache
**Parameters**: self
**Returns**: int
**Description**: Clear result cache.

#### set_cache_enabled
**Parameters**: self, enabled
**Returns**: None
**Description**: Enable or disable caching.

#### reset
**Parameters**: self
**Returns**: None
**Description**: Reset all components to initial state.

#### is_forward_rolling_enabled
**Parameters**: self
**Returns**: bool
**Description**: Check if Forward-Rolling is currently enabled.

#### get_rollout_percentage
**Parameters**: self
**Returns**: int
**Description**: Get current rollout percentage.

#### set_feature_flag
**Parameters**: self, name, enabled, percentage
**Returns**: None
**Description**: Set a feature flag.

#### is_feature_enabled
**Parameters**: self, name, agent_id
**Returns**: bool
**Description**: Check if a feature is enabled.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: __init__

**Parameters**: self, initial_stage, max_depth, enable_pruning, enable_adaptive_depth, enable_monitoring
**Description**: 
        Initialize Forward-Rolling Facade.

        Args:
            initial_stage: Initial rollout stage
            max_depth: Maximum recursion depth
            enable_pruning: Enable context pruning
            enable_adaptive_depth: Enable adaptive depth management
            enable_monitoring: Enable production monitoring
        



## Function: execute

**Parameters**: self, agent_name, context, mission_id, use_cache
**Returns**: ForwardRollingResult
**Description**: 
        Execute an agent using optimal execution mode.

        Automatically selects between Forward-Rolling and Static DAG
        based on configuration and rollout settings.

        Args:
            agent_name: Name of agent to execute
            context: Optional execution context
            mission_id: Optional mission identifier
            use_cache: Whether to use result caching

        Returns:
            ForwardRollingResult with execution details
        



## Function: _execute_forward_rolling

**Parameters**: self, agent_name, context
**Returns**: ForwardRollingResult
**Description**: Execute using Forward-Rolling Recursion.



## Function: _execute_static_dag

**Parameters**: self, agent_name, context
**Returns**: ForwardRollingResult
**Description**: Execute using Static DAG (fallback mode).



## Function: _update_metrics

**Parameters**: self, result, duration_ms
**Returns**: None
**Description**: Update optimization metrics.



## Function: _cache_result

**Parameters**: self, key, result
**Returns**: None
**Description**: Cache a result with size management.



## Function: spawn_successor

**Parameters**: self, current_agent, successor_name, context
**Returns**: AgentResult
**Description**: 
        Spawn a successor agent.

        Convenience method for direct successor spawning.

        Args:
            current_agent: Current agent name
            successor_name: Successor agent to spawn
            context: Current execution context

        Returns:
            AgentResult from successor execution
        



## Function: set_rollout_stage

**Parameters**: self, stage
**Returns**: None
**Description**: Set rollout stage.



## Function: emergency_disable

**Parameters**: self
**Returns**: None
**Description**: Emergency disable Forward-Rolling.



## Function: rollback

**Parameters**: self
**Returns**: bool
**Description**: Rollback to previous configuration.



## Function: get_health_status

**Parameters**: self
**Returns**: HealthStatus
**Description**: Get current health status.



## Function: get_metrics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get comprehensive metrics from all components.



## Function: clear_cache

**Parameters**: self
**Returns**: int
**Description**: Clear result cache.



## Function: set_cache_enabled

**Parameters**: self, enabled
**Returns**: None
**Description**: Enable or disable caching.



## Function: reset

**Parameters**: self
**Returns**: None
**Description**: Reset all components to initial state.



## Function: is_forward_rolling_enabled

**Parameters**: self
**Returns**: bool
**Description**: Check if Forward-Rolling is currently enabled.



## Function: get_rollout_percentage

**Parameters**: self
**Returns**: int
**Description**: Get current rollout percentage.



## Function: set_feature_flag

**Parameters**: self, name, enabled, percentage
**Returns**: None
**Description**: Set a feature flag.



## Function: is_feature_enabled

**Parameters**: self, name, agent_id
**Returns**: bool
**Description**: Check if a feature is enabled.



## Usage Examples

### Class Usage

```python
# Using ForwardRollingResult
forwardrollingresult = ForwardRollingResult()
forwardrollingresult.to_dict()
```

```python
# Using OptimizationMetrics
optimizationmetrics = OptimizationMetrics()
```

```python
# Using ForwardRollingFacade
forwardrollingfacade = ForwardRollingFacade()
forwardrollingfacade.execute()
forwardrollingfacade.spawn_successor()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using __init__
result = __init__(initial_stage, max_depth)
```

```python
# Using execute
result = execute(agent_name, context)
```



---
**Generated**: 2026-03-26T09:39:03.145850
**Type**: api_reference
**Quality**: comprehensive
