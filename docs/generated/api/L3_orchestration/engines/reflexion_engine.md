# API Documentation: reflexion_engine

**Target Audience**: developers, api_users

# reflexion_engine API Documentation

**File**: `reflexion_engine.py`
**Classes**: 1
**Functions**: 2

## Classes

- **ReflexionEngine**

## Functions

- **__init__** -> None
- **with_rg_scorer** -> ReflexionEngine


## Class: ReflexionEngine

**Description**: Iterative critique-revise loop with verbal memory.

    All LLM interactions are injected as async callables so the engine
    remains LLM-provider-agnostic and fully testable with fakes.

    Args:
        generator_fn:  async (task, prior_response, memory_summary) -> str
            Produces the initial response (prior_response=None) or a revision.
        evaluator_fn:  async (task, response) -> dict with keys:
            ``critique`` (str), ``score`` (float 0-1), ``passed`` (bool)
        score_threshold: Stop iterating when score >= this value (default 0.85).
        max_iterations:  Hard upper bound on revision loops (default 5).
    

### Methods

#### __init__
**Parameters**: self, generator_fn, evaluator_fn, score_threshold, max_iterations
**Returns**: None

#### with_rg_scorer
**Parameters**: cls, generator_fn, score_threshold, max_iterations
**Returns**: ReflexionEngine
**Description**: Factory that wires the existing apps_rg ReflectionEngine as the scorer.

        The ReflectionEngine produces a numeric score from workflow_results;
        here we wrap a single-response dict to reuse its scoring logic.
        



## Function: __init__

**Parameters**: self, generator_fn, evaluator_fn, score_threshold, max_iterations
**Returns**: None


## Function: with_rg_scorer

**Parameters**: cls, generator_fn, score_threshold, max_iterations
**Returns**: ReflexionEngine
**Description**: Factory that wires the existing apps_rg ReflectionEngine as the scorer.

        The ReflectionEngine produces a numeric score from workflow_results;
        here we wrap a single-response dict to reuse its scoring logic.
        



## Usage Examples

### Class Usage

```python
# Using ReflexionEngine
reflexionengine = ReflexionEngine()
reflexionengine.with_rg_scorer()
```

### Function Usage

```python
# Using __init__
result = __init__(generator_fn, evaluator_fn)
```

```python
# Using with_rg_scorer
result = with_rg_scorer(cls, generator_fn)
```



---
**Generated**: 2026-03-26T09:39:04.205416
**Type**: api_reference
**Quality**: comprehensive
