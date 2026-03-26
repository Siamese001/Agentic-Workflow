# API Documentation: observability_recorder

**Target Audience**: developers, api_users

# observability_recorder API Documentation

**File**: `observability_recorder.py`
**Classes**: 2
**Functions**: 16

## Classes

- **ExecutionObservabilityContext**
- **ExecutionContext**

## Functions

- **execution_observability_emitted** -> None
- **execution_retry_recorded** -> None
- **execution_failure_classified** -> None
- **policy_block_recorded** -> None
- **record_execution_observability** -> ExecutionObservabilityRecord
- **record_execution_retry** -> ExecutionObservabilityRecord
- **record_execution_failure** -> ExecutionObservabilityRecord
- **record_policy_block** -> ExecutionObservabilityRecord
- **query_execution_observability** -> list[ExecutionObservabilityRecord]
- **record_simple_execution** -> ExecutionObservabilityRecord
- **create** -> ExecutionObservabilityContext
- **create** -> ExecutionContext
- **execution_observability_emitted** -> None
- **execution_retry_recorded** -> None
- **execution_failure_classified** -> None
- **policy_block_recorded** -> None


## Class: ExecutionObservabilityContext

**Description**: Context for execution observability recording.

### Methods

#### create
**Parameters**: cls, run_id, trace_id, execution_target, guardrail_decision_id, policy_hash
**Returns**: ExecutionObservabilityContext



## Class: ExecutionContext

**Description**: Context for execution operations.

### Methods

#### create
**Parameters**: cls, execution_request_id, execution_start_tick, execution_end_tick, execution_status, retry_count, retry_reason, failure_reason, failure_classification
**Returns**: ExecutionContext



## Function: execution_observability_emitted

**Parameters**: record_id, run_id, trace_id, status, duration_ms
**Returns**: None
**Description**: ADG edge emitter for execution_observability_emitted.



## Function: execution_retry_recorded

**Parameters**: retry_id, original_id, retry_count, reason
**Returns**: None
**Description**: ADG edge emitter for execution_retry_recorded.



## Function: execution_failure_classified

**Parameters**: record_id, classification, reason
**Returns**: None
**Description**: ADG edge emitter for execution_failure_classified.



## Function: policy_block_recorded

**Parameters**: record_id, policy_hash, block_reason
**Returns**: None
**Description**: ADG edge emitter for policy_block_recorded.



## Function: record_execution_observability

**Parameters**: execution_context, observability_context
**Returns**: ExecutionObservabilityRecord
**Description**: Mandatory entrypoint for execution observability recording — P3/L2 spec §3.

    Steps (in order, all mandatory):
      1. record start/end timing
      2. compute duration
      3. record status
      4. attach retry metadata
      5. attach failure metadata if applicable
      6. bind to trace and policy
      7. persist observability record

    Args:
        execution_context: ExecutionContext with timing and status
        observability_context: ExecutionObservabilityContext with trace binding
        registry: ObservabilityRegistry to use (uses global if None)

    Returns:
        ExecutionObservabilityRecord — the created and persisted observability record

    Raises:
        ExecutionObservabilityError: If observability recording is required but fails (Gate A)
    



## Function: record_execution_retry

**Parameters**: original_record, retry_execution_context
**Returns**: ExecutionObservabilityRecord
**Description**: Record a retry execution with proper metadata.



## Function: record_execution_failure

**Parameters**: execution_context, observability_context, failure_classification, failure_reason
**Returns**: ExecutionObservabilityRecord
**Description**: Record a failed execution with proper classification.



## Function: record_policy_block

**Parameters**: execution_context, observability_context, block_reason
**Returns**: ExecutionObservabilityRecord
**Description**: Record a policy-blocked execution.



## Function: query_execution_observability

**Parameters**: run_id, trace_id, record_id, status
**Returns**: list[ExecutionObservabilityRecord]
**Description**: Query execution observability records.



## Function: record_simple_execution

**Parameters**: run_id, trace_id, execution_target, execution_request_id, start_tick, end_tick, status, policy_hash
**Returns**: ExecutionObservabilityRecord
**Description**: Convenience wrapper for simple execution observability recording.



## Function: create

**Parameters**: cls, run_id, trace_id, execution_target, guardrail_decision_id, policy_hash
**Returns**: ExecutionObservabilityContext


## Function: create

**Parameters**: cls, execution_request_id, execution_start_tick, execution_end_tick, execution_status, retry_count, retry_reason, failure_reason, failure_classification
**Returns**: ExecutionContext


## Function: execution_observability_emitted

**Parameters**: record_id, run_id, trace_id, status, duration_ms
**Returns**: None
**Description**: ADG edge emitter for execution_observability_emitted.



## Function: execution_retry_recorded

**Parameters**: retry_id, original_id, retry_count, reason
**Returns**: None
**Description**: ADG edge emitter for execution_retry_recorded.



## Function: execution_failure_classified

**Parameters**: record_id, classification, reason
**Returns**: None
**Description**: ADG edge emitter for execution_failure_classified.



## Function: policy_block_recorded

**Parameters**: record_id, policy_hash, block_reason
**Returns**: None
**Description**: ADG edge emitter for policy_block_recorded.



## Usage Examples

### Class Usage

```python
# Using ExecutionObservabilityContext
executionobservabilitycontext = ExecutionObservabilityContext()
executionobservabilitycontext.create()
```

```python
# Using ExecutionContext
executioncontext = ExecutionContext()
executioncontext.create()
```

### Function Usage

```python
# Using execution_observability_emitted
result = execution_observability_emitted(record_id, run_id)
```

```python
# Using execution_retry_recorded
result = execution_retry_recorded(retry_id, original_id)
```

```python
# Using execution_failure_classified
result = execution_failure_classified(record_id, classification)
```



---
**Generated**: 2026-03-26T09:39:03.861102
**Type**: api_reference
**Quality**: comprehensive
