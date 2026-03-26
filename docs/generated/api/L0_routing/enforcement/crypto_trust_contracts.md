# API Documentation: crypto_trust_contracts

**Target Audience**: developers, api_users

# crypto_trust_contracts API Documentation

**File**: `crypto_trust_contracts.py`
**Classes**: 6
**Functions**: 9

## Classes

- **SigningError** (inherits from Exception)
- **VerificationError** (inherits from Exception)
- **ReplayDetectedError** (inherits from Exception)
- **ReplayGuardStore**
- **EscalationRequiredError** (inherits from Exception)
- **SignedGuardianError** (inherits from Exception)

## Functions

- **hash_artifact_canonical** -> str
- **sign_artifact** -> SignatureEnvelope
- **verify_signature** -> bool
- **record_and_block_replay** -> bool
- **record_hash_mismatch** -> bool
- **build_signed_guardian_artifact** -> SignedGuardianArtifact
- **__init__** -> None
- **check_and_record** -> ReplayGuardRecord
- **record_count** -> int


## Class: SigningError

**Description**: Raised when artifact signing fails.

**Inherits from**: Exception



## Class: VerificationError

**Description**: Raised when signature verification fails (fail-closed).

**Inherits from**: Exception



## Class: ReplayDetectedError

**Description**: Raised when a replay attack is detected.

**Inherits from**: Exception



## Class: ReplayGuardStore

**Description**: §7.2 — In-memory replay guard store.

    Tracks artifact_hash sightings. Blocks on second sighting.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### check_and_record
**Parameters**: self, artifact_hash, current_tick
**Returns**: ReplayGuardRecord
**Description**: Record an artifact hash. Raises on replay (second sighting).

#### record_count
**Parameters**: self
**Returns**: int



## Class: EscalationRequiredError

**Description**: Raised when ≥2 hash mismatches force human escalation.

**Inherits from**: Exception



## Class: SignedGuardianError

**Description**: Raised when signed guardian artifact construction fails.

**Inherits from**: Exception



## Function: hash_artifact_canonical

**Parameters**: artifact_bytes
**Returns**: str
**Description**: Canonical SHA-256 hash of artifact bytes. Single source of truth.



## Function: sign_artifact

**Parameters**: artifact_bytes, key_id, enclave, trace_id, semantic_clock_tick
**Returns**: SignatureEnvelope
**Description**: §7.4 / §7.4.1 — Sign artifact bytes via the enclave. Fail-closed.



## Function: verify_signature

**Parameters**: artifact_bytes, envelope, trust_root, enclave
**Returns**: bool
**Description**: §7.4.2 — Verify signature against pinned public keys. Fail-closed.

    Checks:
    1. artifact_hash matches canonical hash of artifact_bytes
    2. key_id exists in trust_root and is ACTIVE
    3. Signature is valid per enclave.verify()
    



## Function: record_and_block_replay

**Parameters**: envelope, replay_store
**Returns**: bool
**Description**: §7.2 — Record envelope and block if replay detected. Fail-closed.



## Function: record_hash_mismatch

**Parameters**: tracker
**Returns**: bool
**Description**: §2.6 — Record a hash mismatch. Raises if escalation threshold met.



## Function: build_signed_guardian_artifact

**Parameters**: trace_id, prestaged_perms, environment_metadata, commit_hash, pass_fail, artifact_bytes, key_id, enclave
**Returns**: SignedGuardianArtifact
**Description**: §7.2.1 / §7.4 — Build a signed guardian artifact. Fail-closed.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: check_and_record

**Parameters**: self, artifact_hash, current_tick
**Returns**: ReplayGuardRecord
**Description**: Record an artifact hash. Raises on replay (second sighting).



## Function: record_count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using SigningError
signingerror = SigningError()
```

```python
# Using VerificationError
verificationerror = VerificationError()
```

```python
# Using ReplayDetectedError
replaydetectederror = ReplayDetectedError()
```

### Function Usage

```python
# Using hash_artifact_canonical
result = hash_artifact_canonical(artifact_bytes)
```

```python
# Using sign_artifact
result = sign_artifact(artifact_bytes, key_id)
```

```python
# Using verify_signature
result = verify_signature(artifact_bytes, envelope)
```



---
**Generated**: 2026-03-26T09:39:02.607912
**Type**: api_reference
**Quality**: comprehensive
