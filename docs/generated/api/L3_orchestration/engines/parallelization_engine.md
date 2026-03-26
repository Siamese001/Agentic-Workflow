# API Documentation: parallelization_engine

**Target Audience**: developers, api_users

# parallelization_engine API Documentation

**File**: `parallelization_engine.py`
**Classes**: 3
**Functions**: 1

## Classes

- **ParallelMode** (inherits from Enum)
- **AggregationStrategy** (inherits from Enum)
- **ParallelizationEngine**

## Functions

- **__init__** -> None


## Class: ParallelMode

**Inherits from**: Enum



## Class: AggregationStrategy

**Inherits from**: Enum



## Class: ParallelizationEngine

**Description**: Fan-out / fan-in parallel execution engine.

    Args:
        worker_fn:     async (task: str, seed: int | None) -> Any
            Called for each parallel branch. In SECTIONING mode, ``task`` is a
            sub-task string; in SAMPLING mode, ``task`` is the same goal each time.
        mode:          ParallelMode (SECTIONING or SAMPLING).
        aggregation:   AggregationStrategy for reducing parallel outputs.
        synthesizer_fn: Required when aggregation=LLM_SYNTHESIZE.
                        async (outputs: list[Any]) -> str
        pass_predicate: Required when aggregation=FIRST_PASS.
                        sync (output: Any) -> bool
        max_concurrency: Optional semaphore cap on simultaneous workers.
    

### Methods

#### __init__
**Parameters**: self, worker_fn, mode, aggregation, synthesizer_fn, pass_predicate, max_concurrency
**Returns**: None



## Function: __init__

**Parameters**: self, worker_fn, mode, aggregation, synthesizer_fn, pass_predicate, max_concurrency
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ParallelMode
parallelmode = ParallelMode()
```

```python
# Using AggregationStrategy
aggregationstrategy = AggregationStrategy()
```

```python
# Using ParallelizationEngine
parallelizationengine = ParallelizationEngine()
```

### Function Usage

```python
# Using __init__
result = __init__(worker_fn, mode)
```



---
**Generated**: 2026-03-26T09:39:04.186023
**Type**: api_reference
**Quality**: comprehensive
