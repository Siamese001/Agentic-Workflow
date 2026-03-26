# API Documentation: crypto_trust_types

**Target Audience**: developers, api_users

# crypto_trust_types API Documentation

**File**: `crypto_trust_types.py`
**Classes**: 12
**Functions**: 16

## Classes

- **KeyStatus** (inherits from Enum)
- **SigningAlgorithm** (inherits from Enum)
- **KeyRecord**
- **TrustRoot**
- **SignatureEnvelope**
- **SignedGuardianArtifact**
- **HumanResolution** (inherits from Enum)
- **SignedModify**
- **ReplayGuardRecord**
- **HashMismatchTracker**
- **SignatureEnclave** (inherits from ABC)
- **DeterministicTestEnclave** (inherits from SignatureEnclave)

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **get_key** -> KeyRecord | None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **record_mismatch** -> bool
- **sign** -> str
- **verify** -> bool
- **get_key_record** -> KeyRecord | None
- **__init__** -> None
- **sign** -> str
- **verify** -> bool
- **get_key_record** -> KeyRecord | None


## Class: KeyStatus

**Description**: Status of a key in the trust root.

**Inherits from**: Enum



## Class: SigningAlgorithm

**Description**: Supported signing algorithms.

**Inherits from**: Enum



## Class: KeyRecord

**Description**: §7.4.2 — A single key record in the trust root.

    Fields: key_id, public_key, created_tick, status, algorithm.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: TrustRoot

**Description**: §7.4.2 — Pinned trust root containing all known keys.

    Immutable once constructed. Keys are looked up by key_id.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### get_key
**Parameters**: self, key_id
**Returns**: KeyRecord | None
**Description**: Look up a key by ID. Returns None if not found.



## Class: SignatureEnvelope

**Description**: §7.4 / §7.2.1 — Cryptographic signature wrapping any artifact.

    Fields: trace_id, artifact_hash, key_id, signature, algorithm,
    semantic_clock_tick.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: SignedGuardianArtifact

**Description**: §7.2.1 / §7.4 — A signed guardian artifact with all required fields.

    Required per spec: trace_id, signature, prestaged_perms,
    environment_metadata, commit_hash, pass_fail.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: HumanResolution

**Description**: §2.7 — Ternary resolution from human review.

**Inherits from**: Enum



## Class: SignedModify

**Description**: §2.7.1 — Human MODIFY resolution generates a signed artifact.

    Required fields: trace_id, human_reviewer_id, resolution,
    modified_manifest, signature.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ReplayGuardRecord

**Description**: §7.2 — Tracks artifact_hash sightings for replay detection.

    Not frozen: seen_count is mutable for tracking.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: HashMismatchTracker

**Description**: §2.6 — Tracks hash mismatches within a healing wave.

    ≥2 mismatches in a single wave forces human escalation.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### record_mismatch
**Parameters**: self
**Returns**: bool
**Description**: Record a mismatch. Returns True if escalation is now required.



## Class: SignatureEnclave

**Description**: §7.4.1 — Abstract interface for the signing enclave.

    All signing operations MUST occur within a SignatureEnclave.
    Implementations must be deterministic, with no wall-clock or env reads.
    

**Inherits from**: ABC

### Methods

#### sign
**Parameters**: self, artifact_bytes, key_id
**Returns**: str
**Description**: Sign artifact bytes with the given key. Returns signature hex string.

#### verify
**Parameters**: self, artifact_bytes, signature, key_id
**Returns**: bool
**Description**: Verify signature against artifact bytes and key. Returns True if valid.

#### get_key_record
**Parameters**: self, key_id
**Returns**: KeyRecord | None
**Description**: Retrieve a key record from the enclave's trust root.



## Class: DeterministicTestEnclave

**Description**: §7.4.1 — Deterministic test enclave using HMAC-SHA256 with fixed keys.

    No network, no env reads, no wall-clock. Purely deterministic.
    

**Inherits from**: SignatureEnclave

### Methods

#### __init__
**Parameters**: self, trust_root
**Returns**: None

#### sign
**Parameters**: self, artifact_bytes, key_id
**Returns**: str
**Description**: HMAC-SHA256 sign using the key's public_key as the HMAC secret.

#### verify
**Parameters**: self, artifact_bytes, signature, key_id
**Returns**: bool
**Description**: Verify HMAC-SHA256 signature.

#### get_key_record
**Parameters**: self, key_id
**Returns**: KeyRecord | None



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: get_key

**Parameters**: self, key_id
**Returns**: KeyRecord | None
**Description**: Look up a key by ID. Returns None if not found.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: record_mismatch

**Parameters**: self
**Returns**: bool
**Description**: Record a mismatch. Returns True if escalation is now required.



## Function: sign

**Parameters**: self, artifact_bytes, key_id
**Returns**: str
**Description**: Sign artifact bytes with the given key. Returns signature hex string.



## Function: verify

**Parameters**: self, artifact_bytes, signature, key_id
**Returns**: bool
**Description**: Verify signature against artifact bytes and key. Returns True if valid.



## Function: get_key_record

**Parameters**: self, key_id
**Returns**: KeyRecord | None
**Description**: Retrieve a key record from the enclave's trust root.



## Function: __init__

**Parameters**: self, trust_root
**Returns**: None


## Function: sign

**Parameters**: self, artifact_bytes, key_id
**Returns**: str
**Description**: HMAC-SHA256 sign using the key's public_key as the HMAC secret.



## Function: verify

**Parameters**: self, artifact_bytes, signature, key_id
**Returns**: bool
**Description**: Verify HMAC-SHA256 signature.



## Function: get_key_record

**Parameters**: self, key_id
**Returns**: KeyRecord | None


## Usage Examples

### Class Usage

```python
# Using KeyStatus
keystatus = KeyStatus()
```

```python
# Using SigningAlgorithm
signingalgorithm = SigningAlgorithm()
```

```python
# Using KeyRecord
keyrecord = KeyRecord()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using get_key
result = get_key(key_id)
```



---
**Generated**: 2026-03-26T09:39:03.433174
**Type**: api_reference
**Quality**: comprehensive
