# API Documentation: policy_hash_enforcer

**Target Audience**: developers, api_users

# policy_hash_enforcer API Documentation

**File**: `policy_hash_enforcer.py`
**Classes**: 3
**Functions**: 8

## Classes

- **PolicyHashViolation** (inherits from RuntimeError)
- **PolicyHashValidationResult**
- **PolicyHashEnforcer**

## Functions

- **_safe_str** -> str
- **__init__** -> None
- **format** -> str
- **__init__** -> None
- **active_merkle_root** -> str
- **enforce** -> None
- **validate** -> PolicyHashValidationResult
- **derive_root** -> str


## Class: PolicyHashViolation

**Description**: Raised when an InstructionPacket fails policy hash validation at L0 routing entry.

**Inherits from**: RuntimeError

### Methods

#### __init__
**Parameters**: self, reason, packet_id, policy_id
**Returns**: None



## Class: PolicyHashValidationResult

**Description**: Result of a policy hash validation pass.

### Methods

#### format
**Parameters**: self
**Returns**: str



## Class: PolicyHashEnforcer

**Description**: Validates InstructionPacket.policy_hash against the active Merkle policy root.

    Configured with an ``active_merkle_root`` at construction.  Call
    ``enforce()`` for a hard-fail check, or ``validate()`` for a non-raising
    result object.

    Usage::

        enforcer = PolicyHashEnforcer(active_merkle_root=current_root)
        enforcer.enforce(instruction_packet)   # raises PolicyHashViolation on failure

    The active Merkle root must be obtained from the canonical policy vault
    (L4 Blueprint Vault or equivalent SSOT).  Callers are responsible for
    supplying the correct root — this class does not fetch it.
    

### Methods

#### __init__
**Parameters**: self, active_merkle_root
**Returns**: None
**Description**: 
        Parameters
        ----------
        active_merkle_root:
            Hex string of the current active policy Merkle root.  Must be
            non-empty; construction raises ``ValueError`` otherwise.
        mode:
            ``"HARD_FAIL"`` (default) — ``enforce()`` raises on any violation.
            ``"LOG_ONLY"`` — ``enforce()`` logs but never raises.
        

#### active_merkle_root
**Parameters**: self
**Returns**: str
**Description**: The active policy Merkle root this enforcer was constructed with.

#### enforce
**Parameters**: self, packet
**Returns**: None
**Description**: Hard-fail validation of ``packet.policy_hash`` vs active root.

        Parameters
        ----------
        packet:
            Any object with an ``instruction_id`` (str) and ``policy_hash``
            (str) attribute — typically an ``InstructionPacket``.

        Raises
        ------
        PolicyHashViolation
            When the packet's policy_hash is missing or does not match the
            active Merkle root, AND mode is ``"HARD_FAIL"``.
        

#### validate
**Parameters**: self, packet
**Returns**: PolicyHashValidationResult
**Description**: Non-raising validation; returns a ``PolicyHashValidationResult``.

        Accepts any object with ``instruction_id`` and ``policy_hash``
        attributes.  Missing attributes are treated as empty strings.
        

#### derive_root
**Parameters**: policy_config
**Returns**: str
**Description**: Derive a deterministic policy Merkle root from *policy_config*.

        Computes SHA-256 over the canonical JSON representation
        (sorted keys, no spaces, ASCII-safe) of *policy_config*.

        This is the same deterministic serialization used by
        ``InstructionPacket._canonical_bytes()``.

        Parameters
        ----------
        policy_config:
            JSON-serialisable dict representing the current policy state.

        Returns
        -------
        str
            Lowercase hex SHA-256 digest.
        



## Function: _safe_str

**Parameters**: value
**Returns**: str
**Description**: Return str(value) or '' if value is None.



## Function: __init__

**Parameters**: self, reason, packet_id, policy_id
**Returns**: None


## Function: format

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, active_merkle_root
**Returns**: None
**Description**: 
        Parameters
        ----------
        active_merkle_root:
            Hex string of the current active policy Merkle root.  Must be
            non-empty; construction raises ``ValueError`` otherwise.
        mode:
            ``"HARD_FAIL"`` (default) — ``enforce()`` raises on any violation.
            ``"LOG_ONLY"`` — ``enforce()`` logs but never raises.
        



## Function: active_merkle_root

**Parameters**: self
**Returns**: str
**Description**: The active policy Merkle root this enforcer was constructed with.



## Function: enforce

**Parameters**: self, packet
**Returns**: None
**Description**: Hard-fail validation of ``packet.policy_hash`` vs active root.

        Parameters
        ----------
        packet:
            Any object with an ``instruction_id`` (str) and ``policy_hash``
            (str) attribute — typically an ``InstructionPacket``.

        Raises
        ------
        PolicyHashViolation
            When the packet's policy_hash is missing or does not match the
            active Merkle root, AND mode is ``"HARD_FAIL"``.
        



## Function: validate

**Parameters**: self, packet
**Returns**: PolicyHashValidationResult
**Description**: Non-raising validation; returns a ``PolicyHashValidationResult``.

        Accepts any object with ``instruction_id`` and ``policy_hash``
        attributes.  Missing attributes are treated as empty strings.
        



## Function: derive_root

**Parameters**: policy_config
**Returns**: str
**Description**: Derive a deterministic policy Merkle root from *policy_config*.

        Computes SHA-256 over the canonical JSON representation
        (sorted keys, no spaces, ASCII-safe) of *policy_config*.

        This is the same deterministic serialization used by
        ``InstructionPacket._canonical_bytes()``.

        Parameters
        ----------
        policy_config:
            JSON-serialisable dict representing the current policy state.

        Returns
        -------
        str
            Lowercase hex SHA-256 digest.
        



## Usage Examples

### Class Usage

```python
# Using PolicyHashViolation
policyhashviolation = PolicyHashViolation()
```

```python
# Using PolicyHashValidationResult
policyhashvalidationresult = PolicyHashValidationResult()
policyhashvalidationresult.format()
```

```python
# Using PolicyHashEnforcer
policyhashenforcer = PolicyHashEnforcer()
policyhashenforcer.active_merkle_root()
policyhashenforcer.enforce()
```

### Function Usage

```python
# Using _safe_str
result = _safe_str(value)
```

```python
# Using __init__
result = __init__(reason, packet_id)
```

```python
# Using format
result = format()
```



---
**Generated**: 2026-03-26T09:39:02.626496
**Type**: api_reference
**Quality**: comprehensive
