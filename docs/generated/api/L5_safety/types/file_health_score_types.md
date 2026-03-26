# API Documentation: file_health_score_types

**Target Audience**: developers, api_users

# file_health_score_types API Documentation

**File**: `file_health_score_types.py`
**Classes**: 3
**Functions**: 12

## Classes

- **FileHealthScore**
- **HealingLease**
- **AtomicBlackboard** (inherits from SovereignBaseAgent)

## Functions

- **get_blackboard** -> AtomicBlackboard
- **to_dict** -> dict
- **from_dict** -> FileHealthScore
- **is_expired** -> bool
- **__init__**
- **acquire_lease** -> HealingLease | None
- **release_lease** -> bool
- **get_health_score** -> FileHealthScore | None
- **update_health_score** -> FileHealthScore
- **record_anomaly** -> None
- **get_file_hash** -> str
- **should_heal** -> bool


## Class: FileHealthScore

**Description**: Health score for a single file.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict

#### from_dict
**Parameters**: cls, data
**Returns**: FileHealthScore



## Class: HealingLease

### Methods

#### is_expired
**Parameters**: self
**Returns**: bool



## Class: AtomicBlackboard

**Description**: 
    Thread-safe blackboard using Sovereign Infrastructure.
    Inherits Redis/Pinecone connections from SovereignBaseAgent.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self

#### acquire_lease
**Parameters**: self, file_path, agent_name
**Returns**: HealingLease | None

#### release_lease
**Parameters**: self, lease
**Returns**: bool

#### get_health_score
**Parameters**: self, file_path
**Returns**: FileHealthScore | None

#### update_health_score
**Parameters**: self, file_path, violations, file_hash
**Returns**: FileHealthScore

#### record_anomaly
**Parameters**: self, anomaly
**Returns**: None
**Description**: Record an anomaly to the blackboard.

#### get_file_hash
**Parameters**: self, file_path
**Returns**: str
**Description**: Get hash of file contents.

#### should_heal
**Parameters**: self, file_path
**Returns**: bool
**Description**: Determine if a file should be healed based on health score.



## Function: get_blackboard

**Returns**: AtomicBlackboard


## Function: to_dict

**Parameters**: self
**Returns**: dict


## Function: from_dict

**Parameters**: cls, data
**Returns**: FileHealthScore


## Function: is_expired

**Parameters**: self
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: acquire_lease

**Parameters**: self, file_path, agent_name
**Returns**: HealingLease | None


## Function: release_lease

**Parameters**: self, lease
**Returns**: bool


## Function: get_health_score

**Parameters**: self, file_path
**Returns**: FileHealthScore | None


## Function: update_health_score

**Parameters**: self, file_path, violations, file_hash
**Returns**: FileHealthScore


## Function: record_anomaly

**Parameters**: self, anomaly
**Returns**: None
**Description**: Record an anomaly to the blackboard.



## Function: get_file_hash

**Parameters**: self, file_path
**Returns**: str
**Description**: Get hash of file contents.



## Function: should_heal

**Parameters**: self, file_path
**Returns**: bool
**Description**: Determine if a file should be healed based on health score.



## Usage Examples

### Class Usage

```python
# Using FileHealthScore
filehealthscore = FileHealthScore()
filehealthscore.to_dict()
filehealthscore.from_dict()
```

```python
# Using HealingLease
healinglease = HealingLease()
healinglease.is_expired()
```

```python
# Using AtomicBlackboard
atomicblackboard = AtomicBlackboard()
atomicblackboard.acquire_lease()
atomicblackboard.release_lease()
```

### Function Usage

```python
# Using get_blackboard
result = get_blackboard()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using from_dict
result = from_dict(cls, data)
```



---
**Generated**: 2026-03-26T09:39:05.505258
**Type**: api_reference
**Quality**: comprehensive
