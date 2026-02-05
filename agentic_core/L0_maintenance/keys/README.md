# Guardian Authority Root Keys

This directory contains the cryptographic public keys used to verify Guardian test artifact signatures.

## Purpose

Guardian tests emit signed artifacts containing:
- Environment metadata
- Commit hash
- Pass/fail result
- Cryptographic signature

The signature must be verifiable against the pinned public key in this directory to prevent:
- Tampering with Guardian results
- Replay attacks
- Unauthorized artifact generation

## Files

- `guardian_pub.pem` - RSA/Ed25519 public key for signature verification

## Security Model

**Trust Anchor:** This public key is the root of trust for all Guardian artifacts.

**Immutability:** Any modification to this key invalidates all existing Guardian artifacts and requires re-signing.

**Version Control:** This key MUST be version-controlled and changes MUST be audited.

## Key Generation (For Future Implementation)

```bash
# Generate Ed25519 key pair
ssh-keygen -t ed25519 -f guardian_key -C "guardian-authority-root"

# Extract public key in PEM format
ssh-keygen -f guardian_key.pub -e -m pem > guardian_pub.pem

# Store private key securely (NOT in version control)
# Private key should be stored in CI/CD secrets or HSM
```

## Verification Process

Guardian artifacts must include:
1. Artifact payload (JSON)
2. Signature (base64-encoded)
3. Timestamp
4. Key fingerprint

Verification:
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

# Load public key
with open("guardian_pub.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

# Verify signature
public_key.verify(signature, artifact_payload)
```

## Rotation Policy

Key rotation requires:
1. Generate new key pair
2. Sign new public key with old private key (chain of trust)
3. Update this file
4. Re-sign all active Guardian artifacts
5. Archive old key with deprecation notice

## References

- Capability 7.2.1: Authority Root (Prompt v4.7 Gap Analysis enhanced.md)
- `structure_blueprint_config.py`: KNOWN_GOOD_HASHES
