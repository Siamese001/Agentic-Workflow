# API Documentation: vigilance_routing

**Target Audience**: developers, api_users

# vigilance_routing API Documentation

**File**: `vigilance_routing.py`
**Classes**: 0
**Functions**: 1


## Functions

- **route_vigilance_event** -> RoutePath


## Function: route_vigilance_event

**Parameters**: event
**Returns**: RoutePath
**Description**: §Wave4.1 — Deterministic routing from VigilanceEventArtifact tier.

    Returns:
        RoutePath.HUMAN_ESCALATION for HIGH/CRITICAL
        RoutePath.STANDARD_VALIDATION for LOW/MEDIUM
    



## Usage Examples

### Function Usage

```python
# Using route_vigilance_event
result = route_vigilance_event(event)
```



---
**Generated**: 2026-03-26T09:39:02.644022
**Type**: api_reference
**Quality**: comprehensive
