# API Documentation: routing_outcome_adapter

**Target Audience**: developers, api_users

# routing_outcome_adapter API Documentation

**File**: `routing_outcome_adapter.py`
**Classes**: 1
**Functions**: 4

## Classes

- **RoutingOutcomeAdapter**

## Functions

- **_outcome_from_decision** -> str
- **build_routing_outcome_package** -> MetaLearningChangePackage
- **__init__** -> None
- **emit** -> bool


## Class: RoutingOutcomeAdapter

**Description**: Enqueues routing outcome packages onto an injected MetaLearningBus.

    Usage::

        bus = MetaLearningBus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        decision = await router.route(user_input)
        adapter.emit(decision, timestamp_utc=now)

    Args:
        bus: The MetaLearningBus instance to enqueue packages onto.
    

### Methods

#### __init__
**Parameters**: self, bus
**Returns**: None

#### emit
**Parameters**: self, decision, timestamp_utc
**Returns**: bool
**Description**: Wrap decision into a change package and enqueue on the bus.

        Args:
            decision:      Resolved RoutingDecision from AgenticRouter.route().
            timestamp_utc: Caller-supplied Unix timestamp.

        Returns:
            True if enqueued successfully, False on any error (fail-open).
        



## Function: _outcome_from_decision

**Parameters**: decision
**Returns**: str
**Description**: Derive a canonical outcome string from a RoutingDecision.



## Function: build_routing_outcome_package

**Parameters**: decision, timestamp_utc
**Returns**: MetaLearningChangePackage
**Description**: Build a MetaLearningChangePackage from a resolved RoutingDecision.

    Args:
        decision:      The RoutingDecision returned by AgenticRouter.route().
        timestamp_utc: Caller-supplied Unix timestamp (no wall-clock read).

    Returns:
        Immutable, deterministically-hashed MetaLearningChangePackage.
    



## Function: __init__

**Parameters**: self, bus
**Returns**: None


## Function: emit

**Parameters**: self, decision, timestamp_utc
**Returns**: bool
**Description**: Wrap decision into a change package and enqueue on the bus.

        Args:
            decision:      Resolved RoutingDecision from AgenticRouter.route().
            timestamp_utc: Caller-supplied Unix timestamp.

        Returns:
            True if enqueued successfully, False on any error (fail-open).
        



## Usage Examples

### Class Usage

```python
# Using RoutingOutcomeAdapter
routingoutcomeadapter = RoutingOutcomeAdapter()
routingoutcomeadapter.emit()
```

### Function Usage

```python
# Using _outcome_from_decision
result = _outcome_from_decision(decision)
```

```python
# Using build_routing_outcome_package
result = build_routing_outcome_package(decision, timestamp_utc)
```

```python
# Using __init__
result = __init__(bus)
```



---
**Generated**: 2026-03-26T09:39:02.666656
**Type**: api_reference
**Quality**: comprehensive
