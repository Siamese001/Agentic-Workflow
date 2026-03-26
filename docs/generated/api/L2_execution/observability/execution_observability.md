# API Documentation: execution_observability

**Target Audience**: developers, api_users

# execution_observability API Documentation

**File**: `execution_observability.py`
**Classes**: 5
**Functions**: 17

## Classes

- **ExecutionStatus** (inherits from Enum)
- **FailureClassification** (inherits from Enum)
- **ExecutionObservabilityError** (inherits from Exception)
- **ExecutionObservabilityRecord**
- **ObservabilityRegistry**

## Functions

- **get_observability_registry** -> ObservabilityRegistry
- **reset_observability_registry** -> None
- **create** -> ExecutionObservabilityRecord
- **has_duration** -> bool
- **has_failure_classification** -> bool
- **has_retry_metadata** -> bool
- **has_policy_linkage** -> bool
- **__init__** -> None
- **get_instance** -> ObservabilityRegistry
- **persist_record** -> None
- **query_by_run_id** -> list[ExecutionObservabilityRecord]
- **query_by_trace_id** -> list[ExecutionObservabilityRecord]
- **query_by_status** -> list[ExecutionObservabilityRecord]
- **query_by_record_id** -> ExecutionObservabilityRecord | None
- **get_record_count** -> int
- **verify_record_exists** -> bool
- **verify_duration_present** -> bool


## Class: ExecutionStatus

**Description**: Status of execution operations.

**Inherits from**: Enum



## Class: FailureClassification

**Description**: Classification of execution failures.

**Inherits from**: Enum



## Class: ExecutionObservabilityError

**Description**: Raised when governed runtime execution completes without observability record (Gate A).

**Inherits from**: Exception



## Class: ExecutionObservabilityRecord

**Description**: Immutable execution observability record for operational telemetry (14 required fields).

### Methods

#### create
**Parameters**: cls, run_id, trace_id, execution_request_id, execution_target, execution_start_tick, execution_end_tick, execution_status, retry_count, retry_reason, failure_reason, guardrail_decision_id, policy_hash
**Returns**: ExecutionObservabilityRecord
**Description**: Factory to create ExecutionObservabilityRecord with computed fields.

#### has_duration
**Parameters**: self
**Returns**: bool
**Description**: Check if record has duration_ms (Gate B).

#### has_failure_classification
**Parameters**: self
**Returns**: bool
**Description**: Check if failed execution has failure classification (Gate C).

#### has_retry_metadata
**Parameters**: self
**Returns**: bool
**Description**: Check if retried execution has retry metadata (Gate D).

#### has_policy_linkage
**Parameters**: self
**Returns**: bool
**Description**: Check if blocked execution has policy linkage (Gate E).



## Class: ObservabilityRegistry

**Description**: Thread-safe registry for execution observability records and queries.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: ObservabilityRegistry
**Description**: Singleton accessor.

#### persist_record
**Parameters**: self, record
**Returns**: None
**Description**: Persist an execution observability record.

#### query_by_run_id
**Parameters**: self, run_id
**Returns**: list[ExecutionObservabilityRecord]
**Description**: Query execution observability records by run_id.

#### query_by_trace_id
**Parameters**: self, trace_id
**Returns**: list[ExecutionObservabilityRecord]
**Description**: Query execution observability records by trace_id.

#### query_by_status
**Parameters**: self, status
**Returns**: list[ExecutionObservabilityRecord]
**Description**: Query execution observability records by status.

#### query_by_record_id
**Parameters**: self, record_id
**Returns**: ExecutionObservabilityRecord | None
**Description**: Query execution observability record by execution_observability_id.

#### get_record_count
**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of execution observability records, optionally filtered by run_id.

#### verify_record_exists
**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify execution observability record exists (Gate A).

#### verify_duration_present
**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify record has duration_ms (Gate B).



## Function: get_observability_registry

**Returns**: ObservabilityRegistry
**Description**: Get the singleton ObservabilityRegistry instance.



## Function: reset_observability_registry

**Returns**: None
**Description**: Reset the singleton ObservabilityRegistry (for testing).



## Function: create

**Parameters**: cls, run_id, trace_id, execution_request_id, execution_target, execution_start_tick, execution_end_tick, execution_status, retry_count, retry_reason, failure_reason, guardrail_decision_id, policy_hash
**Returns**: ExecutionObservabilityRecord
**Description**: Factory to create ExecutionObservabilityRecord with computed fields.



## Function: has_duration

**Parameters**: self
**Returns**: bool
**Description**: Check if record has duration_ms (Gate B).



## Function: has_failure_classification

**Parameters**: self
**Returns**: bool
**Description**: Check if failed execution has failure classification (Gate C).



## Function: has_retry_metadata

**Parameters**: self
**Returns**: bool
**Description**: Check if retried execution has retry metadata (Gate D).



## Function: has_policy_linkage

**Parameters**: self
**Returns**: bool
**Description**: Check if blocked execution has policy linkage (Gate E).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: ObservabilityRegistry
**Description**: Singleton accessor.



## Function: persist_record

**Parameters**: self, record
**Returns**: None
**Description**: Persist an execution observability record.



## Function: query_by_run_id

**Parameters**: self, run_id
**Returns**: list[ExecutionObservabilityRecord]
**Description**: Query execution observability records by run_id.



## Function: query_by_trace_id

**Parameters**: self, trace_id
**Returns**: list[ExecutionObservabilityRecord]
**Description**: Query execution observability records by trace_id.



## Function: query_by_status

**Parameters**: self, status
**Returns**: list[ExecutionObservabilityRecord]
**Description**: Query execution observability records by status.



## Function: query_by_record_id

**Parameters**: self, record_id
**Returns**: ExecutionObservabilityRecord | None
**Description**: Query execution observability record by execution_observability_id.



## Function: get_record_count

**Parameters**: self, run_id
**Returns**: int
**Description**: Get count of execution observability records, optionally filtered by run_id.



## Function: verify_record_exists

**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify execution observability record exists (Gate A).



## Function: verify_duration_present

**Parameters**: self, record_id
**Returns**: bool
**Description**: Verify record has duration_ms (Gate B).



## Usage Examples

### Class Usage

```python
# Using ExecutionStatus
executionstatus = ExecutionStatus()
```

```python
# Using FailureClassification
failureclassification = FailureClassification()
```

```python
# Using ExecutionObservabilityError
executionobservabilityerror = ExecutionObservabilityError()
```

### Function Usage

```python
# Using get_observability_registry
result = get_observability_registry()
```

```python
# Using reset_observability_registry
result = reset_observability_registry()
```

```python
# Using create
result = create(cls, run_id)
```



---
**Generated**: 2026-03-26T09:39:03.858016
**Type**: api_reference
**Quality**: comprehensive
