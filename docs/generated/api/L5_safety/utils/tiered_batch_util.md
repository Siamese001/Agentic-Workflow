# API Documentation: tiered_batch_util

**Target Audience**: developers, api_users

# tiered_batch_util API Documentation

**File**: `tiered_batch_util.py`
**Classes**: 1
**Functions**: 12

## Classes

- **TieredBatchProcessor**

## Functions

- **__init__**
- **_load_checkpoint** -> dict[str, Any]
- **_save_checkpoint** -> None
- **_get_semantic_cache**
- **_check_semantic_cache** -> dict | None
- **_store_semantic_cache** -> None
- **process_batch** -> dict[str, Any]
- **_process_tier2** -> None
- **_get_file_path** -> Path | None
- **_get_violation_type** -> str
- **get_statistics** -> dict[str, Any]
- **clear_checkpoint** -> None


## Class: TieredBatchProcessor

**Description**: 
    Smart batch processor with tiered disposition strategy.

    Tier 1: High-confidence heuristics auto-execute (no LLM)
    Tier 2: Low-confidence routes to LLM with semantic caching

    Attributes:
        agent: CognitiveDispositionAgent instance
        heuristic_threshold: Confidence threshold for auto-execution
        checkpoint_file: Path to checkpoint file
        use_semantic_cache: Enable Redis/Pinecone caching
    

### Methods

#### __init__
**Parameters**: self, agent, heuristic_threshold, checkpoint_file, use_semantic_cache, rate_limit_delay
**Description**: 
        Initialize the Tiered Batch Processor.

        Args:
            agent: CognitiveDispositionAgent instance
            heuristic_threshold: Min confidence for auto-execution
            checkpoint_file: Path to checkpoint file
            use_semantic_cache: Enable Redis/Pinecone caching
            rate_limit_delay: Seconds between LLM calls
        

#### _load_checkpoint
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load checkpoint from file.

#### _save_checkpoint
**Parameters**: self
**Returns**: None
**Description**: Save checkpoint to file.

#### _get_semantic_cache
**Parameters**: self
**Description**: 
        [PHASE 17] Lazy-load SemanticCacheManager.

        Returns:
            SemanticCacheManager instance or None
        

#### _check_semantic_cache
**Parameters**: self, file_path, violation_type
**Returns**: dict | None
**Description**: 
        [PHASE 17] Check semantic cache for cached disposition decision.

        Uses dual-layer caching:
        1. Redis: Exact content hash matching
        2. Pinecone: Semantic similarity matching

        Args:
            file_path: Path to file
            violation_type: Type of violation

        Returns:
            Cached decision dict or None
        

#### _store_semantic_cache
**Parameters**: self, file_path, violation_type, decision
**Returns**: None
**Description**: 
        [PHASE 17] Store disposition decision in semantic cache.

        Stores in both Redis (exact) and Pinecone (semantic) for meta-learning.

        Args:
            file_path: Path to file
            violation_type: Type of violation
            decision: Decision dict to cache
        

#### process_batch
**Parameters**: self, violations
**Returns**: dict[str, Any]
**Description**: 
        Process violations with tiered strategy.

        Args:
            violations: List of violation objects

        Returns:
            Processing statistics
        

#### _process_tier2
**Parameters**: self, tier2_queue
**Returns**: None
**Description**: 
        Process Tier 2 files with LLM and semantic caching.

        Args:
            tier2_queue: List of (violation, file_path, v_type, heuristic) tuples
        

#### _get_file_path
**Parameters**: self, violation
**Returns**: Path | None
**Description**: Extract file path from violation.

#### _get_violation_type
**Parameters**: self, violation
**Returns**: str
**Description**: Extract violation type from violation.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get processing statistics.

#### clear_checkpoint
**Parameters**: self
**Returns**: None
**Description**: Clear checkpoint and reset.



## Function: __init__

**Parameters**: self, agent, heuristic_threshold, checkpoint_file, use_semantic_cache, rate_limit_delay
**Description**: 
        Initialize the Tiered Batch Processor.

        Args:
            agent: CognitiveDispositionAgent instance
            heuristic_threshold: Min confidence for auto-execution
            checkpoint_file: Path to checkpoint file
            use_semantic_cache: Enable Redis/Pinecone caching
            rate_limit_delay: Seconds between LLM calls
        



## Function: _load_checkpoint

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load checkpoint from file.



## Function: _save_checkpoint

**Parameters**: self
**Returns**: None
**Description**: Save checkpoint to file.



## Function: _get_semantic_cache

**Parameters**: self
**Description**: 
        [PHASE 17] Lazy-load SemanticCacheManager.

        Returns:
            SemanticCacheManager instance or None
        



## Function: _check_semantic_cache

**Parameters**: self, file_path, violation_type
**Returns**: dict | None
**Description**: 
        [PHASE 17] Check semantic cache for cached disposition decision.

        Uses dual-layer caching:
        1. Redis: Exact content hash matching
        2. Pinecone: Semantic similarity matching

        Args:
            file_path: Path to file
            violation_type: Type of violation

        Returns:
            Cached decision dict or None
        



## Function: _store_semantic_cache

**Parameters**: self, file_path, violation_type, decision
**Returns**: None
**Description**: 
        [PHASE 17] Store disposition decision in semantic cache.

        Stores in both Redis (exact) and Pinecone (semantic) for meta-learning.

        Args:
            file_path: Path to file
            violation_type: Type of violation
            decision: Decision dict to cache
        



## Function: process_batch

**Parameters**: self, violations
**Returns**: dict[str, Any]
**Description**: 
        Process violations with tiered strategy.

        Args:
            violations: List of violation objects

        Returns:
            Processing statistics
        



## Function: _process_tier2

**Parameters**: self, tier2_queue
**Returns**: None
**Description**: 
        Process Tier 2 files with LLM and semantic caching.

        Args:
            tier2_queue: List of (violation, file_path, v_type, heuristic) tuples
        



## Function: _get_file_path

**Parameters**: self, violation
**Returns**: Path | None
**Description**: Extract file path from violation.



## Function: _get_violation_type

**Parameters**: self, violation
**Returns**: str
**Description**: Extract violation type from violation.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get processing statistics.



## Function: clear_checkpoint

**Parameters**: self
**Returns**: None
**Description**: Clear checkpoint and reset.



## Usage Examples

### Class Usage

```python
# Using TieredBatchProcessor
tieredbatchprocessor = TieredBatchProcessor()
tieredbatchprocessor.process_batch()
tieredbatchprocessor.get_statistics()
```

### Function Usage

```python
# Using __init__
result = __init__(agent, heuristic_threshold)
```

```python
# Using _load_checkpoint
result = _load_checkpoint()
```

```python
# Using _save_checkpoint
result = _save_checkpoint()
```



---
**Generated**: 2026-03-26T09:39:05.698991
**Type**: api_reference
**Quality**: comprehensive
