# API Documentation: sovereign_reasoning_memory_ledger

**Target Audience**: developers, api_users

# sovereign_reasoning_memory_ledger API Documentation

**File**: `sovereign_reasoning_memory_ledger.py`
**Classes**: 1
**Functions**: 5

## Classes

- **SovereignReasoningMemory** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **get_instance** -> SovereignReasoningMemory
- **add_thought** -> None
- **get_history** -> list[dict]
- **heal**


## Class: SovereignReasoningMemory

**Description**: 
    Ultra-hardened sovereign manager for cognitive artifacts.
    Inherits Redis connection from SovereignBaseAgent -> RedisCacheMixin.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self

#### get_instance
**Parameters**: cls
**Returns**: SovereignReasoningMemory

#### add_thought
**Parameters**: self, file_path, thought, key_id
**Returns**: None

#### get_history
**Parameters**: self, file_path
**Returns**: list[dict]

#### heal
**Parameters**: self, violation



## Function: __init__

**Parameters**: self


## Function: get_instance

**Parameters**: cls
**Returns**: SovereignReasoningMemory


## Function: add_thought

**Parameters**: self, file_path, thought, key_id
**Returns**: None


## Function: get_history

**Parameters**: self, file_path
**Returns**: list[dict]


## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using SovereignReasoningMemory
sovereignreasoningmemory = SovereignReasoningMemory()
sovereignreasoningmemory.get_instance()
sovereignreasoningmemory.add_thought()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using get_instance
result = get_instance(cls)
```

```python
# Using add_thought
result = add_thought(file_path, thought)
```



---
**Generated**: 2026-03-26T09:39:04.596167
**Type**: api_reference
**Quality**: comprehensive
