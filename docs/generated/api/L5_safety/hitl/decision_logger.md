# API Documentation: decision_logger

**Target Audience**: developers, api_users

# decision_logger API Documentation

**File**: `decision_logger.py`
**Classes**: 2
**Functions**: 7

## Classes

- **HITLDecision**
- **HITLDecisionLogger**

## Functions

- **get_decision_logger** -> HITLDecisionLogger
- **to_log_line** -> str
- **to_jsonl** -> str
- **__init__** -> None
- **log** -> HITLDecision
- **all_records** -> list[HITLDecision]
- **count** -> int


## Class: HITLDecision

**Description**: Single HITL decision record. No timestamps in key fields.

### Methods

#### to_log_line
**Parameters**: self
**Returns**: str
**Description**: Format as the canonical HITL_DECISION_N line.

#### to_jsonl
**Parameters**: self
**Returns**: str



## Class: HITLDecisionLogger

**Description**: Logger for HITL decisions using deterministic format.

### Methods

#### __init__
**Parameters**: self, log_path
**Returns**: None

#### log
**Parameters**: self, agent, file, violation, proposed, decision, reviewer_signature, metadata
**Returns**: HITLDecision
**Description**: Log a HITL decision. Returns the created record.

#### all_records
**Parameters**: self
**Returns**: list[HITLDecision]

#### count
**Parameters**: self
**Returns**: int



## Function: get_decision_logger

**Parameters**: path
**Returns**: HITLDecisionLogger


## Function: to_log_line

**Parameters**: self
**Returns**: str
**Description**: Format as the canonical HITL_DECISION_N line.



## Function: to_jsonl

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, log_path
**Returns**: None


## Function: log

**Parameters**: self, agent, file, violation, proposed, decision, reviewer_signature, metadata
**Returns**: HITLDecision
**Description**: Log a HITL decision. Returns the created record.



## Function: all_records

**Parameters**: self
**Returns**: list[HITLDecision]


## Function: count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using HITLDecision
hitldecision = HITLDecision()
hitldecision.to_log_line()
hitldecision.to_jsonl()
```

```python
# Using HITLDecisionLogger
hitldecisionlogger = HITLDecisionLogger()
hitldecisionlogger.log()
hitldecisionlogger.all_records()
```

### Function Usage

```python
# Using get_decision_logger
result = get_decision_logger(path)
```

```python
# Using to_log_line
result = to_log_line()
```

```python
# Using to_jsonl
result = to_jsonl()
```



---
**Generated**: 2026-03-26T09:39:05.010141
**Type**: api_reference
**Quality**: comprehensive
