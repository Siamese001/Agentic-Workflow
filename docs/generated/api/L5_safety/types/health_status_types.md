# API Documentation: health_status_types

**Target Audience**: developers, api_users

# health_status_types API Documentation

**File**: `health_status_types.py`
**Classes**: 4
**Functions**: 2

## Classes

- **HealthStatus** (inherits from Enum)
- **AlertSeverity** (inherits from Enum)
- **health_metrics**
- **HealthAlert**

## Functions

- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]


## Class: HealthStatus

**Description**: Agent health status.

**Inherits from**: Enum



## Class: AlertSeverity

**Description**: Alert Severity levels.

**Inherits from**: Enum



## Class: health_metrics

**Description**: Health metrics for an agent.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: HealthAlert

**Description**: Health alert for degradation detection.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



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
# Using health_metrics
health_metrics = health_metrics()
health_metrics.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:05.512003
**Type**: api_reference
**Quality**: comprehensive
