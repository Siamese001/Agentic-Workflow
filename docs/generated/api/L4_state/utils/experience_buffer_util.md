# API Documentation: experience_buffer_util

**Target Audience**: developers, api_users

# experience_buffer_util API Documentation

**File**: `experience_buffer_util.py`
**Classes**: 1
**Functions**: 8

## Classes

- **ExperienceBuffer**

## Functions

- **_get_write_gateway**
- **__init__**
- **record** -> None
- **_enforce_size_limit** -> None
- **load_all** -> list[dict[str, Any]]
- **find_similar** -> list[dict[str, Any]]
- **predict_success_probability** -> float
- **get_stats** -> dict[str, Any]


## Class: ExperienceBuffer

**Description**: 
    Lightweight, append-only experience replay buffer with JSONL persistence.
    Designed for sovereign agents to learn from healing/validation outcomes.
    

### Methods

#### __init__
**Parameters**: self, path, max_entries, similarity_keys
**Description**: 
        Initialize buffer with persistent storage.

        Args:
            path: File path for JSONL storage (e.g., logs/healer_experience.jsonl)
            max_entries: Maximum historical entries to retain
            similarity_keys: Keys used for similarity matching (default: all keys)
        

#### record
**Parameters**: self, entry
**Returns**: None
**Description**: 
        Record a new experience outcome.
        Appends to file and enforces size limit.
        

#### _enforce_size_limit
**Parameters**: self
**Returns**: None
**Description**: Trim file to max_entries by keeping newest lines.

#### load_all
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Load all entries (newest first).

#### find_similar
**Parameters**: self, action, target, context_hash, limit
**Returns**: list[dict[str, Any]]
**Description**: 
        Find historically similar experiences for success prediction.
        Matches on provided filters.
        

#### predict_success_probability
**Parameters**: self, action, target, context_hash
**Returns**: float
**Description**: 
        Predict success probability based on historical outcomes.
        Returns 0.5 if no relevant history.
        

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return buffer statistics for monitoring.



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: __init__

**Parameters**: self, path, max_entries, similarity_keys
**Description**: 
        Initialize buffer with persistent storage.

        Args:
            path: File path for JSONL storage (e.g., logs/healer_experience.jsonl)
            max_entries: Maximum historical entries to retain
            similarity_keys: Keys used for similarity matching (default: all keys)
        



## Function: record

**Parameters**: self, entry
**Returns**: None
**Description**: 
        Record a new experience outcome.
        Appends to file and enforces size limit.
        



## Function: _enforce_size_limit

**Parameters**: self
**Returns**: None
**Description**: Trim file to max_entries by keeping newest lines.



## Function: load_all

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Load all entries (newest first).



## Function: find_similar

**Parameters**: self, action, target, context_hash, limit
**Returns**: list[dict[str, Any]]
**Description**: 
        Find historically similar experiences for success prediction.
        Matches on provided filters.
        



## Function: predict_success_probability

**Parameters**: self, action, target, context_hash
**Returns**: float
**Description**: 
        Predict success probability based on historical outcomes.
        Returns 0.5 if no relevant history.
        



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return buffer statistics for monitoring.



## Usage Examples

### Class Usage

```python
# Using ExperienceBuffer
experiencebuffer = ExperienceBuffer()
experiencebuffer.record()
experiencebuffer.load_all()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using __init__
result = __init__(path, max_entries)
```

```python
# Using record
result = record(entry)
```



---
**Generated**: 2026-03-26T09:39:04.664807
**Type**: api_reference
**Quality**: comprehensive
