# API Documentation: memory_item_types

**Target Audience**: developers, api_users

# memory_item_types API Documentation

**File**: `memory_item_types.py`
**Classes**: 2
**Functions**: 1

## Classes

- **MemoryItem** (inherits from BaseEntity)
- **MemoryQuery** (inherits from BaseModel)

## Functions

- **check_vector_integrity** -> list[float]


## Class: MemoryItem

**Description**: 
    Represents a single unit of semantic memory (e.g., a conversation turn, a fact).
    

**Inherits from**: BaseEntity

### Methods

#### check_vector_integrity
**Parameters**: cls, v
**Returns**: list[float]



## Class: MemoryQuery

**Description**: 
    Request object for semantic search.
    

**Inherits from**: BaseModel



## Function: check_vector_integrity

**Parameters**: cls, v
**Returns**: list[float]


## Usage Examples

### Class Usage

```python
# Using MemoryItem
memoryitem = MemoryItem()
memoryitem.check_vector_integrity()
```

```python
# Using MemoryQuery
memoryquery = MemoryQuery()
```

### Function Usage

```python
# Using check_vector_integrity
result = check_vector_integrity(cls, v)
```



---
**Generated**: 2026-03-26T09:39:04.638065
**Type**: api_reference
**Quality**: comprehensive
