# API Documentation: shadow_router_classifier

**Target Audience**: developers, api_users

# shadow_router_classifier API Documentation

**File**: `shadow_router_classifier.py`
**Classes**: 1
**Functions**: 6

## Classes

- **ShadowRouterClassifier**

## Functions

- **_get_canonical_json**
- **__init__**
- **compute_routing_features** -> dict[str, Any]
- **classify_shadow_route** -> tuple[RoutePath, ShadowRoutingRationale, float]
- **observe_routing_decision** -> ShadowRoutingDecision
- **emit_telemetry** -> ShadowRoutingTelemetry


## Class: ShadowRouterClassifier

**Description**: Non-invasive shadow router classifier for drift detection.

    This classifier observes routing decisions and produces shadow suggestions
    without affecting the actual routing. It's strictly read-only and
    emits telemetry to L6 and optionally stores to L4.
    

### Methods

#### __init__
**Parameters**: self, model_version, ruleset_version
**Description**: Initialize shadow router classifier.

        Args:
            model_version: Version identifier for the shadow model
            ruleset_version: Version identifier for the ruleset
        

#### compute_routing_features
**Parameters**: self, route_decision, additional_context
**Returns**: dict[str, Any]
**Description**: Compute deterministic features from routing decision.

        Args:
            route_decision: The actual routing decision made by L0
            additional_context: Optional additional context for feature computation

        Returns:
            Dictionary of deterministic routing features
        

#### classify_shadow_route
**Parameters**: self, features
**Returns**: tuple[RoutePath, ShadowRoutingRationale, float]
**Description**: Classify shadow route suggestion and compute drift score.

        This is a simple rule-based classifier for Phase 9. In production,
        this could be a machine learning model or more sophisticated rules.

        Args:
            features: Routing features computed from actual decision

        Returns:
            Tuple of (shadow_route, shadow_rationale, drift_score)
        

#### observe_routing_decision
**Parameters**: self, route_decision, additional_context, timestamp
**Returns**: ShadowRoutingDecision
**Description**: Observe a routing decision and produce shadow classification.

        This is the main entry point for shadow classification. It's called
        after the actual routing decision is made and cannot affect it.

        Args:
            route_decision: The actual routing decision made by L0
            additional_context: Optional additional context
            timestamp: Deterministic timestamp (defaults to route_decision.timestamp)

        Returns:
            Shadow routing decision with drift analysis
        

#### emit_telemetry
**Parameters**: self, shadow_decision, emitted_at
**Returns**: ShadowRoutingTelemetry
**Description**: Emit telemetry for shadow routing decision.

        Args:
            shadow_decision: The shadow routing decision
            emitted_at: Deterministic timestamp (defaults to shadow_decision.timestamp)

        Returns:
            Telemetry artifact for L6/L4 emission
        



## Function: _get_canonical_json



## Function: __init__

**Parameters**: self, model_version, ruleset_version
**Description**: Initialize shadow router classifier.

        Args:
            model_version: Version identifier for the shadow model
            ruleset_version: Version identifier for the ruleset
        



## Function: compute_routing_features

**Parameters**: self, route_decision, additional_context
**Returns**: dict[str, Any]
**Description**: Compute deterministic features from routing decision.

        Args:
            route_decision: The actual routing decision made by L0
            additional_context: Optional additional context for feature computation

        Returns:
            Dictionary of deterministic routing features
        



## Function: classify_shadow_route

**Parameters**: self, features
**Returns**: tuple[RoutePath, ShadowRoutingRationale, float]
**Description**: Classify shadow route suggestion and compute drift score.

        This is a simple rule-based classifier for Phase 9. In production,
        this could be a machine learning model or more sophisticated rules.

        Args:
            features: Routing features computed from actual decision

        Returns:
            Tuple of (shadow_route, shadow_rationale, drift_score)
        



## Function: observe_routing_decision

**Parameters**: self, route_decision, additional_context, timestamp
**Returns**: ShadowRoutingDecision
**Description**: Observe a routing decision and produce shadow classification.

        This is the main entry point for shadow classification. It's called
        after the actual routing decision is made and cannot affect it.

        Args:
            route_decision: The actual routing decision made by L0
            additional_context: Optional additional context
            timestamp: Deterministic timestamp (defaults to route_decision.timestamp)

        Returns:
            Shadow routing decision with drift analysis
        



## Function: emit_telemetry

**Parameters**: self, shadow_decision, emitted_at
**Returns**: ShadowRoutingTelemetry
**Description**: Emit telemetry for shadow routing decision.

        Args:
            shadow_decision: The shadow routing decision
            emitted_at: Deterministic timestamp (defaults to shadow_decision.timestamp)

        Returns:
            Telemetry artifact for L6/L4 emission
        



## Usage Examples

### Class Usage

```python
# Using ShadowRouterClassifier
shadowrouterclassifier = ShadowRouterClassifier()
shadowrouterclassifier.compute_routing_features()
shadowrouterclassifier.classify_shadow_route()
```

### Function Usage

```python
# Using _get_canonical_json
result = _get_canonical_json()
```

```python
# Using __init__
result = __init__(model_version, ruleset_version)
```

```python
# Using compute_routing_features
result = compute_routing_features(route_decision, additional_context)
```



---
**Generated**: 2026-03-26T09:39:02.668661
**Type**: api_reference
**Quality**: comprehensive
