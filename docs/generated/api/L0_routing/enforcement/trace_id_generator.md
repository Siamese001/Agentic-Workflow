# API Documentation: trace_id_generator

**Target Audience**: developers, api_users

# trace_id_generator API Documentation

**File**: `trace_id_generator.py`
**Classes**: 1
**Functions**: 6

## Classes

- **TraceIdGenerator**

## Functions

- **generate_trace_id** -> str
- **validate_trace_id** -> bool
- **__init__**
- **generate_trace_id** -> str
- **validate_trace_id** -> bool
- **is_replay_deterministic** -> bool


## Class: TraceIdGenerator

**Description**: Generates deterministic TraceIDs with replay support.

### Methods

#### __init__
**Parameters**: self, replay_mode
**Description**: Initialize generator.

        Args:
            replay_mode: If True, generates deterministic IDs for replay
        

#### generate_trace_id
**Parameters**: self, semantic_clock, operation, additional_context
**Returns**: str
**Description**: Generate a deterministic TraceID.

        Args:
            semantic_clock: Current semantic clock snapshot
            operation: Operation being performed
            additional_context: Optional additional context for uniqueness

        Returns:
            TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
        

#### validate_trace_id
**Parameters**: self, trace_id
**Returns**: bool
**Description**: Validate TraceID matches required pattern.

        Args:
            trace_id: TraceID to validate

        Returns:
            True if valid, False otherwise
        

#### is_replay_deterministic
**Parameters**: self, trace_id1, trace_id2, semantic_clock, operation, additional_context
**Returns**: bool
**Description**: Check if two TraceIDs would be deterministic under same conditions.

        Args:
            trace_id1: First TraceID
            trace_id2: Second TraceID
            semantic_clock: Semantic clock snapshot
            operation: Operation being performed
            additional_context: Additional context

        Returns:
            True if IDs would be deterministic under same conditions
        



## Function: generate_trace_id

**Parameters**: semantic_clock, operation, additional_context, replay_mode
**Returns**: str
**Description**: Generate a TraceID.

    Args:
        semantic_clock: Current semantic clock snapshot
        operation: Operation being performed
        additional_context: Optional additional context
        replay_mode: If True, generates deterministic ID for replay

    Returns:
        TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
    



## Function: validate_trace_id

**Parameters**: trace_id
**Returns**: bool
**Description**: Validate TraceID matches required pattern.

    Args:
        trace_id: TraceID to validate

    Returns:
        True if valid, False otherwise
    



## Function: __init__

**Parameters**: self, replay_mode
**Description**: Initialize generator.

        Args:
            replay_mode: If True, generates deterministic IDs for replay
        



## Function: generate_trace_id

**Parameters**: self, semantic_clock, operation, additional_context
**Returns**: str
**Description**: Generate a deterministic TraceID.

        Args:
            semantic_clock: Current semantic clock snapshot
            operation: Operation being performed
            additional_context: Optional additional context for uniqueness

        Returns:
            TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
        



## Function: validate_trace_id

**Parameters**: self, trace_id
**Returns**: bool
**Description**: Validate TraceID matches required pattern.

        Args:
            trace_id: TraceID to validate

        Returns:
            True if valid, False otherwise
        



## Function: is_replay_deterministic

**Parameters**: self, trace_id1, trace_id2, semantic_clock, operation, additional_context
**Returns**: bool
**Description**: Check if two TraceIDs would be deterministic under same conditions.

        Args:
            trace_id1: First TraceID
            trace_id2: Second TraceID
            semantic_clock: Semantic clock snapshot
            operation: Operation being performed
            additional_context: Additional context

        Returns:
            True if IDs would be deterministic under same conditions
        



## Usage Examples

### Class Usage

```python
# Using TraceIdGenerator
traceidgenerator = TraceIdGenerator()
traceidgenerator.generate_trace_id()
traceidgenerator.validate_trace_id()
```

### Function Usage

```python
# Using generate_trace_id
result = generate_trace_id(semantic_clock, operation)
```

```python
# Using validate_trace_id
result = validate_trace_id(trace_id)
```

```python
# Using __init__
result = __init__(replay_mode)
```



---
**Generated**: 2026-03-26T09:39:02.642022
**Type**: api_reference
**Quality**: comprehensive
