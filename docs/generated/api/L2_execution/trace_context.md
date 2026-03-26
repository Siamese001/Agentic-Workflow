# API Documentation: trace_context

**Target Audience**: developers, api_users

# trace_context API Documentation

**File**: `trace_context.py`
**Classes**: 2
**Functions**: 14

## Classes

- **TraceEntry**
- **TraceContext**

## Functions

- **_get_noop_context** -> TraceContext
- **get_trace_context** -> TraceContext
- **_set_trace_context** -> TraceContext | None
- **to_dict** -> dict[str, Any]
- **__init__** -> None
- **record** -> TraceEntry
- **record_clock** -> None
- **entries** -> list[TraceEntry]
- **entry_count** -> int
- **sign** -> str
- **signed_digest** -> str
- **assert_transcripted** -> None
- **get_stats** -> dict[str, Any]
- **run_frame** -> Generator[TraceContext, None, None]


## Class: TraceEntry

**Description**: Single execution trace record produced by a chokepoint.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: TraceContext

**Description**: Thread-safe, append-only execution trace for a single run.

    Chokepoints call ``record()`` to append entries.  After the run completes,
    call ``sign()`` to produce a determinism digest covering all entries.

    Instances are scoped to a run via ``run_frame()`` context manager, which
    sets/restores the process-level singleton so that ``get_trace_context()``
    always returns the correct context without explicit threading.
    

### Methods

#### __init__
**Parameters**: self, run_id
**Returns**: None

#### record
**Parameters**: self, layer, module, operation, trace_id, elapsed_ms, success, metadata
**Returns**: TraceEntry
**Description**: Append a trace entry.  ADG edge: ``records_execution_trace``.

#### record_clock
**Parameters**: self, clock_value
**Returns**: None
**Description**: Hook for ClockProvider.WallClock to record its value into the trace.

#### entries
**Parameters**: self
**Returns**: list[TraceEntry]
**Description**: Return a snapshot copy of all trace entries.

#### entry_count
**Parameters**: self
**Returns**: int

#### sign
**Parameters**: self
**Returns**: str
**Description**: Seal the trace and return a determinism digest.

        ADG edge: ``signs_execution_trace``.
        

#### signed_digest
**Parameters**: self
**Returns**: str

#### assert_transcripted
**Parameters**: self, operation, module
**Returns**: None
**Description**: Assert that at least one trace entry exists for ``operation``.

        If not found, emits ``hard_fails_untranscripted`` and raises.

        ADG edge: ``hard_fails_untranscripted``.
        

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return coverage statistics for this trace context.

#### run_frame
**Parameters**: cls, run_id
**Returns**: Generator[TraceContext, None, None]
**Description**: Context manager that installs this context as the process singleton.

        On exit, the previous context is restored (supports nested frames).
        



## Function: _get_noop_context

**Returns**: TraceContext


## Function: get_trace_context

**Returns**: TraceContext
**Description**: Return the active TraceContext for this thread.

    Returns a no-op context (entries are discarded) if no run frame is active.
    



## Function: _set_trace_context

**Parameters**: ctx
**Returns**: TraceContext | None
**Description**: Install ctx as the thread-local context, return the previous one.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __init__

**Parameters**: self, run_id
**Returns**: None


## Function: record

**Parameters**: self, layer, module, operation, trace_id, elapsed_ms, success, metadata
**Returns**: TraceEntry
**Description**: Append a trace entry.  ADG edge: ``records_execution_trace``.



## Function: record_clock

**Parameters**: self, clock_value
**Returns**: None
**Description**: Hook for ClockProvider.WallClock to record its value into the trace.



## Function: entries

**Parameters**: self
**Returns**: list[TraceEntry]
**Description**: Return a snapshot copy of all trace entries.



## Function: entry_count

**Parameters**: self
**Returns**: int


## Function: sign

**Parameters**: self
**Returns**: str
**Description**: Seal the trace and return a determinism digest.

        ADG edge: ``signs_execution_trace``.
        



## Function: signed_digest

**Parameters**: self
**Returns**: str


## Function: assert_transcripted

**Parameters**: self, operation, module
**Returns**: None
**Description**: Assert that at least one trace entry exists for ``operation``.

        If not found, emits ``hard_fails_untranscripted`` and raises.

        ADG edge: ``hard_fails_untranscripted``.
        



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return coverage statistics for this trace context.



## Function: run_frame

**Parameters**: cls, run_id
**Returns**: Generator[TraceContext, None, None]
**Description**: Context manager that installs this context as the process singleton.

        On exit, the previous context is restored (supports nested frames).
        



## Usage Examples

### Class Usage

```python
# Using TraceEntry
traceentry = TraceEntry()
traceentry.to_dict()
```

```python
# Using TraceContext
tracecontext = TraceContext()
tracecontext.record()
tracecontext.record_clock()
```

### Function Usage

```python
# Using _get_noop_context
result = _get_noop_context()
```

```python
# Using get_trace_context
result = get_trace_context()
```

```python
# Using _set_trace_context
result = _set_trace_context(ctx)
```



---
**Generated**: 2026-03-26T09:39:03.585962
**Type**: api_reference
**Quality**: comprehensive
