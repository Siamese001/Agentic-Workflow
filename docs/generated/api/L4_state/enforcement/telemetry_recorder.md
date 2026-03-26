# API Documentation: telemetry_recorder

**Target Audience**: developers, api_users

# telemetry_recorder API Documentation

**File**: `telemetry_recorder.py`
**Classes**: 3
**Functions**: 6

## Classes

- **OutcomeRecord**
- **ReconResult**
- **TelemetryRecorder**

## Functions

- **__init__**
- **record** -> str
- **log_async** -> None
- **reconcile** -> ReconResult
- **get_events** -> list[dict[str, Any]]
- **clear** -> None


## Class: OutcomeRecord

**Description**: Immutable outcome record with metrics and reconciliation data.



## Class: ReconResult

**Description**: Reconciliation result between L4 state and actual mutations.



## Class: TelemetryRecorder

**Description**: Durable L4 telemetry recorder with metrics and reconciliation.

    - record(): Store telemetry events with timestamps
    - log_async(): Store outcome records (only after L2.2 commit)
    - reconcile(): Compare L4 state vs actual mutation reality
    

### Methods

#### __init__
**Parameters**: self

#### record
**Parameters**: self, event_type, data, commit_tick, timestamp
**Returns**: str
**Description**: Record a telemetry event.

        Args:
            event_type: Type of telemetry event
            data: Event data payload
            commit_tick: Current commit tick
            timestamp: Optional caller-supplied timestamp (not used in ID derivation)

        Returns:
            Event ID (SHA-256 of event content)
        

#### log_async
**Parameters**: self, record
**Returns**: None
**Description**: Store an outcome record asynchronously.

        Args:
            record: OutcomeRecord to store

        Raises:
            ValueError: If record lacks required l2_commit_hash
        

#### reconcile
**Parameters**: self, l4_state_hash, actual_hash, commit_tick
**Returns**: ReconResult
**Description**: Reconcile L4 state vs actual mutation reality.

        Args:
            l4_state_hash: Expected L4 state hash
            actual_hash: Actual mutation state hash

        Returns:
            ReconResult with mismatch detection
        

#### get_events
**Parameters**: self, event_type, limit
**Returns**: list[dict[str, Any]]
**Description**: Retrieve telemetry events.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of telemetry events
        

#### clear
**Parameters**: self
**Returns**: None
**Description**: Clear all telemetry data (tests only).



## Function: __init__

**Parameters**: self


## Function: record

**Parameters**: self, event_type, data, commit_tick, timestamp
**Returns**: str
**Description**: Record a telemetry event.

        Args:
            event_type: Type of telemetry event
            data: Event data payload
            commit_tick: Current commit tick
            timestamp: Optional caller-supplied timestamp (not used in ID derivation)

        Returns:
            Event ID (SHA-256 of event content)
        



## Function: log_async

**Parameters**: self, record
**Returns**: None
**Description**: Store an outcome record asynchronously.

        Args:
            record: OutcomeRecord to store

        Raises:
            ValueError: If record lacks required l2_commit_hash
        



## Function: reconcile

**Parameters**: self, l4_state_hash, actual_hash, commit_tick
**Returns**: ReconResult
**Description**: Reconcile L4 state vs actual mutation reality.

        Args:
            l4_state_hash: Expected L4 state hash
            actual_hash: Actual mutation state hash

        Returns:
            ReconResult with mismatch detection
        



## Function: get_events

**Parameters**: self, event_type, limit
**Returns**: list[dict[str, Any]]
**Description**: Retrieve telemetry events.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of telemetry events
        



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Clear all telemetry data (tests only).



## Usage Examples

### Class Usage

```python
# Using OutcomeRecord
outcomerecord = OutcomeRecord()
```

```python
# Using ReconResult
reconresult = ReconResult()
```

```python
# Using TelemetryRecorder
telemetryrecorder = TelemetryRecorder()
telemetryrecorder.record()
telemetryrecorder.log_async()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using record
result = record(event_type, data)
```

```python
# Using log_async
result = log_async(record)
```



---
**Generated**: 2026-03-26T09:39:04.523014
**Type**: api_reference
**Quality**: comprehensive
