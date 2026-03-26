# API Documentation: shadow_routing_wiring

**Target Audience**: developers, api_users

# shadow_routing_wiring API Documentation

**File**: `shadow_routing_wiring.py`
**Classes**: 1
**Functions**: 5

## Classes

- **ShadowRoutingWiring**

## Functions

- **get_shadow_wiring** -> ShadowRoutingWiring
- **observe_routing_decision** -> ShadowRoutingTelemetry | None
- **__init__**
- **observe_and_classify** -> ShadowRoutingTelemetry | None
- **validate_non_invasiveness** -> bool


## Class: ShadowRoutingWiring

**Description**: Wires shadow routing into L0 as a non-invasive side-channel.

    This class ensures that shadow classification cannot affect actual routing
    decisions and only provides observational capabilities.
    

### Methods

#### __init__
**Parameters**: self, shadow_classifier, enable_telemetry, enable_l4_storage
**Description**: Initialize shadow routing wiring.

        Args:
            shadow_classifier: Shadow classifier instance (created if None)
            enable_telemetry: Whether to emit telemetry to L6
            enable_l4_storage: Whether to store to L4 bounded store
        

#### observe_and_classify
**Parameters**: self, route_decision, additional_context
**Returns**: ShadowRoutingTelemetry | None
**Description**: Observe routing decision and produce shadow classification.

        This is called AFTER the actual routing decision is made and
        cannot affect the routing outcome. It's strictly observational.

        Args:
            route_decision: The actual routing decision (already made)
            additional_context: Optional additional context

        Returns:
            Shadow telemetry if enabled, None otherwise
        

#### validate_non_invasiveness
**Parameters**: self, route_decision
**Returns**: bool
**Description**: Validate that shadow routing cannot affect the actual route.

        This is a safety check to ensure the shadow classifier is truly
        non-invasive. It verifies that the original route decision is
        unchanged.

        Args:
            route_decision: The original routing decision

        Returns:
            True if non-invasiveness is guaranteed
        



## Function: get_shadow_wiring

**Returns**: ShadowRoutingWiring
**Description**: Get the global shadow routing wiring instance.

    Returns:
        Global shadow routing wiring instance
    



## Function: observe_routing_decision

**Parameters**: route_decision, additional_context
**Returns**: ShadowRoutingTelemetry | None
**Description**: Convenience function to observe a routing decision.

    This is the main entry point called from L0 routing pipeline.

    Args:
        route_decision: The routing decision to observe
        additional_context: Optional additional context

    Returns:
        Shadow telemetry if enabled, None otherwise
    



## Function: __init__

**Parameters**: self, shadow_classifier, enable_telemetry, enable_l4_storage
**Description**: Initialize shadow routing wiring.

        Args:
            shadow_classifier: Shadow classifier instance (created if None)
            enable_telemetry: Whether to emit telemetry to L6
            enable_l4_storage: Whether to store to L4 bounded store
        



## Function: observe_and_classify

**Parameters**: self, route_decision, additional_context
**Returns**: ShadowRoutingTelemetry | None
**Description**: Observe routing decision and produce shadow classification.

        This is called AFTER the actual routing decision is made and
        cannot affect the routing outcome. It's strictly observational.

        Args:
            route_decision: The actual routing decision (already made)
            additional_context: Optional additional context

        Returns:
            Shadow telemetry if enabled, None otherwise
        



## Function: validate_non_invasiveness

**Parameters**: self, route_decision
**Returns**: bool
**Description**: Validate that shadow routing cannot affect the actual route.

        This is a safety check to ensure the shadow classifier is truly
        non-invasive. It verifies that the original route decision is
        unchanged.

        Args:
            route_decision: The original routing decision

        Returns:
            True if non-invasiveness is guaranteed
        



## Usage Examples

### Class Usage

```python
# Using ShadowRoutingWiring
shadowroutingwiring = ShadowRoutingWiring()
shadowroutingwiring.observe_and_classify()
shadowroutingwiring.validate_non_invasiveness()
```

### Function Usage

```python
# Using get_shadow_wiring
result = get_shadow_wiring()
```

```python
# Using observe_routing_decision
result = observe_routing_decision(route_decision, additional_context)
```

```python
# Using __init__
result = __init__(shadow_classifier, enable_telemetry)
```



---
**Generated**: 2026-03-26T09:39:02.671673
**Type**: api_reference
**Quality**: comprehensive
