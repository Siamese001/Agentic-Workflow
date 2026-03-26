# API Documentation: context_curator_engine

**Target Audience**: developers, api_users

# context_curator_engine API Documentation

**File**: `context_curator_engine.py`
**Classes**: 1
**Functions**: 13

## Classes

- **ContextCurator** (inherits from SovereignBaseAgent)

## Functions

- **create_context_curator** -> ContextCurator
- **_run_self_tests** -> dict
- **__init__**
- **add_chunk** -> bool
- **remove_chunk** -> bool
- **pin_chunk** -> bool
- **unpin_chunk** -> bool
- **update_relevance** -> bool
- **prune_by_relevance** -> int
- **get_context_window** -> ContextWindow
- **get_formatted_context** -> str
- **_calculate_total_tokens** -> int
- **_make_space** -> bool


## Class: ContextCurator

**Description**: Curates and manages the context window dynamically.

    Features:
    - Pin core instructions and safety policies
    - Relevance-based chunk swapping
    - Token budget enforcement
    - Priority-based retention
    - Automatic pruning
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, max_tokens, reserved_tokens, enable_logging
**Description**: Initialize context curator.

        Args:
            max_tokens: Maximum context window size
            reserved_tokens: Tokens reserved for output
            enable_logging: Enable logging
        

#### add_chunk
**Parameters**: self, chunk, auto_pin
**Returns**: bool
**Description**: Add a context chunk.

        Args:
            chunk: Context chunk to add
            auto_pin: Automatically pin if critical

        Returns:
            True if added successfully
        

#### remove_chunk
**Parameters**: self, chunk_id
**Returns**: bool
**Description**: Remove a context chunk.

        Args:
            chunk_id: ID of chunk to remove

        Returns:
            True if removed successfully
        

#### pin_chunk
**Parameters**: self, chunk_id
**Returns**: bool
**Description**: Pin a chunk to prevent removal.

        Args:
            chunk_id: ID of chunk to pin

        Returns:
            True if pinned successfully
        

#### unpin_chunk
**Parameters**: self, chunk_id
**Returns**: bool
**Description**: Unpin a chunk.

        Args:
            chunk_id: ID of chunk to unpin

        Returns:
            True if unpinned successfully
        

#### update_relevance
**Parameters**: self, chunk_id, relevance_score
**Returns**: bool
**Description**: # SQL removed: Update relevance score for a chunk.

        Args:
            chunk_id: ID of chunk
            relevance_score: New relevance score (0.0-1.0)

        Returns:
            True if updated successfully
        

#### prune_by_relevance
**Parameters**: self, min_relevance, keep_count
**Returns**: int
**Description**: Prune low-relevance chunks.

        Args:
            min_relevance: Minimum relevance to keep
            keep_count: Minimum chunks to keep

        Returns:
            Number of chunks pruned
        

#### get_context_window
**Parameters**: self
**Returns**: ContextWindow
**Description**: Get current context window.

        Returns:
            ContextWindow with all chunks
        

#### get_formatted_context
**Parameters**: self
**Returns**: str
**Description**: Get formatted context string.

        Returns:
            Formatted context for LLM
        

#### _calculate_total_tokens
**Parameters**: self
**Returns**: int
**Description**: Calculate total tokens in context.

        Returns:
            Total token count
        

#### _make_space
**Parameters**: self, required_tokens
**Returns**: bool
**Description**: Make space by removing low-priority chunks.

        Args:
            required_tokens: Tokens needed

        Returns:
            True if space was made
        



## Function: create_context_curator

**Parameters**: max_tokens, reserved_tokens
**Returns**: ContextCurator
**Description**: Factory function to create context curator.

    Args:
        max_tokens: Maximum context window size
        reserved_tokens: Tokens reserved for output

    Returns:
        ContextCurator instance
    



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: __init__

**Parameters**: self, max_tokens, reserved_tokens, enable_logging
**Description**: Initialize context curator.

        Args:
            max_tokens: Maximum context window size
            reserved_tokens: Tokens reserved for output
            enable_logging: Enable logging
        



## Function: add_chunk

**Parameters**: self, chunk, auto_pin
**Returns**: bool
**Description**: Add a context chunk.

        Args:
            chunk: Context chunk to add
            auto_pin: Automatically pin if critical

        Returns:
            True if added successfully
        



## Function: remove_chunk

**Parameters**: self, chunk_id
**Returns**: bool
**Description**: Remove a context chunk.

        Args:
            chunk_id: ID of chunk to remove

        Returns:
            True if removed successfully
        



## Function: pin_chunk

**Parameters**: self, chunk_id
**Returns**: bool
**Description**: Pin a chunk to prevent removal.

        Args:
            chunk_id: ID of chunk to pin

        Returns:
            True if pinned successfully
        



## Function: unpin_chunk

**Parameters**: self, chunk_id
**Returns**: bool
**Description**: Unpin a chunk.

        Args:
            chunk_id: ID of chunk to unpin

        Returns:
            True if unpinned successfully
        



## Function: update_relevance

**Parameters**: self, chunk_id, relevance_score
**Returns**: bool
**Description**: # SQL removed: Update relevance score for a chunk.

        Args:
            chunk_id: ID of chunk
            relevance_score: New relevance score (0.0-1.0)

        Returns:
            True if updated successfully
        



## Function: prune_by_relevance

**Parameters**: self, min_relevance, keep_count
**Returns**: int
**Description**: Prune low-relevance chunks.

        Args:
            min_relevance: Minimum relevance to keep
            keep_count: Minimum chunks to keep

        Returns:
            Number of chunks pruned
        



## Function: get_context_window

**Parameters**: self
**Returns**: ContextWindow
**Description**: Get current context window.

        Returns:
            ContextWindow with all chunks
        



## Function: get_formatted_context

**Parameters**: self
**Returns**: str
**Description**: Get formatted context string.

        Returns:
            Formatted context for LLM
        



## Function: _calculate_total_tokens

**Parameters**: self
**Returns**: int
**Description**: Calculate total tokens in context.

        Returns:
            Total token count
        



## Function: _make_space

**Parameters**: self, required_tokens
**Returns**: bool
**Description**: Make space by removing low-priority chunks.

        Args:
            required_tokens: Tokens needed

        Returns:
            True if space was made
        



## Usage Examples

### Class Usage

```python
# Using ContextCurator
contextcurator = ContextCurator()
contextcurator.add_chunk()
contextcurator.remove_chunk()
```

### Function Usage

```python
# Using create_context_curator
result = create_context_curator(max_tokens, reserved_tokens)
```

```python
# Using _run_self_tests
result = _run_self_tests()
```

```python
# Using __init__
result = __init__(max_tokens, reserved_tokens)
```



---
**Generated**: 2026-03-26T09:39:04.146479
**Type**: api_reference
**Quality**: comprehensive
