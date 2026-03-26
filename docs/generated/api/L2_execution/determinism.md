# API Documentation: determinism

**Target Audience**: developers, api_users

# determinism API Documentation

**File**: `determinism.py`
**Classes**: 0
**Functions**: 14


## Functions

- **_sha256_bytes** -> str
- **_canonical_json** -> str
- **_file_hash** -> str
- **_load_json** -> dict
- **compute_provider_binding_determinism_digest** -> str
- **compute_p5_determinism_digest** -> str
- **build_agent_2x2_inventory** -> dict
- **write_agent_2x2_inventory** -> Path
- **compute_w6_determinism_digest** -> str
- **generate_determinism_digest** -> str
- **compute_lockdown_determinism_digest** -> str
- **get_embedding_config_surface** -> dict
- **get_meta_learning_config_surface** -> dict
- **generate_lockdown_determinism_digest** -> str


## Function: _sha256_bytes

**Parameters**: data
**Returns**: str


## Function: _canonical_json

**Parameters**: obj
**Returns**: str


## Function: _file_hash

**Parameters**: path
**Returns**: str


## Function: _load_json

**Parameters**: path
**Returns**: dict


## Function: compute_provider_binding_determinism_digest

**Parameters**: provider_id, model_id, semantic_clock, additional_context
**Returns**: str
**Description**: Compute provider binding determinism digest (REQ-413).

    Args:
        provider_id: LLM provider identifier
        model_id: Model identifier
        semantic_clock: Current semantic clock snapshot
        additional_context: Optional additional context

    Returns:
        SHA-256 hex digest including provider binding information
    



## Function: compute_p5_determinism_digest

**Returns**: str
**Description**: Compute stable P5 determinism digest (64-char hex).



## Function: build_agent_2x2_inventory

**Returns**: dict
**Description**: Build canonical Phase 6 fleet inventory document.



## Function: write_agent_2x2_inventory

**Parameters**: path
**Returns**: Path
**Description**: Write canonical fleet inventory artifact JSON and return file path.



## Function: compute_w6_determinism_digest

**Returns**: str
**Description**: Compute stable W6 digest from canonical inventory + policy surface.



## Function: generate_determinism_digest

**Returns**: str
**Description**: Backward-compatible Phase 5 digest API.



## Function: compute_lockdown_determinism_digest

**Returns**: str
**Description**: Compute comprehensive HARDEN-MERGE-LOCKDOWN determinism digest.



## Function: get_embedding_config_surface

**Returns**: dict
**Description**: Get embedding configuration surface for determinism.



## Function: get_meta_learning_config_surface

**Returns**: dict
**Description**: Get meta-learning configuration surface for determinism.



## Function: generate_lockdown_determinism_digest

**Returns**: str
**Description**: Generate HARDEN-MERGE-LOCKDOWN determinism digest with emission format.



## Usage Examples

### Function Usage

```python
# Using _sha256_bytes
result = _sha256_bytes(data)
```

```python
# Using _canonical_json
result = _canonical_json(obj)
```

```python
# Using _file_hash
result = _file_hash(path)
```



---
**Generated**: 2026-03-26T09:39:03.570609
**Type**: api_reference
**Quality**: comprehensive
