# API Documentation: commit_proof_invariant_types

**Target Audience**: developers, api_users

# commit_proof_invariant_types API Documentation

**File**: `commit_proof_invariant_types.py`
**Classes**: 2
**Functions**: 5

## Classes

- **DeterminismProofFailure** (inherits from RuntimeError)
- **CommitProofInvariant**

## Functions

- **make_proof** -> CommitProofInvariant
- **canonical_digest** -> str
- **__post_init__** -> None
- **verify_stable** -> None
- **verify_unstable** -> None


## Class: DeterminismProofFailure

**Description**: Raised when a CommitProofInvariant verification fails.

**Inherits from**: RuntimeError



## Class: CommitProofInvariant

**Description**: Captures a determinism digest and verifies it is reproducible.

    Spec: Determinism & Replayability, Guarantee #18.

    Fields:
        phase_id: Stable identifier for the phase this proof covers.
        digest: The expected 64-hex SHA-256 digest.
        inputs_summary: Human-readable summary of what contributed to the digest.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### verify_stable
**Parameters**: self, recompute_fn
**Returns**: None
**Description**: Assert that recompute_fn() returns the same digest as self.digest.

        Raises DeterminismProofFailure if the digest has changed (non-determinism detected).
        

#### verify_unstable
**Parameters**: self, recompute_fn
**Returns**: None
**Description**: Assert that recompute_fn() returns a DIFFERENT digest than self.digest.

        Negative control: verifies that tampered inputs produce a different hash.
        Raises DeterminismProofFailure if the digest is unchanged (tamper not detected).
        



## Function: make_proof

**Parameters**: phase_id, inputs_summary, recompute_fn
**Returns**: CommitProofInvariant
**Description**: Compute a fresh CommitProofInvariant by calling recompute_fn().

    Use this at seal time to capture the current digest.
    



## Function: canonical_digest

**Parameters**: obj
**Returns**: str
**Description**: Compute SHA-256 of canonical JSON (sorted keys, no spaces, ASCII-safe).



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: verify_stable

**Parameters**: self, recompute_fn
**Returns**: None
**Description**: Assert that recompute_fn() returns the same digest as self.digest.

        Raises DeterminismProofFailure if the digest has changed (non-determinism detected).
        



## Function: verify_unstable

**Parameters**: self, recompute_fn
**Returns**: None
**Description**: Assert that recompute_fn() returns a DIFFERENT digest than self.digest.

        Negative control: verifies that tampered inputs produce a different hash.
        Raises DeterminismProofFailure if the digest is unchanged (tamper not detected).
        



## Usage Examples

### Class Usage

```python
# Using DeterminismProofFailure
determinismprooffailure = DeterminismProofFailure()
```

```python
# Using CommitProofInvariant
commitproofinvariant = CommitProofInvariant()
commitproofinvariant.verify_stable()
commitproofinvariant.verify_unstable()
```

### Function Usage

```python
# Using make_proof
result = make_proof(phase_id, inputs_summary)
```

```python
# Using canonical_digest
result = canonical_digest(obj)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:03.951048
**Type**: api_reference
**Quality**: comprehensive
