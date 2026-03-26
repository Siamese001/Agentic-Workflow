# API Documentation: replay_envelope_types

**Target Audience**: developers, api_users

# replay_envelope_types API Documentation

**File**: `replay_envelope_types.py`
**Classes**: 1
**Functions**: 4

## Classes

- **ReplayEnvelope**

## Functions

- **create_deterministic_cache_key** -> str
- **to_canonical_json** -> str
- **get_digest** -> str
- **from_generation_context** -> 'ReplayEnvelope'


## Class: ReplayEnvelope

**Description**: Canonical replay envelope for deterministic generation tracking.

### Methods

#### to_canonical_json
**Parameters**: self
**Returns**: str
**Description**: Generate canonical JSON representation with deterministic ordering.

#### get_digest
**Parameters**: self
**Returns**: str
**Description**: Get SHA256 digest of canonical JSON representation.

#### from_generation_context
**Parameters**: cls, routing_hash, manifest_hash, model_id, model_version, temperature, policy_version, gateway_version, embedder_provider, embedder_model, embedder_dim, agent_registry_hash, deterministic_engine_version, allowed_model_policy_version, normalization_policy, chunking_policy, distance_metric, retrieval_top_k, retrieval_similarity_cutoff, code_commit_hash
**Returns**: 'ReplayEnvelope'
**Description**: Create ReplayEnvelope from generation context parameters.



## Function: create_deterministic_cache_key

**Parameters**: text, embedder_identity
**Returns**: str
**Description**: Create deterministic cache key for embeddings.



## Function: to_canonical_json

**Parameters**: self
**Returns**: str
**Description**: Generate canonical JSON representation with deterministic ordering.



## Function: get_digest

**Parameters**: self
**Returns**: str
**Description**: Get SHA256 digest of canonical JSON representation.



## Function: from_generation_context

**Parameters**: cls, routing_hash, manifest_hash, model_id, model_version, temperature, policy_version, gateway_version, embedder_provider, embedder_model, embedder_dim, agent_registry_hash, deterministic_engine_version, allowed_model_policy_version, normalization_policy, chunking_policy, distance_metric, retrieval_top_k, retrieval_similarity_cutoff, code_commit_hash
**Returns**: 'ReplayEnvelope'
**Description**: Create ReplayEnvelope from generation context parameters.



## Usage Examples

### Class Usage

```python
# Using ReplayEnvelope
replayenvelope = ReplayEnvelope()
replayenvelope.to_canonical_json()
replayenvelope.get_digest()
```

### Function Usage

```python
# Using create_deterministic_cache_key
result = create_deterministic_cache_key(text, embedder_identity)
```

```python
# Using to_canonical_json
result = to_canonical_json()
```

```python
# Using get_digest
result = get_digest()
```



---
**Generated**: 2026-03-26T09:39:03.997305
**Type**: api_reference
**Quality**: comprehensive
