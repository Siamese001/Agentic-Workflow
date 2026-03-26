# API Documentation: agentic_router

**Target Audience**: developers, api_users

# agentic_router API Documentation

**File**: `agentic_router.py`
**Classes**: 3
**Functions**: 7

## Classes

- **RouteTarget**
- **RoutingDecision**
- **AgenticRouter**

## Functions

- **_get_routing_gateway**
- **_get_proof_emitter**
- **__init__** -> None
- **register** -> None
- **register_mad** -> None
- **_classify** -> tuple[str, str, float]
- **list_targets** -> list[str]


## Class: RouteTarget

**Description**: A registered routing target (agent or workflow).



## Class: RoutingDecision

**Description**: Result of an AgenticRouter dispatch.



## Class: AgenticRouter

**Description**: Classifies input intent and dispatches to the most relevant registered target.

    Usage::

        router = AgenticRouter()
        router.register("resume_writer", handler_fn, intent_keywords=["resume", "cv"])
        router.register("code_reviewer", handler_fn2, intent_keywords=["code", "review"])
        decision = await router.route("Please review my Python code")

    Args:
        fallback_handler: Optional async fn called when no target scores above threshold.
        min_confidence:   Minimum score to dispatch to a target (default 0.2).
    

### Methods

#### __init__
**Parameters**: self, fallback_handler, min_confidence, classifier
**Returns**: None

#### register
**Parameters**: self, name, handler, intent_keywords, description
**Returns**: None
**Description**: Register a specialist agent or workflow as a routing target.

#### register_mad
**Parameters**: self, debaters, synthesizer
**Returns**: None
**Description**: Register Multi-Agent Debate as a named routing target.

        Args:
            debaters:   List of agent handlers that independently answer the input.
            synthesizer: Async fn that synthesizes debater outputs into a final answer.
        

#### _classify
**Parameters**: self, user_input
**Returns**: tuple[str, str, float]
**Description**: Intent classification — embedding similarity with keyword fallback.

        Tries the injected IntentEmbeddingClassifier first.  Falls back to
        keyword hit-ratio when the classifier is absent or returns None.

        Returns (intent_label, best_target_name, confidence_score).
        

#### list_targets
**Parameters**: self
**Returns**: list[str]



## Function: _get_routing_gateway



## Function: _get_proof_emitter



## Function: __init__

**Parameters**: self, fallback_handler, min_confidence, classifier
**Returns**: None


## Function: register

**Parameters**: self, name, handler, intent_keywords, description
**Returns**: None
**Description**: Register a specialist agent or workflow as a routing target.



## Function: register_mad

**Parameters**: self, debaters, synthesizer
**Returns**: None
**Description**: Register Multi-Agent Debate as a named routing target.

        Args:
            debaters:   List of agent handlers that independently answer the input.
            synthesizer: Async fn that synthesizes debater outputs into a final answer.
        



## Function: _classify

**Parameters**: self, user_input
**Returns**: tuple[str, str, float]
**Description**: Intent classification — embedding similarity with keyword fallback.

        Tries the injected IntentEmbeddingClassifier first.  Falls back to
        keyword hit-ratio when the classifier is absent or returns None.

        Returns (intent_label, best_target_name, confidence_score).
        



## Function: list_targets

**Parameters**: self
**Returns**: list[str]


## Usage Examples

### Class Usage

```python
# Using RouteTarget
routetarget = RouteTarget()
```

```python
# Using RoutingDecision
routingdecision = RoutingDecision()
```

```python
# Using AgenticRouter
agenticrouter = AgenticRouter()
agenticrouter.register()
agenticrouter.register_mad()
```

### Function Usage

```python
# Using _get_routing_gateway
result = _get_routing_gateway()
```

```python
# Using _get_proof_emitter
result = _get_proof_emitter()
```

```python
# Using __init__
result = __init__(fallback_handler, min_confidence)
```



---
**Generated**: 2026-03-26T09:39:02.649101
**Type**: api_reference
**Quality**: comprehensive
