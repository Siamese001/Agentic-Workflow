# API Documentation: execution_adaptation

**Target Audience**: developers, api_users

# execution_adaptation API Documentation

**File**: `execution_adaptation.py`
**Classes**: 3
**Functions**: 23

## Classes

- **ExecutionAdaptationError** (inherits from Exception)
- **ExecutionAdaptationRecord**
- **ExecutionAdaptationRegistry**

## Functions

- **get_execution_adaptation_registry** -> ExecutionAdaptationRegistry
- **reset_execution_adaptation_registry** -> None
- **create** -> ExecutionAdaptationRecord
- **has_historical_metrics** -> bool
- **has_trace_record** -> bool
- **has_strategy_evaluation** -> bool
- **is_safe_strategy** -> bool
- **has_policy_compliance** -> bool
- **__init__** -> None
- **get_instance** -> ExecutionAdaptationRegistry
- **persist_adaptation** -> None
- **query_adaptation_by_id** -> ExecutionAdaptationRecord | None
- **query_adaptations_by_strategy_hash** -> list[ExecutionAdaptationRecord]
- **query_adaptations_by_run_id** -> list[ExecutionAdaptationRecord]
- **query_adaptations_by_trace_id** -> list[ExecutionAdaptationRecord]
- **query_adaptations_by_success_rate** -> list[ExecutionAdaptationRecord]
- **get_latest_adaptations** -> list[ExecutionAdaptationRecord]
- **get_adaptation_count** -> int
- **verify_historical_metrics** -> bool
- **verify_strategy_evaluation** -> bool
- **verify_trace_record** -> bool
- **verify_safe_strategy** -> bool
- **verify_policy_compliance** -> bool


## Class: ExecutionAdaptationError

**Description**: Raised when execution adaptation operations fail (Gate A/D).

**Inherits from**: Exception



## Class: ExecutionAdaptationRecord

**Description**: Immutable execution adaptation record for strategy adaptation (9 required fields).

### Methods

#### create
**Parameters**: cls, execution_adaptation_id, run_id, trace_id, execution_strategy_hash, historical_success_rate, historical_failure_rate, latency_profile_hash, chosen_strategy_hash, adaptation_reason_hash
**Returns**: ExecutionAdaptationRecord
**Description**: Factory to create ExecutionAdaptationRecord with default values.

#### has_historical_metrics
**Parameters**: self
**Returns**: bool
**Description**: Check if adaptation has historical metrics (Gate A).

#### has_trace_record
**Parameters**: self
**Returns**: bool
**Description**: Check if adaptation has trace record (Gate C).

#### has_strategy_evaluation
**Parameters**: self
**Returns**: bool
**Description**: Check if strategy has evaluation score (Gate B).

#### is_safe_strategy
**Parameters**: self
**Returns**: bool
**Description**: Check if strategy is safe (Gate D).

#### has_policy_compliance
**Parameters**: self
**Returns**: bool
**Description**: Check if adaptation has policy compliance (Gate E).



## Class: ExecutionAdaptationRegistry

**Description**: Thread-safe registry for execution adaptation records.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_instance
**Parameters**: cls
**Returns**: ExecutionAdaptationRegistry
**Description**: Singleton accessor.

#### persist_adaptation
**Parameters**: self, adaptation
**Returns**: None
**Description**: Persist an execution adaptation record.

#### query_adaptation_by_id
**Parameters**: self, adaptation_id
**Returns**: ExecutionAdaptationRecord | None
**Description**: Query execution adaptation by ID.

#### query_adaptations_by_strategy_hash
**Parameters**: self, strategy_hash
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by strategy hash.

#### query_adaptations_by_run_id
**Parameters**: self, run_id
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by run ID.

#### query_adaptations_by_trace_id
**Parameters**: self, trace_id
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by trace ID.

#### query_adaptations_by_success_rate
**Parameters**: self, min_success_rate
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by minimum success rate.

#### get_latest_adaptations
**Parameters**: self, limit
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Get latest execution adaptations.

#### get_adaptation_count
**Parameters**: self
**Returns**: int
**Description**: Get count of execution adaptations.

#### verify_historical_metrics
**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has historical metrics (Gate A).

#### verify_strategy_evaluation
**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has strategy evaluation (Gate B).

#### verify_trace_record
**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has trace record (Gate C).

#### verify_safe_strategy
**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify strategy is safe (Gate D).

#### verify_policy_compliance
**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has policy compliance (Gate E).



## Function: get_execution_adaptation_registry

**Returns**: ExecutionAdaptationRegistry
**Description**: Get the singleton ExecutionAdaptationRegistry instance.



## Function: reset_execution_adaptation_registry

**Returns**: None
**Description**: Reset the singleton ExecutionAdaptationRegistry (for testing).



## Function: create

**Parameters**: cls, execution_adaptation_id, run_id, trace_id, execution_strategy_hash, historical_success_rate, historical_failure_rate, latency_profile_hash, chosen_strategy_hash, adaptation_reason_hash
**Returns**: ExecutionAdaptationRecord
**Description**: Factory to create ExecutionAdaptationRecord with default values.



## Function: has_historical_metrics

**Parameters**: self
**Returns**: bool
**Description**: Check if adaptation has historical metrics (Gate A).



## Function: has_trace_record

**Parameters**: self
**Returns**: bool
**Description**: Check if adaptation has trace record (Gate C).



## Function: has_strategy_evaluation

**Parameters**: self
**Returns**: bool
**Description**: Check if strategy has evaluation score (Gate B).



## Function: is_safe_strategy

**Parameters**: self
**Returns**: bool
**Description**: Check if strategy is safe (Gate D).



## Function: has_policy_compliance

**Parameters**: self
**Returns**: bool
**Description**: Check if adaptation has policy compliance (Gate E).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_instance

**Parameters**: cls
**Returns**: ExecutionAdaptationRegistry
**Description**: Singleton accessor.



## Function: persist_adaptation

**Parameters**: self, adaptation
**Returns**: None
**Description**: Persist an execution adaptation record.



## Function: query_adaptation_by_id

**Parameters**: self, adaptation_id
**Returns**: ExecutionAdaptationRecord | None
**Description**: Query execution adaptation by ID.



## Function: query_adaptations_by_strategy_hash

**Parameters**: self, strategy_hash
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by strategy hash.



## Function: query_adaptations_by_run_id

**Parameters**: self, run_id
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by run ID.



## Function: query_adaptations_by_trace_id

**Parameters**: self, trace_id
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by trace ID.



## Function: query_adaptations_by_success_rate

**Parameters**: self, min_success_rate
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Query execution adaptations by minimum success rate.



## Function: get_latest_adaptations

**Parameters**: self, limit
**Returns**: list[ExecutionAdaptationRecord]
**Description**: Get latest execution adaptations.



## Function: get_adaptation_count

**Parameters**: self
**Returns**: int
**Description**: Get count of execution adaptations.



## Function: verify_historical_metrics

**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has historical metrics (Gate A).



## Function: verify_strategy_evaluation

**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has strategy evaluation (Gate B).



## Function: verify_trace_record

**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has trace record (Gate C).



## Function: verify_safe_strategy

**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify strategy is safe (Gate D).



## Function: verify_policy_compliance

**Parameters**: self, adaptation_id
**Returns**: bool
**Description**: Verify adaptation has policy compliance (Gate E).



## Usage Examples

### Class Usage

```python
# Using ExecutionAdaptationError
executionadaptationerror = ExecutionAdaptationError()
```

```python
# Using ExecutionAdaptationRecord
executionadaptationrecord = ExecutionAdaptationRecord()
executionadaptationrecord.create()
executionadaptationrecord.has_historical_metrics()
```

```python
# Using ExecutionAdaptationRegistry
executionadaptationregistry = ExecutionAdaptationRegistry()
executionadaptationregistry.get_instance()
executionadaptationregistry.persist_adaptation()
```

### Function Usage

```python
# Using get_execution_adaptation_registry
result = get_execution_adaptation_registry()
```

```python
# Using reset_execution_adaptation_registry
result = reset_execution_adaptation_registry()
```

```python
# Using create
result = create(cls, execution_adaptation_id)
```



---
**Generated**: 2026-03-26T09:39:03.602425
**Type**: api_reference
**Quality**: comprehensive
