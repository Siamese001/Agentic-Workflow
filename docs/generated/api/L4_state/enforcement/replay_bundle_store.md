# API Documentation: replay_bundle_store

**Target Audience**: developers, api_users

# replay_bundle_store API Documentation

**File**: `replay_bundle_store.py`
**Classes**: 4
**Functions**: 8

## Classes

- **ReplayBundleStore**
- **VerifiedReplay**
- **ReplayVerificationError** (inherits from Exception)
- **ReplayVerifier**

## Functions

- **_sha256** -> str
- **store_replay_bundle** -> str
- **fetch_replay_bundle** -> ReplayBundle | None
- **count** -> int
- **seal** -> str
- **mutate** -> None
- **__init__** -> None
- **verify** -> VerifiedReplay


## Class: ReplayBundleStore

**Description**: 
    L4 in-process store for ReplayBundle artifacts.

    Keyed by replay_hash. Idempotent: duplicate hash = no-op.
    Non-mutating to knowledge index (Pinecone/Redis).
    

### Methods

#### store_replay_bundle
**Parameters**: self, bundle
**Returns**: str
**Description**: 
        Persist a ReplayBundle. Returns replay_hash.
        Idempotent: storing the same bundle twice is a no-op.
        

#### fetch_replay_bundle
**Parameters**: self, replay_hash
**Returns**: ReplayBundle | None
**Description**: Return the ReplayBundle for the given replay_hash, or None.

#### count
**Parameters**: self
**Returns**: int

#### seal
**Parameters**: self, data
**Returns**: str
**Description**: REQ-020: persist an arbitrary dict as a sealed, immutable record.

        Returns a content-addressed key (sha256 of JSON-serialised data).
        Once sealed the entry is append-only; call mutate() to verify immutability.
        

#### mutate
**Parameters**: self, bundle_id, updates
**Returns**: None
**Description**: REQ-020: mutation of a sealed artifact is forbidden — always raises.



## Class: VerifiedReplay

**Description**: Result of a successful replay verification.



## Class: ReplayVerificationError

**Description**: 
    Raised when replay bundle verification fails.

    Attributes
    ----------
    code   : str — violation code
    detail : str — human-readable description
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, code, detail
**Returns**: None



## Class: ReplayVerifier

**Description**: 
    Verifies a ReplayBundle for:
    1. Hash integrity — replay_hash recomputation matches stored value.
    2. Prior-only constraints — all referenced prior signals/violations have
       commit_tick strictly less than execution_start_tick.
    3. Component presence — referenced hashes exist in provided registries.

    All checks are deterministic and raise ReplayVerificationError on failure.
    

### Methods

#### verify
**Parameters**: self, bundle
**Returns**: VerifiedReplay
**Description**: 
        Verify a ReplayBundle.

        Parameters
        ----------
        bundle                 : ReplayBundle
        known_config_hashes    : set of valid config hash strings (optional)
        known_citation_hashes  : set of valid citation_hash strings (optional)
        known_signal_hashes    : set of valid signal_hash strings (optional)
        known_violation_hashes : set of valid violation event_hash strings (optional)
        known_intent_hashes    : set of valid tool intent_hash strings (optional)
        known_result_hashes    : set of valid tool result_hash strings (optional)
        prior_signal_tick      : commit_tick of the prior detection signal (optional)
        prior_violation_ticks  : {event_hash: commit_tick} for prior violations (optional)

        Returns
        -------
        VerifiedReplay on success.

        Raises
        ------
        ReplayVerificationError on any failure.
        



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: store_replay_bundle

**Parameters**: self, bundle
**Returns**: str
**Description**: 
        Persist a ReplayBundle. Returns replay_hash.
        Idempotent: storing the same bundle twice is a no-op.
        



## Function: fetch_replay_bundle

**Parameters**: self, replay_hash
**Returns**: ReplayBundle | None
**Description**: Return the ReplayBundle for the given replay_hash, or None.



## Function: count

**Parameters**: self
**Returns**: int


## Function: seal

**Parameters**: self, data
**Returns**: str
**Description**: REQ-020: persist an arbitrary dict as a sealed, immutable record.

        Returns a content-addressed key (sha256 of JSON-serialised data).
        Once sealed the entry is append-only; call mutate() to verify immutability.
        



## Function: mutate

**Parameters**: self, bundle_id, updates
**Returns**: None
**Description**: REQ-020: mutation of a sealed artifact is forbidden — always raises.



## Function: __init__

**Parameters**: self, code, detail
**Returns**: None


## Function: verify

**Parameters**: self, bundle
**Returns**: VerifiedReplay
**Description**: 
        Verify a ReplayBundle.

        Parameters
        ----------
        bundle                 : ReplayBundle
        known_config_hashes    : set of valid config hash strings (optional)
        known_citation_hashes  : set of valid citation_hash strings (optional)
        known_signal_hashes    : set of valid signal_hash strings (optional)
        known_violation_hashes : set of valid violation event_hash strings (optional)
        known_intent_hashes    : set of valid tool intent_hash strings (optional)
        known_result_hashes    : set of valid tool result_hash strings (optional)
        prior_signal_tick      : commit_tick of the prior detection signal (optional)
        prior_violation_ticks  : {event_hash: commit_tick} for prior violations (optional)

        Returns
        -------
        VerifiedReplay on success.

        Raises
        ------
        ReplayVerificationError on any failure.
        



## Usage Examples

### Class Usage

```python
# Using ReplayBundleStore
replaybundlestore = ReplayBundleStore()
replaybundlestore.store_replay_bundle()
replaybundlestore.fetch_replay_bundle()
```

```python
# Using VerifiedReplay
verifiedreplay = VerifiedReplay()
```

```python
# Using ReplayVerificationError
replayverificationerror = ReplayVerificationError()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using store_replay_bundle
result = store_replay_bundle(bundle)
```

```python
# Using fetch_replay_bundle
result = fetch_replay_bundle(replay_hash)
```



---
**Generated**: 2026-03-26T09:39:04.519673
**Type**: api_reference
**Quality**: comprehensive
