# API Documentation: healing_event_emitter

**Target Audience**: developers, api_users

# healing_event_emitter API Documentation

**File**: `healing_event_emitter.py`
**Classes**: 2
**Functions**: 5

## Classes

- **HealingAttemptEvent**
- **HealingEventEmitter**

## Functions

- **get_healing_emitter** -> HealingEventEmitter
- **to_jsonl** -> str
- **__init__** -> None
- **emit** -> HealingAttemptEvent
- **emitted_events** -> list[HealingAttemptEvent]


## Class: HealingAttemptEvent

**Description**: Single healing attempt record.

### Methods

#### to_jsonl
**Parameters**: self
**Returns**: str



## Class: HealingEventEmitter

**Description**: Emitter for healing attempt events.

    Wire into all healing orchestrators (RG, LIC, core).
    

### Methods

#### __init__
**Parameters**: self, log_path
**Returns**: None

#### emit
**Parameters**: self, trace_id, attempt_number, failure_class, healer_selected, model_used, outcome, metadata
**Returns**: HealingAttemptEvent
**Description**: Emit a healing attempt event to the log and in-memory list.

#### emitted_events
**Parameters**: self
**Returns**: list[HealingAttemptEvent]
**Description**: Return all events emitted in this session (in-memory only).



## Function: get_healing_emitter

**Parameters**: path
**Returns**: HealingEventEmitter
**Description**: Return module-level singleton emitter.



## Function: to_jsonl

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, log_path
**Returns**: None


## Function: emit

**Parameters**: self, trace_id, attempt_number, failure_class, healer_selected, model_used, outcome, metadata
**Returns**: HealingAttemptEvent
**Description**: Emit a healing attempt event to the log and in-memory list.



## Function: emitted_events

**Parameters**: self
**Returns**: list[HealingAttemptEvent]
**Description**: Return all events emitted in this session (in-memory only).



## Usage Examples

### Class Usage

```python
# Using HealingAttemptEvent
healingattemptevent = HealingAttemptEvent()
healingattemptevent.to_jsonl()
```

```python
# Using HealingEventEmitter
healingeventemitter = HealingEventEmitter()
healingeventemitter.emit()
healingeventemitter.emitted_events()
```

### Function Usage

```python
# Using get_healing_emitter
result = get_healing_emitter(path)
```

```python
# Using to_jsonl
result = to_jsonl()
```

```python
# Using __init__
result = __init__(log_path)
```



---
**Generated**: 2026-03-26T09:39:03.809335
**Type**: api_reference
**Quality**: comprehensive
