# API Documentation: CachedStateLedger

**Target Audience**: developers, api_users

# CachedStateLedger API Documentation

**File**: `CachedStateLedger.py`
**Classes**: 1
**Functions**: 10

## Classes

- **CachedStateLedger** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **cache_validation_context**
- **get_cached_validation_context** -> dict | None
- **_record_successful_trace**
- **get_successful_traces** -> list[dict]
- **append_audit_event**
- **_run_self_tests** -> bool
- **_perform_healing** -> bool
- **heal** -> dict
- **heal_repository** -> dict


## Class: CachedStateLedger

**Description**: 
    Sovereign L4 state base — Redis cache for context, audit, Historian.
    All L4 components inherit from this.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, session_id

#### cache_validation_context
**Parameters**: self, key, context
**Description**: cache validation context for instant access

#### get_cached_validation_context
**Parameters**: self, key
**Returns**: dict | None

#### _record_successful_trace
**Parameters**: self, trace
**Description**: Internal helper to maintain successful_traces list in both Redis and memory mode

#### get_successful_traces
**Parameters**: self
**Returns**: list[dict]
**Description**: Public accessor required by ValidationContext and GeminiSpy telemetry

#### append_audit_event
**Parameters**: self, event
**Description**: Immutable append-only audit trail via Redis List

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Run self-tests for CachedStateLedgerAgent.

#### _perform_healing
**Parameters**: self, anomaly
**Returns**: bool
**Description**: Perform healing for detected anomalies.

#### heal
**Parameters**: self
**Returns**: dict
**Description**: heal() not implemented for CachedStateLedgerAgent.

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Function: __init__

**Parameters**: self, project_root, session_id


## Function: cache_validation_context

**Parameters**: self, key, context
**Description**: cache validation context for instant access



## Function: get_cached_validation_context

**Parameters**: self, key
**Returns**: dict | None


## Function: _record_successful_trace

**Parameters**: self, trace
**Description**: Internal helper to maintain successful_traces list in both Redis and memory mode



## Function: get_successful_traces

**Parameters**: self
**Returns**: list[dict]
**Description**: Public accessor required by ValidationContext and GeminiSpy telemetry



## Function: append_audit_event

**Parameters**: self, event
**Description**: Immutable append-only audit trail via Redis List



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Run self-tests for CachedStateLedgerAgent.



## Function: _perform_healing

**Parameters**: self, anomaly
**Returns**: bool
**Description**: Perform healing for detected anomalies.



## Function: heal

**Parameters**: self
**Returns**: dict
**Description**: heal() not implemented for CachedStateLedgerAgent.



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Usage Examples

### Class Usage

```python
# Using CachedStateLedger
cachedstateledger = CachedStateLedger()
cachedstateledger.cache_validation_context()
cachedstateledger.get_cached_validation_context()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, session_id)
```

```python
# Using cache_validation_context
result = cache_validation_context(key, context)
```

```python
# Using get_cached_validation_context
result = get_cached_validation_context(key)
```



---
**Generated**: 2026-03-26T09:39:04.610920
**Type**: api_reference
**Quality**: comprehensive
