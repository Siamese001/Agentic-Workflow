# API Documentation: boundary_verifier

**Target Audience**: developers, api_users

# boundary_verifier API Documentation

**File**: `boundary_verifier.py`
**Classes**: 1
**Functions**: 11

## Classes

- **L2BoundaryVerifier**

## Functions

- **__init__** -> None
- **verify_instruction_packet** -> None
- **verify_l5_certification** -> None
- **verify_instruction_packet_with_l5** -> None
- **verify_packet** -> None
- **verify_envelope** -> None
- **verify_sandbox_envelope** -> None
- **is_packet_valid** -> bool
- **is_l5_certified** -> bool
- **is_packet_valid_with_l5** -> bool
- **is_envelope_valid** -> bool


## Class: L2BoundaryVerifier

**Description**: Fail-closed verification gate for L2 ingress artifacts.

    Usage
    -----
    verifier = L2BoundaryVerifier()
    verifier.verify_instruction_packet(packet)    # raises if invalid
    verifier.verify_sandbox_envelope(envelope)  # raises if invalid
    verifier.verify_l5_certification(packet)     # raises if uncertified
    

### Methods

#### __init__
**Parameters**: self, l5_secret, secret
**Returns**: None
**Description**: Initialize verifier with optional L5 secret.

        Args:
            l5_secret: L5 guardian signing secret. If None, L5 verification
                      is skipped (for backward compatibility).
            secret: Deprecated backward-compat param (ignored; key source is injected).
        

#### verify_instruction_packet
**Parameters**: self, packet
**Returns**: None
**Description**: Verify InstructionPacket signature.  Raises SignatureVerificationError on failure.

#### verify_l5_certification
**Parameters**: self, packet
**Returns**: None
**Description**: Verify L5 guardian certification.  Raises SignatureVerificationError on failure.

        This is the P1: INITIALIZATION verification sequence:
        1. Verify L5 signature using canonical HMAC-SHA256
        2. Verify expiration timestamp
        3. Additional verification steps can be added here
        

#### verify_instruction_packet_with_l5
**Parameters**: self, packet
**Returns**: None
**Description**: Verify both base signature and L5 certification.  Raises on any failure.

#### verify_packet
**Parameters**: self, packet
**Returns**: None
**Description**: Backward-compat alias for verify_instruction_packet.

#### verify_envelope
**Parameters**: self, envelope
**Returns**: None
**Description**: Backward-compat alias for verify_sandbox_envelope.

#### verify_sandbox_envelope
**Parameters**: self, envelope
**Returns**: None
**Description**: Verify SandboxEnvelope signature before side-effects.  Raises on failure.

#### is_packet_valid
**Parameters**: self, packet
**Returns**: bool
**Description**: Return True if packet passes verification, False otherwise (no exception).

#### is_l5_certified
**Parameters**: self, packet
**Returns**: bool
**Description**: Return True if packet has valid L5 certification, False otherwise.

#### is_packet_valid_with_l5
**Parameters**: self, packet
**Returns**: bool
**Description**: Return True if packet passes both base and L5 verification, False otherwise.

#### is_envelope_valid
**Parameters**: self, envelope
**Returns**: bool
**Description**: Return True if envelope passes verification, False otherwise (no exception).



## Function: __init__

**Parameters**: self, l5_secret, secret
**Returns**: None
**Description**: Initialize verifier with optional L5 secret.

        Args:
            l5_secret: L5 guardian signing secret. If None, L5 verification
                      is skipped (for backward compatibility).
            secret: Deprecated backward-compat param (ignored; key source is injected).
        



## Function: verify_instruction_packet

**Parameters**: self, packet
**Returns**: None
**Description**: Verify InstructionPacket signature.  Raises SignatureVerificationError on failure.



## Function: verify_l5_certification

**Parameters**: self, packet
**Returns**: None
**Description**: Verify L5 guardian certification.  Raises SignatureVerificationError on failure.

        This is the P1: INITIALIZATION verification sequence:
        1. Verify L5 signature using canonical HMAC-SHA256
        2. Verify expiration timestamp
        3. Additional verification steps can be added here
        



## Function: verify_instruction_packet_with_l5

**Parameters**: self, packet
**Returns**: None
**Description**: Verify both base signature and L5 certification.  Raises on any failure.



## Function: verify_packet

**Parameters**: self, packet
**Returns**: None
**Description**: Backward-compat alias for verify_instruction_packet.



## Function: verify_envelope

**Parameters**: self, envelope
**Returns**: None
**Description**: Backward-compat alias for verify_sandbox_envelope.



## Function: verify_sandbox_envelope

**Parameters**: self, envelope
**Returns**: None
**Description**: Verify SandboxEnvelope signature before side-effects.  Raises on failure.



## Function: is_packet_valid

**Parameters**: self, packet
**Returns**: bool
**Description**: Return True if packet passes verification, False otherwise (no exception).



## Function: is_l5_certified

**Parameters**: self, packet
**Returns**: bool
**Description**: Return True if packet has valid L5 certification, False otherwise.



## Function: is_packet_valid_with_l5

**Parameters**: self, packet
**Returns**: bool
**Description**: Return True if packet passes both base and L5 verification, False otherwise.



## Function: is_envelope_valid

**Parameters**: self, envelope
**Returns**: bool
**Description**: Return True if envelope passes verification, False otherwise (no exception).



## Usage Examples

### Class Usage

```python
# Using L2BoundaryVerifier
l2boundaryverifier = L2BoundaryVerifier()
l2boundaryverifier.verify_instruction_packet()
l2boundaryverifier.verify_l5_certification()
```

### Function Usage

```python
# Using __init__
result = __init__(l5_secret, secret)
```

```python
# Using verify_instruction_packet
result = verify_instruction_packet(packet)
```

```python
# Using verify_l5_certification
result = verify_l5_certification(packet)
```



---
**Generated**: 2026-03-26T09:39:03.677655
**Type**: api_reference
**Quality**: comprehensive
