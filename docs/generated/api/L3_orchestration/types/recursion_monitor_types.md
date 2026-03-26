# API Documentation: recursion_monitor_types

**Target Audience**: developers, api_users

# recursion_monitor_types API Documentation

**File**: `recursion_monitor_types.py`
**Classes**: 6
**Functions**: 19

## Classes

- **HealthStatus** (inherits from str, Enum)
- **AlertSeverity** (inherits from str, Enum)
- **Alert**
- **HealthCheck**
- **RecursionSnapshot**
- **RecursionMonitor**

## Functions

- **__init__**
- **record_spawn** -> None
- **record_snapshot** -> RecursionSnapshot
- **_calculate_health_status** -> HealthStatus
- **run_health_checks** -> list[HealthCheck]
- **get_overall_health** -> HealthStatus
- **_open_circuit** -> None
- **close_circuit** -> None
- **is_circuit_open** -> bool
- **_check_performance_degradation** -> None
- **_create_alert** -> Alert
- **get_alerts** -> list[Alert]
- **acknowledge_alert** -> bool
- **clear_alerts** -> int
- **_cleanup_old_metrics** -> None
- **set_threshold** -> bool
- **get_thresholds** -> dict[str, float]
- **get_metrics_summary** -> dict[str, Any]
- **reset** -> None


## Class: HealthStatus

**Description**: Health status levels for the recursion system.

**Inherits from**: str, Enum



## Class: AlertSeverity

**Description**: Alert severity levels.

**Inherits from**: str, Enum



## Class: Alert

**Description**: Alert data structure.



## Class: HealthCheck

**Description**: Health check result.



## Class: RecursionSnapshot

**Description**: Point-in-time snapshot of recursion state.



## Class: RecursionMonitor

**Description**: 
    Production-grade monitoring for Forward-Rolling Recursion.

    Features:
    - Real-time metrics collection
    - Health checks with configurable thresholds
    - Alert generation and management
    - Circuit breaker integration
    - Performance degradation detection
    

### Methods

#### __init__
**Parameters**: self, alert_callback, health_check_interval_sec, metrics_retention_hours
**Description**: 
        Initialize recursion monitor.

        Args:
            alert_callback: Optional callback for alert notifications
            health_check_interval_sec: Interval between health checks
            metrics_retention_hours: Hours to retain metric history
        

#### record_spawn
**Parameters**: self, success, depth, duration_ms, memory_bytes, cache_hit
**Returns**: None
**Description**: 
        Record a spawn operation for monitoring.

        Args:
            success: Whether spawn was successful
            depth: Recursion depth at spawn
            duration_ms: Duration of spawn operation
            memory_bytes: Memory used by spawn
            cache_hit: Whether validation cache was hit
        

#### record_snapshot
**Parameters**: self, active_recursions, total_spawns, successful_spawns, depths, memory_bytes, cache_hits, cache_misses
**Returns**: RecursionSnapshot
**Description**: 
        Record a point-in-time snapshot of recursion state.

        Args:
            active_recursions: Number of active recursive operations
            total_spawns: Total spawn operations
            successful_spawns: Number of successful spawns
            depths: List of current depths
            memory_bytes: Total memory usage
            cache_hits: Number of cache hits
            cache_misses: Number of cache misses

        Returns:
            RecursionSnapshot with current state
        

#### _calculate_health_status
**Parameters**: self, active_recursions, success_rate, avg_depth, memory_bytes, cache_hit_rate
**Returns**: HealthStatus
**Description**: Calculate overall health status based on metrics.

#### run_health_checks
**Parameters**: self
**Returns**: list[HealthCheck]
**Description**: 
        Run all health checks and return results.

        Returns:
            List of HealthCheck results
        

#### get_overall_health
**Parameters**: self
**Returns**: HealthStatus
**Description**: Get overall system health status.

#### _open_circuit
**Parameters**: self
**Returns**: None
**Description**: Open the circuit breaker.

#### close_circuit
**Parameters**: self
**Returns**: None
**Description**: Manually close the circuit breaker.

#### is_circuit_open
**Parameters**: self
**Returns**: bool
**Description**: Check if circuit breaker is open.

#### _check_performance_degradation
**Parameters**: self, duration_ms
**Returns**: None
**Description**: Check for performance degradation.

#### _create_alert
**Parameters**: self, severity, message, source, metadata
**Returns**: Alert
**Description**: Create and store an alert.

#### get_alerts
**Parameters**: self, severity, unacknowledged_only
**Returns**: list[Alert]
**Description**: Get alerts with optional filtering.

#### acknowledge_alert
**Parameters**: self, index
**Returns**: bool
**Description**: Acknowledge an alert by index.

#### clear_alerts
**Parameters**: self
**Returns**: int
**Description**: Clear all alerts and return count cleared.

#### _cleanup_old_metrics
**Parameters**: self
**Returns**: None
**Description**: Remove metrics older than retention period.

#### set_threshold
**Parameters**: self, name, value
**Returns**: bool
**Description**: Set a monitoring threshold.

#### get_thresholds
**Parameters**: self
**Returns**: dict[str, float]
**Description**: Get current monitoring thresholds.

#### get_metrics_summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get summary of collected metrics.

#### reset
**Parameters**: self
**Returns**: None
**Description**: Reset all monitoring state.



## Function: __init__

**Parameters**: self, alert_callback, health_check_interval_sec, metrics_retention_hours
**Description**: 
        Initialize recursion monitor.

        Args:
            alert_callback: Optional callback for alert notifications
            health_check_interval_sec: Interval between health checks
            metrics_retention_hours: Hours to retain metric history
        



## Function: record_spawn

**Parameters**: self, success, depth, duration_ms, memory_bytes, cache_hit
**Returns**: None
**Description**: 
        Record a spawn operation for monitoring.

        Args:
            success: Whether spawn was successful
            depth: Recursion depth at spawn
            duration_ms: Duration of spawn operation
            memory_bytes: Memory used by spawn
            cache_hit: Whether validation cache was hit
        



## Function: record_snapshot

**Parameters**: self, active_recursions, total_spawns, successful_spawns, depths, memory_bytes, cache_hits, cache_misses
**Returns**: RecursionSnapshot
**Description**: 
        Record a point-in-time snapshot of recursion state.

        Args:
            active_recursions: Number of active recursive operations
            total_spawns: Total spawn operations
            successful_spawns: Number of successful spawns
            depths: List of current depths
            memory_bytes: Total memory usage
            cache_hits: Number of cache hits
            cache_misses: Number of cache misses

        Returns:
            RecursionSnapshot with current state
        



## Function: _calculate_health_status

**Parameters**: self, active_recursions, success_rate, avg_depth, memory_bytes, cache_hit_rate
**Returns**: HealthStatus
**Description**: Calculate overall health status based on metrics.



## Function: run_health_checks

**Parameters**: self
**Returns**: list[HealthCheck]
**Description**: 
        Run all health checks and return results.

        Returns:
            List of HealthCheck results
        



## Function: get_overall_health

**Parameters**: self
**Returns**: HealthStatus
**Description**: Get overall system health status.



## Function: _open_circuit

**Parameters**: self
**Returns**: None
**Description**: Open the circuit breaker.



## Function: close_circuit

**Parameters**: self
**Returns**: None
**Description**: Manually close the circuit breaker.



## Function: is_circuit_open

**Parameters**: self
**Returns**: bool
**Description**: Check if circuit breaker is open.



## Function: _check_performance_degradation

**Parameters**: self, duration_ms
**Returns**: None
**Description**: Check for performance degradation.



## Function: _create_alert

**Parameters**: self, severity, message, source, metadata
**Returns**: Alert
**Description**: Create and store an alert.



## Function: get_alerts

**Parameters**: self, severity, unacknowledged_only
**Returns**: list[Alert]
**Description**: Get alerts with optional filtering.



## Function: acknowledge_alert

**Parameters**: self, index
**Returns**: bool
**Description**: Acknowledge an alert by index.



## Function: clear_alerts

**Parameters**: self
**Returns**: int
**Description**: Clear all alerts and return count cleared.



## Function: _cleanup_old_metrics

**Parameters**: self
**Returns**: None
**Description**: Remove metrics older than retention period.



## Function: set_threshold

**Parameters**: self, name, value
**Returns**: bool
**Description**: Set a monitoring threshold.



## Function: get_thresholds

**Parameters**: self
**Returns**: dict[str, float]
**Description**: Get current monitoring thresholds.



## Function: get_metrics_summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get summary of collected metrics.



## Function: reset

**Parameters**: self
**Returns**: None
**Description**: Reset all monitoring state.



## Usage Examples

### Class Usage

```python
# Using HealthStatus
healthstatus = HealthStatus()
```

```python
# Using AlertSeverity
alertseverity = AlertSeverity()
```

```python
# Using Alert
alert = Alert()
```

### Function Usage

```python
# Using __init__
result = __init__(alert_callback, health_check_interval_sec)
```

```python
# Using record_spawn
result = record_spawn(success, depth)
```

```python
# Using record_snapshot
result = record_snapshot(active_recursions, total_spawns)
```



---
**Generated**: 2026-03-26T09:39:04.402441
**Type**: api_reference
**Quality**: comprehensive
