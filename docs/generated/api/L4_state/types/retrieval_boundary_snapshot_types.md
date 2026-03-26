# API Documentation: retrieval_boundary_snapshot_types

**Target Audience**: developers, api_users

# retrieval_boundary_snapshot_types API Documentation

**File**: `retrieval_boundary_snapshot_types.py`
**Classes**: 2
**Functions**: 9

## Classes

- **AnchorEntry**
- **RetrievalBoundarySnapshot**

## Functions

- **_sha256** -> str
- **build_request_hash** -> str
- **create_retrieval_boundary_snapshot** -> RetrievalBoundarySnapshot
- **__post_init__** -> None
- **to_dict** -> dict[str, str]
- **sort_key** -> tuple[str, str]
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **to_dict** -> dict[str, Any]


## Class: AnchorEntry

**Description**: 
    Minimal anchor identifier included in the snapshot.
    Carries chunk_id and version_hash for deterministic ordering.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, str]

#### sort_key
**Parameters**: self
**Returns**: tuple[str, str]



## Class: RetrievalBoundarySnapshot

**Description**: 
    Non-mutating boundary record produced at the start of every retrieval.

    Fields
    ------
    schema_version      : int  — bumped on breaking schema changes
    mission_id          : str  — non-empty identifier for the mission/run
    request_hash        : str  — sha256 of the canonical retrieval request subset
    active_config_hashes: dict — {"policy_hash": ..., "routing_hash": ..., ...}
    anchors             : list — sorted AnchorEntry records (chunk_id, version_hash)
    created_at_utc      : str  — ISO-8601 UTC timestamp (stable, no uuid/elapsed)
    snapshot_hash       : str  — sha256(canonical_bytes()); auto-computed
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding snapshot_hash (self-referential).
        Keys sorted, anchors sorted by (chunk_id, version_hash).
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: build_request_hash

**Parameters**: query, top_k, domain
**Returns**: str
**Description**: 
    Compute a deterministic sha256 hash of the canonical retrieval request subset.
    Excludes volatile fields (timestamps, trace IDs).
    



## Function: create_retrieval_boundary_snapshot

**Parameters**: mission_id, query, top_k, domain, active_config_hashes, anchors, created_at_utc
**Returns**: RetrievalBoundarySnapshot
**Description**: 
    Factory: build a RetrievalBoundarySnapshot from retrieval parameters.

    Non-mutating — does not write to any persistent store.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, str]


## Function: sort_key

**Parameters**: self
**Returns**: tuple[str, str]


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: 
        Deterministic serialisation excluding snapshot_hash (self-referential).
        Keys sorted, anchors sorted by (chunk_id, version_hash).
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using AnchorEntry
anchorentry = AnchorEntry()
anchorentry.to_dict()
anchorentry.sort_key()
```

```python
# Using RetrievalBoundarySnapshot
retrievalboundarysnapshot = RetrievalBoundarySnapshot()
retrievalboundarysnapshot.canonical_bytes()
retrievalboundarysnapshot.to_dict()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using build_request_hash
result = build_request_hash(query, top_k)
```

```python
# Using create_retrieval_boundary_snapshot
result = create_retrieval_boundary_snapshot(mission_id, query)
```



---
**Generated**: 2026-03-26T09:39:04.646232
**Type**: api_reference
**Quality**: comprehensive
