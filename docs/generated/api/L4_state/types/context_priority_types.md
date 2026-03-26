# API Documentation: context_priority_types

**Target Audience**: developers, api_users

# context_priority_types API Documentation

**File**: `context_priority_types.py`
**Classes**: 4
**Functions**: 2

## Classes

- **ContextPriority** (inherits from Enum)
- **ContextType** (inherits from Enum)
- **ContextChunk**
- **ContextWindow**

## Functions

- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]


## Class: ContextPriority

**Description**: Priority levels for context chunks.

**Inherits from**: Enum



## Class: ContextType

**Description**: Types of context chunks.

**Inherits from**: Enum



## Class: ContextChunk

**Description**: Individual context chunk.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: ContextWindow

**Description**: Managed context window.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Usage Examples

### Class Usage

```python
# Using ContextPriority
contextpriority = ContextPriority()
```

```python
# Using ContextType
contexttype = ContextType()
```

```python
# Using ContextChunk
contextchunk = ContextChunk()
contextchunk.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.628693
**Type**: api_reference
**Quality**: comprehensive
