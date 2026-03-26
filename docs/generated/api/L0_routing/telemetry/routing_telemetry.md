# API Documentation: routing_telemetry

**Target Audience**: developers, api_users

# routing_telemetry API Documentation

**File**: `routing_telemetry.py`
**Classes**: 5
**Functions**: 19

## Classes

- **RoutingOutcomeStatus** (inherits from str, Enum)
- **NullMetricReason** (inherits from str, Enum)
- **RoutingTelemetry**
- **RoutingTelemetryContext**
- **RoutingTelemetryStore**

## Functions

- **record_routing_telemetry** -> RoutingTelemetry
- **get_routing_telemetry_store** -> RoutingTelemetryStore
- **reset_routing_telemetry_store** -> None
- **_resolve_trace_id** -> str
- **_resolve_run_id** -> str
- **_persist_telemetry** -> None
- **create** -> RoutingTelemetry
- **__init__** -> None
- **ingest** -> None
- **by_run_id** -> list[RoutingTelemetry]
- **by_trace_id** -> list[RoutingTelemetry]
- **by_contract_id** -> list[RoutingTelemetry]
- **by_outcome** -> list[RoutingTelemetry]
- **all_records** -> list[RoutingTelemetry]
- **record_count** -> int
- **records_without_duration** -> list[RoutingTelemetry]
- **records_without_outcome** -> list[RoutingTelemetry]
- **records_with_silent_null** -> list[RoutingTelemetry]
- **average_duration_ms** -> float


## Class: RoutingOutcomeStatus

**Description**: Classification of a routing decision outcome.

    Every RoutingTelemetry record must bind to exactly one of these.
    

**Inherits from**: str, Enum



## Class: NullMetricReason

**Description**: Reason why a load or queue metric is unavailable.

    Per spec §4: if a load metric is unavailable, emit an explicit null-metric
    reason rather than silently omitting the field.
    

**Inherits from**: str, Enum



## Class: RoutingTelemetry

**Description**: Immutable telemetry artifact for one routing decision (P2/L0 spec §2).

    All 15 fields are required. Fields that cannot be measured must carry
    an explicit NullMetricReason value rather than being omitted or None.
    

### Methods

#### create
**Parameters**: cls, run_id, trace_id, routing_contract_id, router_id, request_hash, candidate_route_count, chosen_route, routing_start_tick, routing_end_tick, routing_outcome_status, queue_depth_snapshot, target_load_snapshot, routing_failure_reason
**Returns**: RoutingTelemetry



## Class: RoutingTelemetryContext

**Description**: All inputs required to emit a RoutingTelemetry record.

    Callers must populate router_id, routing_contract_id, request_hash,
    candidate_routes, chosen_route, and outcome. Optional timing fields
    default to the current clock if not supplied.
    



## Class: RoutingTelemetryStore

**Description**: Queryable in-memory store for all emitted RoutingTelemetry records.

    Per spec §4: routing telemetry must be queryable by:
    - run_id
    - trace_id
    - routing_contract_id
    - routing_outcome_status
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### ingest
**Parameters**: self, record
**Returns**: None

#### by_run_id
**Parameters**: self, run_id
**Returns**: list[RoutingTelemetry]

#### by_trace_id
**Parameters**: self, trace_id
**Returns**: list[RoutingTelemetry]

#### by_contract_id
**Parameters**: self, routing_contract_id
**Returns**: list[RoutingTelemetry]

#### by_outcome
**Parameters**: self, outcome
**Returns**: list[RoutingTelemetry]

#### all_records
**Parameters**: self
**Returns**: list[RoutingTelemetry]

#### record_count
**Parameters**: self
**Returns**: int

#### records_without_duration
**Parameters**: self
**Returns**: list[RoutingTelemetry]
**Description**: Return records with routing_duration_ms == 0 (missing timing).

#### records_without_outcome
**Parameters**: self
**Returns**: list[RoutingTelemetry]
**Description**: Return records with no outcome status set.

#### records_with_silent_null
**Parameters**: self
**Returns**: list[RoutingTelemetry]
**Description**: Return records where queue/load are Python None (silent omission, prohibited).

#### average_duration_ms
**Parameters**: self
**Returns**: float



## Function: record_routing_telemetry

**Parameters**: routing_context
**Returns**: RoutingTelemetry
**Description**: Mandatory routing telemetry entrypoint — P2/L0 spec §3.

    Steps (in order, all mandatory):
      1. capture start and end timing
      2. attach queue / load snapshot if available (explicit null if not)
      3. bind telemetry to routing contract and trace
      4. emit routing outcome status
      5. persist telemetry artifact

    Args:
        routing_context:  Fully-populated RoutingTelemetryContext.

    Returns:
        RoutingTelemetry (immutable, 15 fields), persisted to the store.
    



## Function: get_routing_telemetry_store

**Returns**: RoutingTelemetryStore
**Description**: Return the process-level RoutingTelemetryStore singleton.



## Function: reset_routing_telemetry_store

**Returns**: None
**Description**: Reset the global store (for testing).



## Function: _resolve_trace_id

**Returns**: str


## Function: _resolve_run_id

**Returns**: str


## Function: _persist_telemetry

**Parameters**: record
**Returns**: None


## Function: create

**Parameters**: cls, run_id, trace_id, routing_contract_id, router_id, request_hash, candidate_route_count, chosen_route, routing_start_tick, routing_end_tick, routing_outcome_status, queue_depth_snapshot, target_load_snapshot, routing_failure_reason
**Returns**: RoutingTelemetry


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: ingest

**Parameters**: self, record
**Returns**: None


## Function: by_run_id

**Parameters**: self, run_id
**Returns**: list[RoutingTelemetry]


## Function: by_trace_id

**Parameters**: self, trace_id
**Returns**: list[RoutingTelemetry]


## Function: by_contract_id

**Parameters**: self, routing_contract_id
**Returns**: list[RoutingTelemetry]


## Function: by_outcome

**Parameters**: self, outcome
**Returns**: list[RoutingTelemetry]


## Function: all_records

**Parameters**: self
**Returns**: list[RoutingTelemetry]


## Function: record_count

**Parameters**: self
**Returns**: int


## Function: records_without_duration

**Parameters**: self
**Returns**: list[RoutingTelemetry]
**Description**: Return records with routing_duration_ms == 0 (missing timing).



## Function: records_without_outcome

**Parameters**: self
**Returns**: list[RoutingTelemetry]
**Description**: Return records with no outcome status set.



## Function: records_with_silent_null

**Parameters**: self
**Returns**: list[RoutingTelemetry]
**Description**: Return records where queue/load are Python None (silent omission, prohibited).



## Function: average_duration_ms

**Parameters**: self
**Returns**: float


## Usage Examples

### Class Usage

```python
# Using RoutingOutcomeStatus
routingoutcomestatus = RoutingOutcomeStatus()
```

```python
# Using NullMetricReason
nullmetricreason = NullMetricReason()
```

```python
# Using RoutingTelemetry
routingtelemetry = RoutingTelemetry()
routingtelemetry.create()
```

### Function Usage

```python
# Using record_routing_telemetry
result = record_routing_telemetry(routing_context)
```

```python
# Using get_routing_telemetry_store
result = get_routing_telemetry_store()
```

```python
# Using reset_routing_telemetry_store
result = reset_routing_telemetry_store()
```



---
**Generated**: 2026-03-26T09:39:03.418666
**Type**: api_reference
**Quality**: comprehensive
