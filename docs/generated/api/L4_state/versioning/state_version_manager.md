# API Documentation: state_version_manager

**Target Audience**: developers, api_users

# state_version_manager API Documentation

**File**: `state_version_manager.py`
**Classes**: 2
**Functions**: 10

## Classes

- **StateVersion**
- **StateVersionManager**

## Functions

- **_hash_state** -> str
- **get_version_manager** -> StateVersionManager
- **release_version_manager** -> None
- **__init__** -> None
- **commit** -> StateVersion
- **current_version** -> StateVersion | None
- **rollback** -> StateVersion | None
- **diff** -> dict[str, Any]
- **history** -> list[StateVersion]
- **version_count** -> int


## Class: StateVersion

**Description**: Single immutable version in the state chain.



## Class: StateVersionManager

**Description**: Immutable versioned state chain.

    Usage::

        mgr = StateVersionManager("campaign-brief-run")
        mgr.commit({"context": "..."}, author="ResearchAgent")
        mgr.commit({"context": "...", "budget": 500}, author="PlannerAgent")

        v = mgr.current_version()
        print(v.version_id, v.state_hash)

        # rollback to previous version
        mgr.rollback(v.parent_id)
    

### Methods

#### __init__
**Parameters**: self, run_id
**Returns**: None

#### commit
**Parameters**: self, state, author, metadata
**Returns**: StateVersion
**Description**: Commit a new state version to the chain.

        Emits ``snapshots_state`` + ``version_chain_appended`` ADG edges.
        

#### current_version
**Parameters**: self
**Returns**: StateVersion | None

#### rollback
**Parameters**: self, target_version_id
**Returns**: StateVersion | None
**Description**: Rollback to a previous version by version_id.

        Emits ``rollback_vector`` ADG edge.
        

#### diff
**Parameters**: self, v1_id, v2_id
**Returns**: dict[str, Any]
**Description**: Return changed keys between two versions.

#### history
**Parameters**: self
**Returns**: list[StateVersion]

#### version_count
**Parameters**: self
**Returns**: int



## Function: _hash_state

**Parameters**: state
**Returns**: str


## Function: get_version_manager

**Parameters**: run_id
**Returns**: StateVersionManager


## Function: release_version_manager

**Parameters**: run_id
**Returns**: None


## Function: __init__

**Parameters**: self, run_id
**Returns**: None


## Function: commit

**Parameters**: self, state, author, metadata
**Returns**: StateVersion
**Description**: Commit a new state version to the chain.

        Emits ``snapshots_state`` + ``version_chain_appended`` ADG edges.
        



## Function: current_version

**Parameters**: self
**Returns**: StateVersion | None


## Function: rollback

**Parameters**: self, target_version_id
**Returns**: StateVersion | None
**Description**: Rollback to a previous version by version_id.

        Emits ``rollback_vector`` ADG edge.
        



## Function: diff

**Parameters**: self, v1_id, v2_id
**Returns**: dict[str, Any]
**Description**: Return changed keys between two versions.



## Function: history

**Parameters**: self
**Returns**: list[StateVersion]


## Function: version_count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using StateVersion
stateversion = StateVersion()
```

```python
# Using StateVersionManager
stateversionmanager = StateVersionManager()
stateversionmanager.commit()
stateversionmanager.current_version()
```

### Function Usage

```python
# Using _hash_state
result = _hash_state(state)
```

```python
# Using get_version_manager
result = get_version_manager(run_id)
```

```python
# Using release_version_manager
result = release_version_manager(run_id)
```



---
**Generated**: 2026-03-26T09:39:04.692027
**Type**: api_reference
**Quality**: comprehensive
