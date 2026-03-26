# API Documentation: config_store_types

**Target Audience**: developers, api_users

# config_store_types API Documentation

**File**: `config_store_types.py`
**Classes**: 2
**Functions**: 12

## Classes

- **ConfigSnapshotArtifact**
- **ConfigDeltaArtifact**

## Functions

- **_get_MUTABLE_COMPONENTS**
- **canonical_json** -> str
- **stable_sha256** -> str
- **validate_component_allowed** -> None
- **build_config_snapshot** -> ConfigSnapshotArtifact
- **build_config_delta** -> ConfigDeltaArtifact
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **to_json** -> str
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **to_json** -> str


## Class: ConfigSnapshotArtifact

**Description**: Frozen, schema-locked versioned config snapshot.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical, deterministic serialization.

#### to_json
**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON string.



## Class: ConfigDeltaArtifact

**Description**: Frozen, schema-locked computed diff between two config versions.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical, deterministic serialization.

#### to_json
**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON string.



## Function: _get_MUTABLE_COMPONENTS



## Function: canonical_json

**Parameters**: obj
**Returns**: str
**Description**: Deterministic JSON: sorted keys recursively, compact separators.



## Function: stable_sha256

**Parameters**: text
**Returns**: str
**Description**: Deterministic SHA-256 hex digest of a UTF-8 encoded string.



## Function: validate_component_allowed

**Parameters**: component
**Returns**: None
**Description**: Raise ValueError if *component* is not in MUTABLE_COMPONENTS (L7 SSOT).



## Function: build_config_snapshot

**Returns**: ConfigSnapshotArtifact
**Description**: Build a ConfigSnapshotArtifact with deterministic trace_id.



## Function: build_config_delta

**Returns**: ConfigDeltaArtifact
**Description**: Build a ConfigDeltaArtifact with deterministic trace_id.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical, deterministic serialization.



## Function: to_json

**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON string.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical, deterministic serialization.



## Function: to_json

**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON string.



## Usage Examples

### Class Usage

```python
# Using ConfigSnapshotArtifact
configsnapshotartifact = ConfigSnapshotArtifact()
configsnapshotartifact.to_dict()
configsnapshotartifact.to_json()
```

```python
# Using ConfigDeltaArtifact
configdeltaartifact = ConfigDeltaArtifact()
configdeltaartifact.to_dict()
configdeltaartifact.to_json()
```

### Function Usage

```python
# Using _get_MUTABLE_COMPONENTS
result = _get_MUTABLE_COMPONENTS()
```

```python
# Using canonical_json
result = canonical_json(obj)
```

```python
# Using stable_sha256
result = stable_sha256(text)
```



---
**Generated**: 2026-03-26T09:39:02.680804
**Type**: api_reference
**Quality**: comprehensive
