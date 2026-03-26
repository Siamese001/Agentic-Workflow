# API Documentation: seam_audit

**Target Audience**: developers, api_users

# seam_audit API Documentation

**File**: `seam_audit.py`
**Classes**: 2
**Functions**: 16

## Classes

- **SeamAuditRecord**
- **SeamAuditLogger**

## Functions

- **get_seam_audit_logger** -> SeamAuditLogger
- **seam_audit_hook**
- **log_seam_operation** -> SeamAuditRecord | None
- **get_seam_audit_digest** -> str
- **clear_seam_audit_records**
- **__post_init__**
- **__init__**
- **enable**
- **disable**
- **log_seam_operation** -> SeamAuditRecord
- **get_records** -> list[SeamAuditRecord]
- **get_digest** -> str
- **clear_records**
- **_compute_hash** -> str
- **decorator**
- **wrapper**


## Class: SeamAuditRecord

**Description**: Immutable audit record for seam operations.

### Methods

#### __post_init__
**Parameters**: self



## Class: SeamAuditLogger

**Description**: Central logger for seam audit records.

### Methods

#### __init__
**Parameters**: self

#### enable
**Parameters**: self
**Description**: Enable audit logging.

#### disable
**Parameters**: self
**Description**: Disable audit logging.

#### log_seam_operation
**Parameters**: self, seam_id, operation, inputs, outputs, layer_source, layer_target, caller_id, metadata
**Returns**: SeamAuditRecord
**Description**: Log a seam operation with deterministic hashing.

#### get_records
**Parameters**: self, seam_id
**Returns**: list[SeamAuditRecord]
**Description**: Get audit records, optionally filtered by seam_id.

#### get_digest
**Parameters**: self, seam_id
**Returns**: str
**Description**: Compute deterministic digest of audit records.

#### clear_records
**Parameters**: self
**Description**: Clear all audit records (for testing).

#### _compute_hash
**Parameters**: self, data
**Returns**: str
**Description**: Compute deterministic hash for any serializable data.



## Function: get_seam_audit_logger

**Returns**: SeamAuditLogger
**Description**: Get the global seam audit logger instance.



## Function: seam_audit_hook

**Parameters**: seam_id, operation, layer_source, layer_target
**Description**: Decorator to automatically audit seam operations.



## Function: log_seam_operation

**Parameters**: seam_id, operation, inputs, outputs, layer_source, layer_target, caller_id, metadata
**Returns**: SeamAuditRecord | None
**Description**: Log a seam operation manually.



## Function: get_seam_audit_digest

**Parameters**: seam_id
**Returns**: str
**Description**: Get deterministic digest of seam audit records.



## Function: clear_seam_audit_records

**Description**: Clear all seam audit records (for testing).



## Function: __post_init__

**Parameters**: self


## Function: __init__

**Parameters**: self


## Function: enable

**Parameters**: self
**Description**: Enable audit logging.



## Function: disable

**Parameters**: self
**Description**: Disable audit logging.



## Function: log_seam_operation

**Parameters**: self, seam_id, operation, inputs, outputs, layer_source, layer_target, caller_id, metadata
**Returns**: SeamAuditRecord
**Description**: Log a seam operation with deterministic hashing.



## Function: get_records

**Parameters**: self, seam_id
**Returns**: list[SeamAuditRecord]
**Description**: Get audit records, optionally filtered by seam_id.



## Function: get_digest

**Parameters**: self, seam_id
**Returns**: str
**Description**: Compute deterministic digest of audit records.



## Function: clear_records

**Parameters**: self
**Description**: Clear all audit records (for testing).



## Function: _compute_hash

**Parameters**: self, data
**Returns**: str
**Description**: Compute deterministic hash for any serializable data.



## Function: decorator

**Parameters**: func


## Function: wrapper



## Usage Examples

### Class Usage

```python
# Using SeamAuditRecord
seamauditrecord = SeamAuditRecord()
```

```python
# Using SeamAuditLogger
seamauditlogger = SeamAuditLogger()
seamauditlogger.enable()
seamauditlogger.disable()
```

### Function Usage

```python
# Using get_seam_audit_logger
result = get_seam_audit_logger()
```

```python
# Using seam_audit_hook
result = seam_audit_hook(seam_id, operation)
```

```python
# Using log_seam_operation
result = log_seam_operation(seam_id, operation)
```



---
**Generated**: 2026-03-26T09:39:03.390690
**Type**: api_reference
**Quality**: comprehensive
