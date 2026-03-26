# API Documentation: filesystem_store

**Target Audience**: developers, api_users

# filesystem_store API Documentation

**File**: `filesystem_store.py`
**Classes**: 1
**Functions**: 8

## Classes

- **FileSystemStore**

## Functions

- **__init__**
- **_get_artifact_dir** -> Path
- **_get_next_version** -> int
- **_get_artifact_path** -> Path
- **_validate_artifact** -> None
- **put** -> StoredArtifactRef
- **get** -> StoredArtifact
- **list** -> list[StoredArtifactRef]


## Class: FileSystemStore

**Description**: Local filesystem storage backend with append-only semantics.

### Methods

#### __init__
**Parameters**: self, root_dir, max_artifact_size
**Description**: Initialize filesystem store.

        Args:
            root_dir: Root directory for storage
            max_artifact_size: Maximum artifact size in bytes (default: 5MB)
        

#### _get_artifact_dir
**Parameters**: self, kind, logical_id
**Returns**: Path
**Description**: Get directory for a specific artifact type and ID.

#### _get_next_version
**Parameters**: self, artifact_dir
**Returns**: int
**Description**: Get next version number for artifact directory.

#### _get_artifact_path
**Parameters**: self, artifact_dir, version
**Returns**: Path
**Description**: Get file path for specific version.

#### _validate_artifact
**Parameters**: self, artifact
**Returns**: None
**Description**: Validate artifact before storage.

#### put
**Parameters**: self, artifact
**Returns**: StoredArtifactRef
**Description**: Store an artifact and return its reference.

        Args:
            artifact: Artifact to store

        Returns:
            Reference to stored artifact

        Raises:
            ValueError: If artifact validation fails
            OSError: If filesystem operation fails
        

#### get
**Parameters**: self, ref
**Returns**: StoredArtifact
**Description**: Retrieve an artifact by reference.

        Args:
            ref: Artifact reference

        Returns:
            Retrieved artifact

        Raises:
            FileNotFoundError: If artifact doesn't exist
            ValueError: If artifact data is invalid
        

#### list
**Parameters**: self, kind, limit
**Returns**: list[StoredArtifactRef]
**Description**: List stored artifacts, optionally filtered by kind and limited.

        Args:
            kind: Filter by artifact kind (if None, list all)
            limit: Maximum number of results to return (if None, return all)

        Returns:
            List of artifact references, deterministically sorted and limited
        



## Function: __init__

**Parameters**: self, root_dir, max_artifact_size
**Description**: Initialize filesystem store.

        Args:
            root_dir: Root directory for storage
            max_artifact_size: Maximum artifact size in bytes (default: 5MB)
        



## Function: _get_artifact_dir

**Parameters**: self, kind, logical_id
**Returns**: Path
**Description**: Get directory for a specific artifact type and ID.



## Function: _get_next_version

**Parameters**: self, artifact_dir
**Returns**: int
**Description**: Get next version number for artifact directory.



## Function: _get_artifact_path

**Parameters**: self, artifact_dir, version
**Returns**: Path
**Description**: Get file path for specific version.



## Function: _validate_artifact

**Parameters**: self, artifact
**Returns**: None
**Description**: Validate artifact before storage.



## Function: put

**Parameters**: self, artifact
**Returns**: StoredArtifactRef
**Description**: Store an artifact and return its reference.

        Args:
            artifact: Artifact to store

        Returns:
            Reference to stored artifact

        Raises:
            ValueError: If artifact validation fails
            OSError: If filesystem operation fails
        



## Function: get

**Parameters**: self, ref
**Returns**: StoredArtifact
**Description**: Retrieve an artifact by reference.

        Args:
            ref: Artifact reference

        Returns:
            Retrieved artifact

        Raises:
            FileNotFoundError: If artifact doesn't exist
            ValueError: If artifact data is invalid
        



## Function: list

**Parameters**: self, kind, limit
**Returns**: list[StoredArtifactRef]
**Description**: List stored artifacts, optionally filtered by kind and limited.

        Args:
            kind: Filter by artifact kind (if None, list all)
            limit: Maximum number of results to return (if None, return all)

        Returns:
            List of artifact references, deterministically sorted and limited
        



## Usage Examples

### Class Usage

```python
# Using FileSystemStore
filesystemstore = FileSystemStore()
filesystemstore.put()
filesystemstore.get()
```

### Function Usage

```python
# Using __init__
result = __init__(root_dir, max_artifact_size)
```

```python
# Using _get_artifact_dir
result = _get_artifact_dir(kind, logical_id)
```

```python
# Using _get_next_version
result = _get_next_version(artifact_dir)
```



---
**Generated**: 2026-03-26T09:39:04.622945
**Type**: api_reference
**Quality**: comprehensive
