# API Documentation: vllm_replay_validator_types

**Target Audience**: developers, api_users

# vllm_replay_validator_types API Documentation

**File**: `vllm_replay_validator_types.py`
**Classes**: 2
**Functions**: 9

## Classes

- **VLLMReplayArtifact**
- **VLLMReplayValidator**

## Functions

- **canonical_prompt_hash** -> str
- **canonical_local_request_hash** -> str
- **canonical_response_hash** -> str
- **compute_replay_hash** -> str
- **__post_init__** -> None
- **canonical_payload_hash** -> str
- **verify** -> bool
- **validate** -> bool
- **validate_and_report** -> dict[str, Any]


## Class: VLLMReplayArtifact

**Description**: Immutable artifact for deterministic replay validation.

    Contains all components needed to recompute and verify replay_hash.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_payload_hash
**Parameters**: self
**Returns**: str
**Description**: 
        Get the canonical payload hash derived from the exact bytes used for replay_hash computation.

        This reflects the combined canonical payload (prompt_hash + local_request_hash +
        fingerprint_hash + response_hash) before the final SHA-256.

        Returns:
            64-character lowercase hex SHA256 digest of the canonical payload.
        

#### verify
**Parameters**: self
**Returns**: bool
**Description**: 
        Verify that stored hashes match recomputed hashes.

        Returns:
            True if all hashes match (artifact is untampered), False otherwise.
        



## Class: VLLMReplayValidator

**Description**: Minimal replay validator for tamper detection.

### Methods

#### validate
**Parameters**: self, artifact
**Returns**: bool
**Description**: 
        Validate a replay artifact.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            True if artifact is valid (untampered), False otherwise.
        

#### validate_and_report
**Parameters**: self, artifact
**Returns**: dict[str, Any]
**Description**: 
        Validate artifact and return detailed report.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            Dict with validation result and hash details.
        



## Function: canonical_prompt_hash

**Parameters**: prompt
**Returns**: str
**Description**: 
    Compute SHA256 hash of canonical prompt representation.

    Args:
        prompt: Input prompt string.

    Returns:
        64-character lowercase hex SHA256 digest.
    



## Function: canonical_local_request_hash

**Parameters**: request
**Returns**: str
**Description**: 
    Compute SHA256 hash of shaped local request dict.

    Args:
        request: VLLMLocalRequest instance.

    Returns:
        64-character lowercase hex SHA256 digest.
    



## Function: canonical_response_hash

**Parameters**: result
**Returns**: str
**Description**: 
    Compute SHA256 hash of structured response artifact / telemetry decision record.

    PHASE 6: Includes invariant violations in canonical form for replay integrity.

    Args:
        result: VLLMGatewayCallResult instance.

    Returns:
        64-character lowercase hex SHA256 digest.
    



## Function: compute_replay_hash

**Parameters**: prompt, request, fingerprint, result
**Returns**: str
**Description**: 
    Compute deterministic replay hash from all components.

    replay_hash = SHA256(prompt_hash + local_request_hash + fingerprint_hash + response_hash)

    Args:
        prompt: Input prompt string.
        request: Shaped local request (None if routed to Gemini).
        fingerprint: Infrastructure fingerprint.
        result: Gateway call result.

    Returns:
        64-character lowercase hex SHA256 digest.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_payload_hash

**Parameters**: self
**Returns**: str
**Description**: 
        Get the canonical payload hash derived from the exact bytes used for replay_hash computation.

        This reflects the combined canonical payload (prompt_hash + local_request_hash +
        fingerprint_hash + response_hash) before the final SHA-256.

        Returns:
            64-character lowercase hex SHA256 digest of the canonical payload.
        



## Function: verify

**Parameters**: self
**Returns**: bool
**Description**: 
        Verify that stored hashes match recomputed hashes.

        Returns:
            True if all hashes match (artifact is untampered), False otherwise.
        



## Function: validate

**Parameters**: self, artifact
**Returns**: bool
**Description**: 
        Validate a replay artifact.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            True if artifact is valid (untampered), False otherwise.
        



## Function: validate_and_report

**Parameters**: self, artifact
**Returns**: dict[str, Any]
**Description**: 
        Validate artifact and return detailed report.

        Args:
            artifact: VLLMReplayArtifact to validate.

        Returns:
            Dict with validation result and hash details.
        



## Usage Examples

### Class Usage

```python
# Using VLLMReplayArtifact
vllmreplayartifact = VLLMReplayArtifact()
vllmreplayartifact.canonical_payload_hash()
vllmreplayartifact.verify()
```

```python
# Using VLLMReplayValidator
vllmreplayvalidator = VLLMReplayValidator()
vllmreplayvalidator.validate()
vllmreplayvalidator.validate_and_report()
```

### Function Usage

```python
# Using canonical_prompt_hash
result = canonical_prompt_hash(prompt)
```

```python
# Using canonical_local_request_hash
result = canonical_local_request_hash(request)
```

```python
# Using canonical_response_hash
result = canonical_response_hash(result)
```



---
**Generated**: 2026-03-26T09:39:04.037379
**Type**: api_reference
**Quality**: comprehensive
