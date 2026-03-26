# API Documentation: ai_check_audit

**Target Audience**: developers, api_users

# ai_check_audit API Documentation

**File**: `ai_check_audit.py`
**Classes**: 2
**Functions**: 7

## Classes

- **AICheckAuditRecord**
- **AICheckAuditEmitter**

## Functions

- **get_audit_emitter** -> AICheckAuditEmitter
- **to_jsonl** -> str
- **__init__** -> None
- **_hash_input** -> str
- **emit** -> AICheckAuditRecord
- **read_all** -> list[AICheckAuditRecord]
- **check_ci_invariant** -> list[str]


## Class: AICheckAuditRecord

**Description**: Single AI-checking-AI audit record.

### Methods

#### to_jsonl
**Parameters**: self
**Returns**: str



## Class: AICheckAuditEmitter

**Description**: Thread-safe JSONL audit emitter for AI-check decisions.

    Usage:
        emitter = AICheckAuditEmitter()
        emitter.emit(
            component="JudgeEvaluator",
            model_id="gemini-2.5-pro",
            input_data="some input string",
            verdict="PASS",
            confidence=0.92,
            trace_id="abc123",
        )
    

### Methods

#### __init__
**Parameters**: self, audit_path
**Returns**: None

#### _hash_input
**Parameters**: input_data
**Returns**: str
**Description**: Deterministic SHA256 of the input.

#### emit
**Parameters**: self, component, model_id, input_data, verdict, confidence, trace_id, metadata
**Returns**: AICheckAuditRecord
**Description**: Emit a single audit record.

        Automatically sets human_enqueued=True when confidence < 0.7 (C5 rule).
        

#### read_all
**Parameters**: self
**Returns**: list[AICheckAuditRecord]
**Description**: Read all audit records from the JSONL file.

#### check_ci_invariant
**Parameters**: self
**Returns**: list[str]
**Description**: CI: Return violations where confidence < 0.5 AND human_enqueued == False.



## Function: get_audit_emitter

**Parameters**: path
**Returns**: AICheckAuditEmitter
**Description**: Return the module-level default emitter (singleton pattern).



## Function: to_jsonl

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, audit_path
**Returns**: None


## Function: _hash_input

**Parameters**: input_data
**Returns**: str
**Description**: Deterministic SHA256 of the input.



## Function: emit

**Parameters**: self, component, model_id, input_data, verdict, confidence, trace_id, metadata
**Returns**: AICheckAuditRecord
**Description**: Emit a single audit record.

        Automatically sets human_enqueued=True when confidence < 0.7 (C5 rule).
        



## Function: read_all

**Parameters**: self
**Returns**: list[AICheckAuditRecord]
**Description**: Read all audit records from the JSONL file.



## Function: check_ci_invariant

**Parameters**: self
**Returns**: list[str]
**Description**: CI: Return violations where confidence < 0.5 AND human_enqueued == False.



## Usage Examples

### Class Usage

```python
# Using AICheckAuditRecord
aicheckauditrecord = AICheckAuditRecord()
aicheckauditrecord.to_jsonl()
```

```python
# Using AICheckAuditEmitter
aicheckauditemitter = AICheckAuditEmitter()
aicheckauditemitter.emit()
aicheckauditemitter.read_all()
```

### Function Usage

```python
# Using get_audit_emitter
result = get_audit_emitter(path)
```

```python
# Using to_jsonl
result = to_jsonl()
```

```python
# Using __init__
result = __init__(audit_path)
```



---
**Generated**: 2026-03-26T09:39:04.719516
**Type**: api_reference
**Quality**: comprehensive
