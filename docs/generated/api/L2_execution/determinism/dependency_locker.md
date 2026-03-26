# API Documentation: dependency_locker

**Target Audience**: developers, api_users

# dependency_locker API Documentation

**File**: `dependency_locker.py`
**Classes**: 1
**Functions**: 4

## Classes

- **DependencyLocker**

## Functions

- **generate_lock_hash** -> str
- **save_lock_file** -> None
- **load_lock_hash** -> str
- **validate** -> bool


## Class: DependencyLocker

**Description**: Manages the dependency lock hash used in determinism digests.

### Methods

#### generate_lock_hash
**Parameters**: cls, requirements_path
**Returns**: str
**Description**: Return SHA-256 hash of pinned dependencies from *requirements_path*.

#### save_lock_file
**Parameters**: cls, lock_hash, lock_file_path
**Returns**: None
**Description**: Persist *lock_hash* to *lock_file_path* (creates parents if needed).

#### load_lock_hash
**Parameters**: cls, lock_file_path
**Returns**: str
**Description**: Load and return the stored lock hash.

#### validate
**Parameters**: cls, requirements_path, lock_file_path
**Returns**: bool
**Description**: Return True if current dependencies match the stored lock hash.

        If no lock file exists, generate one and return True.
        



## Function: generate_lock_hash

**Parameters**: cls, requirements_path
**Returns**: str
**Description**: Return SHA-256 hash of pinned dependencies from *requirements_path*.



## Function: save_lock_file

**Parameters**: cls, lock_hash, lock_file_path
**Returns**: None
**Description**: Persist *lock_hash* to *lock_file_path* (creates parents if needed).



## Function: load_lock_hash

**Parameters**: cls, lock_file_path
**Returns**: str
**Description**: Load and return the stored lock hash.



## Function: validate

**Parameters**: cls, requirements_path, lock_file_path
**Returns**: bool
**Description**: Return True if current dependencies match the stored lock hash.

        If no lock file exists, generate one and return True.
        



## Usage Examples

### Class Usage

```python
# Using DependencyLocker
dependencylocker = DependencyLocker()
dependencylocker.generate_lock_hash()
dependencylocker.save_lock_file()
```

### Function Usage

```python
# Using generate_lock_hash
result = generate_lock_hash(cls, requirements_path)
```

```python
# Using save_lock_file
result = save_lock_file(cls, lock_hash)
```

```python
# Using load_lock_hash
result = load_lock_hash(cls, lock_file_path)
```



---
**Generated**: 2026-03-26T09:39:03.662112
**Type**: api_reference
**Quality**: comprehensive
