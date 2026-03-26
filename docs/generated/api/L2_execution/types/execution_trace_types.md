# API Documentation: execution_trace_types

**Target Audience**: developers, api_users

# execution_trace_types API Documentation

**File**: `execution_trace_types.py`
**Classes**: 2
**Functions**: 16

## Classes

- **ExecutionTrace**
- **ExecutionTraceBuilder**

## Functions

- **_compute_replay_key** -> str
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **content_hash** -> str
- **validate_completeness** -> None
- **__init__** -> None
- **set_governed_payload** -> None
- **add_sandbox_envelope** -> None
- **set_llm_response** -> None
- **set_transcript** -> None
- **set_policy_hash** -> None
- **set_prev_hash** -> None
- **set_validation_decision** -> None
- **set_hash_chain_root** -> None
- **set_timing** -> None
- **seal** -> ExecutionTrace


## Class: ExecutionTrace

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes

#### content_hash
**Parameters**: self
**Returns**: str

#### validate_completeness
**Parameters**: self
**Returns**: None
**Description**: Addendum 1.1: Raise ExecutionTraceIntegrityError if any required field is empty.

        Required fields: trace_id, instruction_packet_id, governed_payload_hash,
        llm_response_hash, validation_decision, hash_chain_root, replay_key.
        



## Class: ExecutionTraceBuilder

**Description**: Mutable builder. Call seal() exactly once.

### Methods

#### __init__
**Parameters**: self, trace_id, instruction_packet_id
**Returns**: None

#### set_governed_payload
**Parameters**: self, routing_hash
**Returns**: None

#### add_sandbox_envelope
**Parameters**: self, envelope_id
**Returns**: None

#### set_llm_response
**Parameters**: self, raw_text
**Returns**: None

#### set_transcript
**Parameters**: self, transcript_bytes
**Returns**: None
**Description**: Set transcript_hash from raw PTC ToolTranscript bytes.

#### set_policy_hash
**Parameters**: self, policy_hash
**Returns**: None

#### set_prev_hash
**Parameters**: self, prev_hash
**Returns**: None

#### set_validation_decision
**Parameters**: self, decision
**Returns**: None

#### set_hash_chain_root
**Parameters**: self, root
**Returns**: None

#### set_timing
**Parameters**: self, ms
**Returns**: None

#### seal
**Parameters**: self
**Returns**: ExecutionTrace



## Function: _compute_replay_key

**Parameters**: trace_id, plan_hash, transcript_hash
**Returns**: str


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes


## Function: content_hash

**Parameters**: self
**Returns**: str


## Function: validate_completeness

**Parameters**: self
**Returns**: None
**Description**: Addendum 1.1: Raise ExecutionTraceIntegrityError if any required field is empty.

        Required fields: trace_id, instruction_packet_id, governed_payload_hash,
        llm_response_hash, validation_decision, hash_chain_root, replay_key.
        



## Function: __init__

**Parameters**: self, trace_id, instruction_packet_id
**Returns**: None


## Function: set_governed_payload

**Parameters**: self, routing_hash
**Returns**: None


## Function: add_sandbox_envelope

**Parameters**: self, envelope_id
**Returns**: None


## Function: set_llm_response

**Parameters**: self, raw_text
**Returns**: None


## Function: set_transcript

**Parameters**: self, transcript_bytes
**Returns**: None
**Description**: Set transcript_hash from raw PTC ToolTranscript bytes.



## Function: set_policy_hash

**Parameters**: self, policy_hash
**Returns**: None


## Function: set_prev_hash

**Parameters**: self, prev_hash
**Returns**: None


## Function: set_validation_decision

**Parameters**: self, decision
**Returns**: None


## Function: set_hash_chain_root

**Parameters**: self, root
**Returns**: None


## Function: set_timing

**Parameters**: self, ms
**Returns**: None


## Function: seal

**Parameters**: self
**Returns**: ExecutionTrace


## Usage Examples

### Class Usage

```python
# Using ExecutionTrace
executiontrace = ExecutionTrace()
executiontrace.canonical_bytes()
executiontrace.content_hash()
```

```python
# Using ExecutionTraceBuilder
executiontracebuilder = ExecutionTraceBuilder()
executiontracebuilder.set_governed_payload()
executiontracebuilder.add_sandbox_envelope()
```

### Function Usage

```python
# Using _compute_replay_key
result = _compute_replay_key(trace_id, plan_hash)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using canonical_bytes
result = canonical_bytes()
```



---
**Generated**: 2026-03-26T09:39:03.958509
**Type**: api_reference
**Quality**: comprehensive
