# API Documentation: context_pruning_types

**Target Audience**: developers, api_users

# context_pruning_types API Documentation

**File**: `context_pruning_types.py`
**Classes**: 4
**Functions**: 19

## Classes

- **PruningMetrics**
- **PruningResult**
- **ContextPruningStrategy**
- **AdaptiveDepthManager**

## Functions

- **__init__**
- **should_prune** -> bool
- **prune_context** -> PruningResult
- **_identify_preserved_keys** -> set[str]
- **_score_keys_for_pruning** -> list[tuple]
- **_calculate_key_score** -> float
- **_estimate_context_size** -> int
- **_estimate_entry_size** -> int
- **record_access** -> None
- **set_priority** -> None
- **get_metrics** -> dict[str, Any]
- **reset_metrics** -> None
- **__init__**
- **calculate_adaptive_limit** -> int
- **_assess_complexity** -> float
- **should_extend_limit** -> bool
- **get_extension_amount** -> int
- **get_statistics** -> dict[str, Any]
- **reset_history** -> None


## Class: PruningMetrics

**Description**: Metrics for tracking context pruning operations.



## Class: PruningResult

**Description**: Result from a pruning operation.



## Class: ContextPruningStrategy

**Description**: 
    Selective context pruning to prevent memory leaks in Forward-Rolling recursion.

    Implements LRU and priority-based pruning while preserving critical DNA keys.

    Strategies:
    - LRU (Least Recently Used): Prunes oldest accessed entries
    - PRIORITY: Prunes lowest priority entries first
    - SIZE: Prunes largest entries first
    - HYBRID: Combines all strategies with weighted scoring
    

### Methods

#### __init__
**Parameters**: self, max_context_size, prune_ratio, min_entries_to_keep, critical_keys, strategy
**Description**: 
        Initialize context pruning strategy.

        Args:
            max_context_size: Maximum context size in bytes before pruning
            prune_ratio: Ratio of context to prune when triggered (0.0-1.0)
            min_entries_to_keep: Minimum entries to keep after pruning
            critical_keys: Set of keys that must never be pruned
            strategy: Pruning strategy ('lru', 'priority', 'size', 'hybrid')
        

#### should_prune
**Parameters**: self, context
**Returns**: bool
**Description**: 
        Check if context should be pruned based on size.

        Args:
            context: Context dictionary to check

        Returns:
            True if pruning should be triggered
        

#### prune_context
**Parameters**: self, context
**Returns**: PruningResult
**Description**: 
        Prune context using configured strategy.

        Args:
            context: Context dictionary to prune

        Returns:
            PruningResult with details of pruning operation
        

#### _identify_preserved_keys
**Parameters**: self, context
**Returns**: set[str]
**Description**: Identify keys that must be preserved (critical DNA).

#### _score_keys_for_pruning
**Parameters**: self, context, prunable_keys
**Returns**: list[tuple]
**Description**: 
        Score keys for pruning priority.

        Lower scores get pruned first.

        Args:
            context: Context dictionary
            prunable_keys: Keys that can be pruned

        Returns:
            List of (key, score) tuples sorted by score ascending
        

#### _calculate_key_score
**Parameters**: self, key, value
**Returns**: float
**Description**: 
        Calculate pruning score for a key.

        Higher scores = more important = pruned later.

        Args:
            key: Key name
            value: Key value

        Returns:
            Score (0-100)
        

#### _estimate_context_size
**Parameters**: self, context
**Returns**: int
**Description**: Estimate context size in bytes.

#### _estimate_entry_size
**Parameters**: self, value
**Returns**: int
**Description**: Estimate size of a single entry in bytes.

#### record_access
**Parameters**: self, key
**Returns**: None
**Description**: Record access timestamp for LRU tracking.

#### set_priority
**Parameters**: self, key, priority
**Returns**: None
**Description**: Set priority score for a key (0-100, higher = more important).

#### get_metrics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get pruning metrics.

#### reset_metrics
**Parameters**: self
**Returns**: None
**Description**: Reset pruning metrics.



## Class: AdaptiveDepthManager

**Description**: 
    Adaptive depth management based on mission complexity.

    Replaces static 50-step limit with intelligent depth control
    that adapts to mission requirements and available resources.
    

### Methods

#### __init__
**Parameters**: self, base_limit, max_limit, min_limit, enable_adaptive
**Description**: 
        Initialize adaptive depth manager.

        Args:
            base_limit: Default depth limit
            max_limit: Maximum allowable depth
            min_limit: Minimum allowable depth
            enable_adaptive: Enable adaptive depth calculation
        

#### calculate_adaptive_limit
**Parameters**: self, context, current_metrics
**Returns**: int
**Description**: 
        Calculate adaptive depth limit based on mission complexity.

        Args:
            context: Current execution context
            current_metrics: Optional metrics from current execution

        Returns:
            Calculated depth limit
        

#### _assess_complexity
**Parameters**: self, context, metrics
**Returns**: float
**Description**: 
        Assess mission complexity from 0.0 to 1.0.

        Args:
            context: Execution context
            metrics: Optional current metrics

        Returns:
            Complexity score (0.0 = simple, 1.0 = highly complex)
        

#### should_extend_limit
**Parameters**: self, current_depth, current_limit, success_rate
**Returns**: bool
**Description**: 
        Determine if depth limit should be extended mid-mission.

        Args:
            current_depth: Current recursion depth
            current_limit: Current depth limit
            success_rate: Success rate of operations (0.0-1.0)

        Returns:
            True if limit should be extended
        

#### get_extension_amount
**Parameters**: self, current_limit, success_rate
**Returns**: int
**Description**: 
        Calculate how much to extend the depth limit.

        Args:
            current_limit: Current depth limit
            success_rate: Success rate of operations

        Returns:
            Extension amount
        

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get depth management statistics.

#### reset_history
**Parameters**: self
**Returns**: None
**Description**: Reset complexity and depth history.



## Function: __init__

**Parameters**: self, max_context_size, prune_ratio, min_entries_to_keep, critical_keys, strategy
**Description**: 
        Initialize context pruning strategy.

        Args:
            max_context_size: Maximum context size in bytes before pruning
            prune_ratio: Ratio of context to prune when triggered (0.0-1.0)
            min_entries_to_keep: Minimum entries to keep after pruning
            critical_keys: Set of keys that must never be pruned
            strategy: Pruning strategy ('lru', 'priority', 'size', 'hybrid')
        



## Function: should_prune

**Parameters**: self, context
**Returns**: bool
**Description**: 
        Check if context should be pruned based on size.

        Args:
            context: Context dictionary to check

        Returns:
            True if pruning should be triggered
        



## Function: prune_context

**Parameters**: self, context
**Returns**: PruningResult
**Description**: 
        Prune context using configured strategy.

        Args:
            context: Context dictionary to prune

        Returns:
            PruningResult with details of pruning operation
        



## Function: _identify_preserved_keys

**Parameters**: self, context
**Returns**: set[str]
**Description**: Identify keys that must be preserved (critical DNA).



## Function: _score_keys_for_pruning

**Parameters**: self, context, prunable_keys
**Returns**: list[tuple]
**Description**: 
        Score keys for pruning priority.

        Lower scores get pruned first.

        Args:
            context: Context dictionary
            prunable_keys: Keys that can be pruned

        Returns:
            List of (key, score) tuples sorted by score ascending
        



## Function: _calculate_key_score

**Parameters**: self, key, value
**Returns**: float
**Description**: 
        Calculate pruning score for a key.

        Higher scores = more important = pruned later.

        Args:
            key: Key name
            value: Key value

        Returns:
            Score (0-100)
        



## Function: _estimate_context_size

**Parameters**: self, context
**Returns**: int
**Description**: Estimate context size in bytes.



## Function: _estimate_entry_size

**Parameters**: self, value
**Returns**: int
**Description**: Estimate size of a single entry in bytes.



## Function: record_access

**Parameters**: self, key
**Returns**: None
**Description**: Record access timestamp for LRU tracking.



## Function: set_priority

**Parameters**: self, key, priority
**Returns**: None
**Description**: Set priority score for a key (0-100, higher = more important).



## Function: get_metrics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get pruning metrics.



## Function: reset_metrics

**Parameters**: self
**Returns**: None
**Description**: Reset pruning metrics.



## Function: __init__

**Parameters**: self, base_limit, max_limit, min_limit, enable_adaptive
**Description**: 
        Initialize adaptive depth manager.

        Args:
            base_limit: Default depth limit
            max_limit: Maximum allowable depth
            min_limit: Minimum allowable depth
            enable_adaptive: Enable adaptive depth calculation
        



## Function: calculate_adaptive_limit

**Parameters**: self, context, current_metrics
**Returns**: int
**Description**: 
        Calculate adaptive depth limit based on mission complexity.

        Args:
            context: Current execution context
            current_metrics: Optional metrics from current execution

        Returns:
            Calculated depth limit
        



## Function: _assess_complexity

**Parameters**: self, context, metrics
**Returns**: float
**Description**: 
        Assess mission complexity from 0.0 to 1.0.

        Args:
            context: Execution context
            metrics: Optional current metrics

        Returns:
            Complexity score (0.0 = simple, 1.0 = highly complex)
        



## Function: should_extend_limit

**Parameters**: self, current_depth, current_limit, success_rate
**Returns**: bool
**Description**: 
        Determine if depth limit should be extended mid-mission.

        Args:
            current_depth: Current recursion depth
            current_limit: Current depth limit
            success_rate: Success rate of operations (0.0-1.0)

        Returns:
            True if limit should be extended
        



## Function: get_extension_amount

**Parameters**: self, current_limit, success_rate
**Returns**: int
**Description**: 
        Calculate how much to extend the depth limit.

        Args:
            current_limit: Current depth limit
            success_rate: Success rate of operations

        Returns:
            Extension amount
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get depth management statistics.



## Function: reset_history

**Parameters**: self
**Returns**: None
**Description**: Reset complexity and depth history.



## Usage Examples

### Class Usage

```python
# Using PruningMetrics
pruningmetrics = PruningMetrics()
```

```python
# Using PruningResult
pruningresult = PruningResult()
```

```python
# Using ContextPruningStrategy
contextpruningstrategy = ContextPruningStrategy()
contextpruningstrategy.should_prune()
contextpruningstrategy.prune_context()
```

### Function Usage

```python
# Using __init__
result = __init__(max_context_size, prune_ratio)
```

```python
# Using should_prune
result = should_prune(context)
```

```python
# Using prune_context
result = prune_context(context)
```



---
**Generated**: 2026-03-26T09:39:04.368910
**Type**: api_reference
**Quality**: comprehensive
