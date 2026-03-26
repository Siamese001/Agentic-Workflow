# API Documentation: recursive_orchestration_types

**Target Audience**: developers, api_users

# recursive_orchestration_types API Documentation

**File**: `recursive_orchestration_types.py`
**Classes**: 3
**Functions**: 16

## Classes

- **SuccessorSpec**
- **RecursionMetrics**
- **RecursiveOrchestrator**

## Functions

- **__init__**
- **spawn_successor** -> AgentResult
- **_validate_successor_acyclicity** -> bool
- **_would_create_cycle** -> bool
- **_cache_validation_result** -> None
- **_create_successor_context** -> ExecutionContext
- **_deep_merge_context** -> dict[str, Any]
- **get_metrics** -> dict[str, Any]
- **reset_metrics** -> None
- **clear_cache** -> None
- **clear_successor_graph** -> None
- **is_acyclic** -> bool
- **get_successor_chain** -> list[str]
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **has_cycle** -> bool


## Class: SuccessorSpec

**Description**: Specification for successor agent spawning.



## Class: RecursionMetrics

**Description**: Metrics for tracking recursion performance.



## Class: RecursiveOrchestrator

**Description**: 
    Forward-Rolling Recursion Orchestrator.

    Implements successor-based recursion pattern that maintains:
    - Acyclicity through successor chain validation
    - DNA integrity through zero-loss context merging
    - Infinite-horizon reasoning within depth limits

    SSOT COMPLIANCE: Uses validated successor chains, no arbitrary recursion.
    DNA PRESERVATION: accumulated_context survives all successor spawns.
    

### Methods

#### __init__
**Parameters**: self, max_depth, enable_validation_cache, cache_size
**Description**: 
        Initialize recursive orchestrator.

        Args:
            max_depth: Maximum recursion depth (default: 50)
            enable_validation_cache: Enable acyclicity validation caching
            cache_size: Maximum cache entries for validation results
        

#### spawn_successor
**Parameters**: self, current_agent, successor_spec, context
**Returns**: AgentResult
**Description**: 
        Spawn successor agent using Forward-Rolling pattern.

        [ACYCLICITY GUARD] Validates successor maintains DAG properties
        [DNA PRESERVATION] Ensures context continuity across spawns

        Args:
            current_agent: Name of the current (predecessor) agent
            successor_spec: Specification for the successor to spawn
            context: Current execution context

        Returns:
            AgentResult from successor execution
        

#### _validate_successor_acyclicity
**Parameters**: self, predecessor, successor
**Returns**: bool
**Description**: 
        Validate that adding successor maintains acyclicity.

        Uses path-based cycle detection for O(n) validation.
        Implements validation caching for performance optimization.

        Args:
            predecessor: Current agent name
            successor: Proposed successor agent name

        Returns:
            True if adding successor maintains acyclicity
        

#### _would_create_cycle
**Parameters**: self, start, target, visited
**Returns**: bool
**Description**: 
        Check if there's a path from start to target in current graph.

        Args:
            start: Starting node
            target: Target node we're looking for
            visited: Set of visited nodes

        Returns:
            True if path exists (would create cycle)
        

#### _cache_validation_result
**Parameters**: self, cache_key, result
**Returns**: None
**Description**: Cache validation result with size management.

#### _create_successor_context
**Parameters**: self, predecessor, successor_spec, context
**Returns**: ExecutionContext
**Description**: 
        Create successor context with zero-loss DNA preservation.

        Implements deep context merging strategy ensuring no data loss
        across successor spawns while maintaining metadata integrity.

        Args:
            predecessor: Name of predecessor agent
            successor_spec: Specification for successor
            context: Current execution context

        Returns:
            New ExecutionContext for successor execution
        

#### _deep_merge_context
**Parameters**: self, base, override
**Returns**: dict[str, Any]
**Description**: 
        Deep merge two context dictionaries.

        Preserves nested structures and critical DNA keys.

        Args:
            base: Base context dictionary
            override: Override values

        Returns:
            Merged context dictionary
        

#### get_metrics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current recursion metrics.

#### reset_metrics
**Parameters**: self
**Returns**: None
**Description**: Reset recursion metrics.

#### clear_cache
**Parameters**: self
**Returns**: None
**Description**: Clear validation cache.

#### clear_successor_graph
**Parameters**: self
**Returns**: None
**Description**: Clear successor edge tracking.

#### is_acyclic
**Parameters**: self
**Returns**: bool
**Description**: 
        Check if current successor graph is acyclic.

        Returns:
            True if graph has no cycles
        

#### get_successor_chain
**Parameters**: self, start_agent
**Returns**: list[str]
**Description**: 
        Get the successor chain starting from an agent.

        Args:
            start_agent: Starting agent name

        Returns:
            List of agents in successor order
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Heal recursive orchestration infrastructure.

        Validates successor graph acyclicity and repairs DNA integrity violations.

        Args:
            dry_run: If True, only report issues
            execute: If True, apply fixes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of agents already in call path

        Returns:
            Dict with healing metrics
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RecursiveOrchestrator.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing results
        



## Function: __init__

**Parameters**: self, max_depth, enable_validation_cache, cache_size
**Description**: 
        Initialize recursive orchestrator.

        Args:
            max_depth: Maximum recursion depth (default: 50)
            enable_validation_cache: Enable acyclicity validation caching
            cache_size: Maximum cache entries for validation results
        



## Function: spawn_successor

**Parameters**: self, current_agent, successor_spec, context
**Returns**: AgentResult
**Description**: 
        Spawn successor agent using Forward-Rolling pattern.

        [ACYCLICITY GUARD] Validates successor maintains DAG properties
        [DNA PRESERVATION] Ensures context continuity across spawns

        Args:
            current_agent: Name of the current (predecessor) agent
            successor_spec: Specification for the successor to spawn
            context: Current execution context

        Returns:
            AgentResult from successor execution
        



## Function: _validate_successor_acyclicity

**Parameters**: self, predecessor, successor
**Returns**: bool
**Description**: 
        Validate that adding successor maintains acyclicity.

        Uses path-based cycle detection for O(n) validation.
        Implements validation caching for performance optimization.

        Args:
            predecessor: Current agent name
            successor: Proposed successor agent name

        Returns:
            True if adding successor maintains acyclicity
        



## Function: _would_create_cycle

**Parameters**: self, start, target, visited
**Returns**: bool
**Description**: 
        Check if there's a path from start to target in current graph.

        Args:
            start: Starting node
            target: Target node we're looking for
            visited: Set of visited nodes

        Returns:
            True if path exists (would create cycle)
        



## Function: _cache_validation_result

**Parameters**: self, cache_key, result
**Returns**: None
**Description**: Cache validation result with size management.



## Function: _create_successor_context

**Parameters**: self, predecessor, successor_spec, context
**Returns**: ExecutionContext
**Description**: 
        Create successor context with zero-loss DNA preservation.

        Implements deep context merging strategy ensuring no data loss
        across successor spawns while maintaining metadata integrity.

        Args:
            predecessor: Name of predecessor agent
            successor_spec: Specification for successor
            context: Current execution context

        Returns:
            New ExecutionContext for successor execution
        



## Function: _deep_merge_context

**Parameters**: self, base, override
**Returns**: dict[str, Any]
**Description**: 
        Deep merge two context dictionaries.

        Preserves nested structures and critical DNA keys.

        Args:
            base: Base context dictionary
            override: Override values

        Returns:
            Merged context dictionary
        



## Function: get_metrics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current recursion metrics.



## Function: reset_metrics

**Parameters**: self
**Returns**: None
**Description**: Reset recursion metrics.



## Function: clear_cache

**Parameters**: self
**Returns**: None
**Description**: Clear validation cache.



## Function: clear_successor_graph

**Parameters**: self
**Returns**: None
**Description**: Clear successor edge tracking.



## Function: is_acyclic

**Parameters**: self
**Returns**: bool
**Description**: 
        Check if current successor graph is acyclic.

        Returns:
            True if graph has no cycles
        



## Function: get_successor_chain

**Parameters**: self, start_agent
**Returns**: list[str]
**Description**: 
        Get the successor chain starting from an agent.

        Args:
            start_agent: Starting agent name

        Returns:
            List of agents in successor order
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Heal recursive orchestration infrastructure.

        Validates successor graph acyclicity and repairs DNA integrity violations.

        Args:
            dry_run: If True, only report issues
            execute: If True, apply fixes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of agents already in call path

        Returns:
            Dict with healing metrics
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RecursiveOrchestrator.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing results
        



## Function: has_cycle

**Parameters**: node
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using SuccessorSpec
successorspec = SuccessorSpec()
```

```python
# Using RecursionMetrics
recursionmetrics = RecursionMetrics()
```

```python
# Using RecursiveOrchestrator
recursiveorchestrator = RecursiveOrchestrator()
recursiveorchestrator.spawn_successor()
recursiveorchestrator.get_metrics()
```

### Function Usage

```python
# Using __init__
result = __init__(max_depth, enable_validation_cache)
```

```python
# Using spawn_successor
result = spawn_successor(current_agent, successor_spec)
```

```python
# Using _validate_successor_acyclicity
result = _validate_successor_acyclicity(predecessor, successor)
```



---
**Generated**: 2026-03-26T09:39:04.407288
**Type**: api_reference
**Quality**: comprehensive
