# API Documentation: hash_chain_audit_log

**Target Audience**: developers, api_users

# hash_chain_audit_log API Documentation

**File**: `hash_chain_audit_log.py`
**Classes**: 2
**Functions**: 9

## Classes

- **AuditEntry**
- **HashChainAuditLog**

## Functions

- **_canonical_entry_bytes** -> bytes
- **verify_hash** -> bool
- **__init__** -> None
- **length** -> int
- **entries** -> tuple[AuditEntry, ...]
- **chain_root** -> str | None
- **append** -> AuditEntry
- **seal** -> str
- **verify_chain_integrity** -> bool


## Class: AuditEntry

**Description**: Single immutable entry in the hash-chained audit log.

### Methods

#### verify_hash
**Parameters**: self
**Returns**: bool
**Description**: Re-derive hash and compare.



## Class: HashChainAuditLog

**Description**: Append-only hash-chained audit log.

    Usage::

        log = HashChainAuditLog()
        log.append(tier="L2", action="persist",
                   payload={"key": "value"})
        assert log.verify_chain_integrity()
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### length
**Parameters**: self
**Returns**: int

#### entries
**Parameters**: self
**Returns**: tuple[AuditEntry, ...]

#### chain_root
**Parameters**: self
**Returns**: str | None
**Description**: Hash of the last entry, or None if empty.

#### append
**Parameters**: self
**Returns**: AuditEntry
**Description**: Append a new entry to the chain.

        Timestamp is frozen at call time before hash.
        

#### seal
**Parameters**: self
**Returns**: str
**Description**: Seal the log — no further appends allowed.

        Returns the chain root hash.
        

#### verify_chain_integrity
**Parameters**: self
**Returns**: bool
**Description**: Replay hash chain from genesis and verify.



## Function: _canonical_entry_bytes

**Parameters**: entry_index, previous_hash, timestamp, tier, action, payload
**Returns**: bytes
**Description**: Deterministic canonical bytes for hash computation.

    Delegates to the shared canonical serializer.
    



## Function: verify_hash

**Parameters**: self
**Returns**: bool
**Description**: Re-derive hash and compare.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: length

**Parameters**: self
**Returns**: int


## Function: entries

**Parameters**: self
**Returns**: tuple[AuditEntry, ...]


## Function: chain_root

**Parameters**: self
**Returns**: str | None
**Description**: Hash of the last entry, or None if empty.



## Function: append

**Parameters**: self
**Returns**: AuditEntry
**Description**: Append a new entry to the chain.

        Timestamp is frozen at call time before hash.
        



## Function: seal

**Parameters**: self
**Returns**: str
**Description**: Seal the log — no further appends allowed.

        Returns the chain root hash.
        



## Function: verify_chain_integrity

**Parameters**: self
**Returns**: bool
**Description**: Replay hash chain from genesis and verify.



## Usage Examples

### Class Usage

```python
# Using AuditEntry
auditentry = AuditEntry()
auditentry.verify_hash()
```

```python
# Using HashChainAuditLog
hashchainauditlog = HashChainAuditLog()
hashchainauditlog.length()
hashchainauditlog.entries()
```

### Function Usage

```python
# Using _canonical_entry_bytes
result = _canonical_entry_bytes(entry_index, previous_hash)
```

```python
# Using verify_hash
result = verify_hash()
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:03.614606
**Type**: api_reference
**Quality**: comprehensive
