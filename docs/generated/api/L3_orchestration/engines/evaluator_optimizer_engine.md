# API Documentation: evaluator_optimizer_engine

**Target Audience**: developers, api_users

# evaluator_optimizer_engine API Documentation

**File**: `evaluator_optimizer_engine.py`
**Classes**: 1
**Functions**: 2

## Classes

- **EvaluatorOptimizerEngine**

## Functions

- **__init__** -> None
- **from_rg_engines** -> EvaluatorOptimizerEngine


## Class: EvaluatorOptimizerEngine

**Description**: Generator → Evaluator → Optimizer feedback loop.

    Args:
        generator_fn:  async (task, prior_response) -> dict  (content payload)
        evaluator_fn:  async (content) -> dict  with at least ``score`` (float) and
                       ``issues`` (list[str]) and ``status`` ('passed'|'warning'|…)
        optimizer_fn:  async (content, issues) -> dict  (revised content payload)
        score_threshold: Stop when evaluator score >= this value (default 80.0).
        max_iterations:  Hard cap on revision loops (default 5).
    

### Methods

#### __init__
**Parameters**: self, generator_fn, evaluator_fn, optimizer_fn, score_threshold, max_iterations
**Returns**: None

#### from_rg_engines
**Parameters**: cls, ctx, generator_fn, score_threshold, max_iterations
**Returns**: EvaluatorOptimizerEngine
**Description**: Factory that wires ContentQualityEngine + ContentOptimizerEngine.

        Args:
            ctx: apps_rg buffer context (passed to both engines).
            generator_fn: Async callable producing the initial content dict.
            score_threshold: Quality score gate.
            max_iterations: Max revision cycles.
        



## Function: __init__

**Parameters**: self, generator_fn, evaluator_fn, optimizer_fn, score_threshold, max_iterations
**Returns**: None


## Function: from_rg_engines

**Parameters**: cls, ctx, generator_fn, score_threshold, max_iterations
**Returns**: EvaluatorOptimizerEngine
**Description**: Factory that wires ContentQualityEngine + ContentOptimizerEngine.

        Args:
            ctx: apps_rg buffer context (passed to both engines).
            generator_fn: Async callable producing the initial content dict.
            score_threshold: Quality score gate.
            max_iterations: Max revision cycles.
        



## Usage Examples

### Class Usage

```python
# Using EvaluatorOptimizerEngine
evaluatoroptimizerengine = EvaluatorOptimizerEngine()
evaluatoroptimizerengine.from_rg_engines()
```

### Function Usage

```python
# Using __init__
result = __init__(generator_fn, evaluator_fn)
```

```python
# Using from_rg_engines
result = from_rg_engines(cls, ctx)
```



---
**Generated**: 2026-03-26T09:39:04.167038
**Type**: api_reference
**Quality**: comprehensive
