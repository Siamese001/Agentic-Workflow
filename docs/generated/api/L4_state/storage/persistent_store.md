# API Documentation: persistent_store

**Target Audience**: developers, api_users

# persistent_store API Documentation

**File**: `persistent_store.py`
**Classes**: 4
**Functions**: 7

## Classes

- **StoredArtifact**
- **StoreMetrics**
- **StoredArtifactRef**
- **StoreBackend** (inherits from Protocol)

## Functions

- **_sanitize_id** -> str
- **_canonicalize_payload** -> str
- **_compute_sha256** -> str
- **create_artifact** -> StoredArtifact
- **put** -> StoredArtifactRef
- **get** -> StoredArtifact
- **list** -> list[StoredArtifactRef]


## Class: StoredArtifact

**Description**: Immutable artifact definition for storage.



## Class: StoreMetrics

**Description**: Deterministic performance metrics for storage operations.



## Class: StoredArtifactRef

**Description**: Immutable reference to a stored artifact.



## Class: StoreBackend

**Description**: Protocol for storage backends.

**Inherits from**: Protocol

### Methods

#### put
**Parameters**: self, artifact
**Returns**: StoredArtifactRef
**Description**: Store an artifact and return its reference.

#### get
**Parameters**: self, ref
**Returns**: StoredArtifact
**Description**: Retrieve an artifact by reference.

#### list
**Parameters**: self, kind
**Returns**: list[StoredArtifactRef]
**Description**: List stored artifacts, optionally filtered by kind.



## Function: _sanitize_id

**Parameters**: identifier
**Returns**: str
**Description**: Sanitize identifier to prevent path traversal.

    Only allows alphanumeric, hyphen, underscore, and dot characters.
    



## Function: _canonicalize_payload

**Parameters**: payload
**Returns**: str
**Description**: Canonicalize payload to deterministic JSON string.



## Function: _compute_sha256

**Parameters**: data
**Returns**: str
**Description**: Compute SHA256 hash of data string.



## Function: create_artifact

**Parameters**: kind, logical_id, payload, content_type, created_utc, metadata
**Returns**: StoredArtifact
**Description**: Create a StoredArtifact with computed hashes.

    Args:
        kind: Artifact kind
        logical_id: Logical identifier
        payload: Artifact data
        content_type: Content type (default: application/json)
        created_utc: ISO timestamp (if None, uses current UTC time)
        metadata: Allowlisted metadata (filtered to allowed keys)

    Returns:
        StoredArtifact with computed hashes
    



## Function: put

**Parameters**: self, artifact
**Returns**: StoredArtifactRef
**Description**: Store an artifact and return its reference.



## Function: get

**Parameters**: self, ref
**Returns**: StoredArtifact
**Description**: Retrieve an artifact by reference.



## Function: list

**Parameters**: self, kind
**Returns**: list[StoredArtifactRef]
**Description**: List stored artifacts, optionally filtered by kind.



## Usage Examples

### Class Usage

```python
# Using StoredArtifact
storedartifact = StoredArtifact()
```

```python
# Using StoreMetrics
storemetrics = StoreMetrics()
```

```python
# Using StoredArtifactRef
storedartifactref = StoredArtifactRef()
```

### Function Usage

```python
# Using _sanitize_id
result = _sanitize_id(identifier)
```

```python
# Using _canonicalize_payload
result = _canonicalize_payload(payload)
```

```python
# Using _compute_sha256
result = _compute_sha256(data)
```



---
**Generated**: 2026-03-26T09:39:04.625548
**Type**: api_reference
**Quality**: comprehensive
