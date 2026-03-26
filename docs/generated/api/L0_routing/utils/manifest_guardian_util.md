# API Documentation: manifest_guardian_util

**Target Audience**: developers, api_users

# manifest_guardian_util API Documentation

**File**: `manifest_guardian_util.py`
**Classes**: 1
**Functions**: 3

## Classes

- **ManifestGuardian**

## Functions

- **calculate_checksum** -> str
- **seal_manifest** -> str
- **verify_integrity** -> bool


## Class: ManifestGuardian

**Description**: 
    L0 Security Component: SSOT Integrity Enforcer.

    Responsibilities:
    1. Generate SHA-256 checksums of the manifest.json.
    2. Validate runtime manifest against the frozen boot checksum.
    3. Lock the manifest file system permissions (Linux/Unix).
    

### Methods

#### calculate_checksum
**Parameters**: file_path
**Returns**: str
**Description**: Calculates the SHA-256 checksum of the manifest file.

#### seal_manifest
**Parameters**: cls
**Returns**: str
**Description**: Generates the lock file containing the authoritative checksum.

#### verify_integrity
**Parameters**: cls
**Returns**: bool
**Description**: 
        Compares current manifest state against the .lock file.
        Returns True if integrity is preserved, False otherwise.
        



## Function: calculate_checksum

**Parameters**: file_path
**Returns**: str
**Description**: Calculates the SHA-256 checksum of the manifest file.



## Function: seal_manifest

**Parameters**: cls
**Returns**: str
**Description**: Generates the lock file containing the authoritative checksum.



## Function: verify_integrity

**Parameters**: cls
**Returns**: bool
**Description**: 
        Compares current manifest state against the .lock file.
        Returns True if integrity is preserved, False otherwise.
        



## Usage Examples

### Class Usage

```python
# Using ManifestGuardian
manifestguardian = ManifestGuardian()
manifestguardian.calculate_checksum()
manifestguardian.seal_manifest()
```

### Function Usage

```python
# Using calculate_checksum
result = calculate_checksum(file_path)
```

```python
# Using seal_manifest
result = seal_manifest(cls)
```

```python
# Using verify_integrity
result = verify_integrity(cls)
```



---
**Generated**: 2026-03-26T09:39:03.536234
**Type**: api_reference
**Quality**: comprehensive
