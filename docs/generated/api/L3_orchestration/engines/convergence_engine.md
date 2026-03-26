# API Documentation: convergence_engine

**Target Audience**: developers, api_users

# convergence_engine API Documentation

**File**: `convergence_engine.py`
**Classes**: 1
**Functions**: 3

## Classes

- **ConvergenceEngine**

## Functions

- **__init__**
- **get_file_hash** -> str
- **detect_fission** -> bool


## Class: ConvergenceEngine

### Methods

#### __init__
**Parameters**: self, max_rounds

#### get_file_hash
**Parameters**: self, file_path
**Returns**: str
**Description**: 
        SSOT SNAPSHOTTING: Generates SHA256 hash for fission detection.
        

#### detect_fission
**Parameters**: self, pre_hash, post_hash, file_size
**Returns**: bool
**Description**: 
        FISSION DETECTION: Triggers if a large file fails to change after healing.
        



## Function: __init__

**Parameters**: self, max_rounds


## Function: get_file_hash

**Parameters**: self, file_path
**Returns**: str
**Description**: 
        SSOT SNAPSHOTTING: Generates SHA256 hash for fission detection.
        



## Function: detect_fission

**Parameters**: self, pre_hash, post_hash, file_size
**Returns**: bool
**Description**: 
        FISSION DETECTION: Triggers if a large file fails to change after healing.
        



## Usage Examples

### Class Usage

```python
# Using ConvergenceEngine
convergenceengine = ConvergenceEngine()
convergenceengine.get_file_hash()
convergenceengine.detect_fission()
```

### Function Usage

```python
# Using __init__
result = __init__(max_rounds)
```

```python
# Using get_file_hash
result = get_file_hash(file_path)
```

```python
# Using detect_fission
result = detect_fission(pre_hash, post_hash)
```



---
**Generated**: 2026-03-26T09:39:04.149035
**Type**: api_reference
**Quality**: comprehensive
