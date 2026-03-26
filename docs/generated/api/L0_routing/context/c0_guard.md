# API Documentation: c0_guard

**Target Audience**: developers, api_users

# c0_guard API Documentation

**File**: `c0_guard.py`
**Classes**: 0
**Functions**: 4


## Functions

- **_get_hardening_errors**
- **guard_c0_payload** -> None
- **verify_c0_immutability** -> None
- **_hash** -> str


## Function: _get_hardening_errors



## Function: guard_c0_payload

**Parameters**: payload
**Returns**: None
**Description**: Raise C0AuthorityLeakError if payload contains authority fields.

    Wire into RAG context assembly before payload is passed downstream.
    



## Function: verify_c0_immutability

**Parameters**: payload_pre, payload_post
**Returns**: None
**Description**: Raise C0MutationViolation if the payload was modified during assembly.

    Addendum 3.2: context mutation prevention.
    



## Function: _hash

**Parameters**: d
**Returns**: str


## Usage Examples

### Function Usage

```python
# Using _get_hardening_errors
result = _get_hardening_errors()
```

```python
# Using guard_c0_payload
result = guard_c0_payload(payload)
```

```python
# Using verify_c0_immutability
result = verify_c0_immutability(payload_pre, payload_post)
```



---
**Generated**: 2026-03-26T09:39:02.594611
**Type**: api_reference
**Quality**: comprehensive
