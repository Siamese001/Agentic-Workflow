# API Documentation: integrity_validator

**Target Audience**: developers, api_users

# integrity_validator API Documentation

**File**: `integrity_validator.py`
**Classes**: 0
**Functions**: 4


## Functions

- **compute_entry_hash** -> str
- **validate_ledger_chain** -> None
- **append_with_hash** -> dict[str, Any]
- **validate_ledger_file** -> None


## Function: compute_entry_hash

**Parameters**: prev_hash, entry
**Returns**: str
**Description**: Compute chained SHA256: hash(prev_hash || entry_bytes).



## Function: validate_ledger_chain

**Parameters**: entries
**Returns**: None
**Description**: Walk the ledger chain and raise LedgerIntegrityViolation on first broken link.

    Each entry must have a ``_hash`` field computed from the previous hash
    and the entry data (excluding the ``_hash`` field itself).
    



## Function: append_with_hash

**Parameters**: entries, new_entry
**Returns**: dict[str, Any]
**Description**: Append a new entry to the ledger list, computing its chained hash.

    Returns the entry dict with ``_hash`` set.
    



## Function: validate_ledger_file

**Parameters**: ledger_path
**Returns**: None
**Description**: Load a JSONL ledger file and validate its hash chain.



## Usage Examples

### Function Usage

```python
# Using compute_entry_hash
result = compute_entry_hash(prev_hash, entry)
```

```python
# Using validate_ledger_chain
result = validate_ledger_chain(entries)
```

```python
# Using append_with_hash
result = append_with_hash(entries, new_entry)
```



---
**Generated**: 2026-03-26T09:39:04.544233
**Type**: api_reference
**Quality**: comprehensive
