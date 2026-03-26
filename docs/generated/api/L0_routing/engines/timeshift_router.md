# API Documentation: timeshift_router

**Target Audience**: developers, api_users

# timeshift_router API Documentation

**File**: `timeshift_router.py`
**Classes**: 2
**Functions**: 3

## Classes

- **RoutingMode**
- **TimeshiftRoutingDecision**

## Functions

- **_get_routing_config_and_active**
- **_get_prior_detection_signal**
- **evaluate_timeshift_routing** -> TimeshiftRoutingDecision


## Class: RoutingMode



## Class: TimeshiftRoutingDecision

**Description**: Result of a time-shifted routing evaluation.



## Function: _get_routing_config_and_active



## Function: _get_prior_detection_signal



## Function: evaluate_timeshift_routing

**Parameters**: execution_start_tick, routing_config
**Returns**: TimeshiftRoutingDecision
**Description**: 
    Evaluate routing mode using ONLY prior committed signals.

    Args:
        execution_start_tick: The tick at which this execution started.
            Only signals committed BEFORE this tick are considered.
        routing_config: Optional override; defaults to L4 SSOT RoutingConfig.

    Returns:
        TimeshiftRoutingDecision with mode and audit fields.

    GUARANTEE: same_cycle_influence is always False — signals emitted
    during this execution cycle cannot affect this decision.
    



## Usage Examples

### Class Usage

```python
# Using RoutingMode
routingmode = RoutingMode()
```

```python
# Using TimeshiftRoutingDecision
timeshiftroutingdecision = TimeshiftRoutingDecision()
```

### Function Usage

```python
# Using _get_routing_config_and_active
result = _get_routing_config_and_active()
```

```python
# Using _get_prior_detection_signal
result = _get_prior_detection_signal()
```

```python
# Using evaluate_timeshift_routing
result = evaluate_timeshift_routing(execution_start_tick, routing_config)
```



---
**Generated**: 2026-03-26T09:39:02.671673
**Type**: api_reference
**Quality**: comprehensive
