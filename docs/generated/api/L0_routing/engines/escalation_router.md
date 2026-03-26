# API Documentation: escalation_router

**Target Audience**: developers, api_users

# escalation_router API Documentation

**File**: `escalation_router.py`
**Classes**: 0
**Functions**: 3


## Functions

- **_get_routing_config_class**
- **_get_violation_event_store_class**
- **decide_mode_from_prior_violations** -> str


## Function: _get_routing_config_class



## Function: _get_violation_event_store_class



## Function: decide_mode_from_prior_violations

**Parameters**: execution_start_tick, routing_config, violation_store
**Returns**: str
**Description**: 
    Determine L0 routing mode based solely on prior violations.

    Algorithm
    ---------
    1. Fetch events in window [execution_start_tick - window_ticks, execution_start_tick).
       Same-cycle events (commit_tick == execution_start_tick) are excluded by the store.
    2. For each prior event, check:
       a. severity_score >= escalation_severity_threshold (from config — no hardcoded literal)
       b. OR any violation_code in event.violation_codes is in denylist (if denylist non-empty)
    3. If any event triggers escalation → return routing_config.escalation_mode.
    4. Otherwise → return "normal".

    Parameters
    ----------
    execution_start_tick : int
        The commit_tick at which the current execution begins.
    routing_config : RoutingConfig
        Versioned config supplying all thresholds (no hardcoded literals).
    violation_store : ViolationEventStore
        L4 store to query prior violations from.

    Returns
    -------
    str
        Routing mode string ("normal" or routing_config.escalation_mode).
    



## Usage Examples

### Function Usage

```python
# Using _get_routing_config_class
result = _get_routing_config_class()
```

```python
# Using _get_violation_event_store_class
result = _get_violation_event_store_class()
```

```python
# Using decide_mode_from_prior_violations
result = decide_mode_from_prior_violations(execution_start_tick, routing_config)
```



---
**Generated**: 2026-03-26T09:39:02.653608
**Type**: api_reference
**Quality**: comprehensive
