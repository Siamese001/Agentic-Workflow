# API Documentation: instruction_packet_types

**Target Audience**: developers, api_users

# instruction_packet_types API Documentation

**File**: `instruction_packet_types.py`
**Classes**: 2
**Functions**: 11

## Classes

- **SignatureVerificationError** (inherits from ValueError)
- **InstructionPacket**

## Functions

- **_canonical_bytes** -> bytes
- **__post_init__** -> None
- **_signable_dict** -> dict[str, Any]
- **_l5_signable_dict** -> dict[str, Any]
- **canonical_bytes** -> bytes
- **sign** -> InstructionPacket
- **certify_l5** -> InstructionPacket
- **verify_l5_certification** -> None
- **verify** -> None
- **is_signed** -> bool
- **is_l5_certified** -> bool


## Class: SignatureVerificationError

**Description**: Raised when HMAC signature verification fails.

**Inherits from**: ValueError



## Class: InstructionPacket

**Description**: Signed instruction artifact for L2 ingress.

    Fields
    ------
    instruction_id : str
        Stable, deterministic identifier for this instruction.
    payload : str
        The instruction text / command payload.
    metadata : dict[str, Any]
        Arbitrary key/value context (must be JSON-serialisable).
    signature : str
        Lowercase hex HMAC-SHA256.  Empty string means unsigned.
    l5_signature : str
        L5 guardian certification signature (HMAC-SHA256). Empty means uncertified.
    certification_timestamp : str
        ISO8601 timestamp when L5 certification was applied.
    expiration_timestamp : str
        ISO8601 timestamp when L5 certification expires.
    agent_registry_hash : str
        SHA256 hash of agent registry at time of certification.
    execution_profile_hash : str
        SHA256 hash of execution profile at time of certification.
    policy_hash : str
        SHA256 hash of policy configuration at time of certification.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Enforce mandatory signing at construction.

#### _signable_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return the dict that is signed by base signature (base fields only).

#### _l5_signable_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return the dict for L5 signature (excludes l5_signature to avoid circularity).

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Deterministic bytes over the base signing surface.

#### sign
**Parameters**: self, secret
**Returns**: InstructionPacket
**Description**: Return a *new* InstructionPacket with HMAC-SHA256 signature set.

#### certify_l5
**Parameters**: self, l5_secret, agent_registry_hash, execution_profile_hash, policy_hash, expiration_hours
**Returns**: InstructionPacket
**Description**: Return a *new* InstructionPacket with L5 certification applied.

        Args:
            l5_secret: L5 guardian signing secret
            agent_registry_hash: SHA256 of agent registry
            execution_profile_hash: SHA256 of execution profile
            policy_hash: SHA256 of policy configuration
            expiration_hours: Hours until certification expires

        Returns:
            New InstructionPacket with L5 certification fields populated
        

#### verify_l5_certification
**Parameters**: self, l5_secret
**Returns**: None
**Description**: Verify L5 certification signature and expiration.

        Args:
            l5_secret: L5 guardian signing secret

        Raises:
            SignatureVerificationError: if L5 signature is invalid or expired
        

#### verify
**Parameters**: self, secret
**Returns**: None
**Description**: Raise SignatureVerificationError if signature is absent or wrong.

#### is_signed
**Parameters**: self
**Returns**: bool
**Description**: True when a signature string is present (not verified).

#### is_l5_certified
**Parameters**: self
**Returns**: bool
**Description**: True when L5 certification signature is present (not verified).



## Function: _canonical_bytes

**Parameters**: data
**Returns**: bytes
**Description**: Return deterministic UTF-8 bytes from *data* (sorted keys, no spaces).



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Enforce mandatory signing at construction.



## Function: _signable_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return the dict that is signed by base signature (base fields only).



## Function: _l5_signable_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return the dict for L5 signature (excludes l5_signature to avoid circularity).



## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Deterministic bytes over the base signing surface.



## Function: sign

**Parameters**: self, secret
**Returns**: InstructionPacket
**Description**: Return a *new* InstructionPacket with HMAC-SHA256 signature set.



## Function: certify_l5

**Parameters**: self, l5_secret, agent_registry_hash, execution_profile_hash, policy_hash, expiration_hours
**Returns**: InstructionPacket
**Description**: Return a *new* InstructionPacket with L5 certification applied.

        Args:
            l5_secret: L5 guardian signing secret
            agent_registry_hash: SHA256 of agent registry
            execution_profile_hash: SHA256 of execution profile
            policy_hash: SHA256 of policy configuration
            expiration_hours: Hours until certification expires

        Returns:
            New InstructionPacket with L5 certification fields populated
        



## Function: verify_l5_certification

**Parameters**: self, l5_secret
**Returns**: None
**Description**: Verify L5 certification signature and expiration.

        Args:
            l5_secret: L5 guardian signing secret

        Raises:
            SignatureVerificationError: if L5 signature is invalid or expired
        



## Function: verify

**Parameters**: self, secret
**Returns**: None
**Description**: Raise SignatureVerificationError if signature is absent or wrong.



## Function: is_signed

**Parameters**: self
**Returns**: bool
**Description**: True when a signature string is present (not verified).



## Function: is_l5_certified

**Parameters**: self
**Returns**: bool
**Description**: True when L5 certification signature is present (not verified).



## Usage Examples

### Class Usage

```python
# Using SignatureVerificationError
signatureverificationerror = SignatureVerificationError()
```

```python
# Using InstructionPacket
instructionpacket = InstructionPacket()
instructionpacket.canonical_bytes()
instructionpacket.sign()
```

### Function Usage

```python
# Using _canonical_bytes
result = _canonical_bytes(data)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _signable_dict
result = _signable_dict()
```



---
**Generated**: 2026-03-26T09:39:03.971241
**Type**: api_reference
**Quality**: comprehensive
