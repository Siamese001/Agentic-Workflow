# API Documentation: reasoning_memory

**Target Audience**: developers, api_users

# reasoning_memory API Documentation

**File**: `reasoning_memory.py`
**Classes**: 2
**Functions**: 15

## Classes

- **Thought**
- **ReasoningMemory**

## Functions

- **__init__**
- **semantic_memory**
- **store** -> str
- **retrieve** -> list[dict[str, Any]]
- **retrieve_relevant** -> list[dict[str, Any]]
- **retrieve_by_type** -> list[dict[str, Any]]
- **retrieve_high_confidence** -> list[dict[str, Any]]
- **_keyword_search** -> list[dict[str, Any]]
- **_is_duplicate** -> bool
- **_generate_id** -> str
- **_thought_to_dict** -> dict[str, Any]
- **_persist_thought** -> None
- **_load_persistent** -> None
- **clear** -> None
- **get_statistics** -> dict[str, Any]


## Class: Thought

**Description**: Individual thought entry.



## Class: ReasoningMemory

**Description**: 
    Expanded Reasoning Memory - Short-term thought storage with persistence.

    Provides:
    - Expanded capacity (500 thoughts vs original 50)
    - LRU eviction with semantic memory offload
    - Persistence to ledger/file
    - Relevance-based retrieval
    

### Methods

#### __init__
**Parameters**: self, capacity, persist, semantic_offload
**Description**: 
        Initialize reasoning memory.

        Args:
            capacity: Maximum thoughts in memory (default 500, up from 50)
            persist: Whether to persist thoughts
            semantic_offload: Whether to offload evicted thoughts to semantic memory
        

#### semantic_memory
**Parameters**: self
**Description**: Lazy load semantic memory.

#### store
**Parameters**: self, thought
**Returns**: str
**Description**: 
        Store a thought in memory.

        Args:
            thought: Thought dictionary with content, type, etc.

        Returns:
            Thought ID
        

#### retrieve
**Parameters**: self, count
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve recent thoughts.

        Args:
            count: Number of thoughts to retrieve

        Returns:
            List of thought dictionaries
        

#### retrieve_relevant
**Parameters**: self, query, top_k
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve relevant thoughts using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of relevant thoughts
        

#### retrieve_by_type
**Parameters**: self, thought_type, count
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve thoughts by type.

        Args:
            thought_type: Type to filter by
            count: Number of results

        Returns:
            List of matching thoughts
        

#### retrieve_high_confidence
**Parameters**: self, threshold, count
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve high-confidence thoughts.

        Args:
            threshold: Minimum confidence
            count: Number of results

        Returns:
            List of high-confidence thoughts
        

#### _keyword_search
**Parameters**: self, query, top_k
**Returns**: list[dict[str, Any]]
**Description**: Simple keyword-based search in memory.

#### _is_duplicate
**Parameters**: self, result, existing
**Returns**: bool
**Description**: Check if result is duplicate of existing.

#### _generate_id
**Parameters**: self, thought
**Returns**: str
**Description**: Generate unique ID for thought.

#### _thought_to_dict
**Parameters**: self, thought
**Returns**: dict[str, Any]
**Description**: Convert thought object to dictionary.

#### _persist_thought
**Parameters**: self, thought
**Returns**: None
**Description**: Persist thought to storage.

#### _load_persistent
**Parameters**: self
**Returns**: None
**Description**: Load thoughts from persistent storage.

#### clear
**Parameters**: self
**Returns**: None
**Description**: Clear all thoughts.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get memory statistics.



## Function: __init__

**Parameters**: self, capacity, persist, semantic_offload
**Description**: 
        Initialize reasoning memory.

        Args:
            capacity: Maximum thoughts in memory (default 500, up from 50)
            persist: Whether to persist thoughts
            semantic_offload: Whether to offload evicted thoughts to semantic memory
        



## Function: semantic_memory

**Parameters**: self
**Description**: Lazy load semantic memory.



## Function: store

**Parameters**: self, thought
**Returns**: str
**Description**: 
        Store a thought in memory.

        Args:
            thought: Thought dictionary with content, type, etc.

        Returns:
            Thought ID
        



## Function: retrieve

**Parameters**: self, count
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve recent thoughts.

        Args:
            count: Number of thoughts to retrieve

        Returns:
            List of thought dictionaries
        



## Function: retrieve_relevant

**Parameters**: self, query, top_k
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve relevant thoughts using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of relevant thoughts
        



## Function: retrieve_by_type

**Parameters**: self, thought_type, count
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve thoughts by type.

        Args:
            thought_type: Type to filter by
            count: Number of results

        Returns:
            List of matching thoughts
        



## Function: retrieve_high_confidence

**Parameters**: self, threshold, count
**Returns**: list[dict[str, Any]]
**Description**: 
        Retrieve high-confidence thoughts.

        Args:
            threshold: Minimum confidence
            count: Number of results

        Returns:
            List of high-confidence thoughts
        



## Function: _keyword_search

**Parameters**: self, query, top_k
**Returns**: list[dict[str, Any]]
**Description**: Simple keyword-based search in memory.



## Function: _is_duplicate

**Parameters**: self, result, existing
**Returns**: bool
**Description**: Check if result is duplicate of existing.



## Function: _generate_id

**Parameters**: self, thought
**Returns**: str
**Description**: Generate unique ID for thought.



## Function: _thought_to_dict

**Parameters**: self, thought
**Returns**: dict[str, Any]
**Description**: Convert thought object to dictionary.



## Function: _persist_thought

**Parameters**: self, thought
**Returns**: None
**Description**: Persist thought to storage.



## Function: _load_persistent

**Parameters**: self
**Returns**: None
**Description**: Load thoughts from persistent storage.



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Clear all thoughts.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get memory statistics.



## Usage Examples

### Class Usage

```python
# Using Thought
thought = Thought()
```

```python
# Using ReasoningMemory
reasoningmemory = ReasoningMemory()
reasoningmemory.semantic_memory()
reasoningmemory.store()
```

### Function Usage

```python
# Using __init__
result = __init__(capacity, persist)
```

```python
# Using semantic_memory
result = semantic_memory()
```

```python
# Using store
result = store(thought)
```



---
**Generated**: 2026-03-26T09:39:04.582976
**Type**: api_reference
**Quality**: comprehensive
