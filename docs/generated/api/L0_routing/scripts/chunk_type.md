# API Documentation: chunk_type

**Target Audience**: developers, api_users

# chunk_type API Documentation

**File**: `chunk_type.py`
**Classes**: 2
**Functions**: 5

## Classes

- **ChunkType** (inherits from Enum)
- **SemanticChunk**

## Functions

- **_extract_docstring** -> str | None
- **_get_source_segment** -> str
- **chunk_python_ast** -> list[SemanticChunk]
- **chunk_text_fallback** -> list[SemanticChunk]
- **chunk_text** -> list[dict]


## Class: ChunkType

**Description**: Semantic chunk types for metadata.

**Inherits from**: Enum



## Class: SemanticChunk

**Description**: Structured semantic chunk with metadata.



## Function: _extract_docstring

**Parameters**: node
**Returns**: str | None
**Description**: Extract docstring from AST node if present.



## Function: _get_source_segment

**Parameters**: lines, start, end
**Returns**: str
**Description**: Extract line segment from source lines (1-indexed).



## Function: chunk_python_ast

**Parameters**: text, file_path
**Returns**: list[SemanticChunk]
**Description**: Parse Python file to semantic chunks using ast.



## Function: chunk_text_fallback

**Parameters**: text, file_path
**Returns**: list[SemanticChunk]
**Description**: Fallback to line-based chunking for non-Python or parse failures.



## Function: chunk_text

**Parameters**: text, file_path
**Returns**: list[dict]
**Description**: 
    Smart semantic chunking: AST for Python, fallback for others.
    Returns dicts ready for vector store with enriched metadata.
    



## Usage Examples

### Class Usage

```python
# Using ChunkType
chunktype = ChunkType()
```

```python
# Using SemanticChunk
semanticchunk = SemanticChunk()
```

### Function Usage

```python
# Using _extract_docstring
result = _extract_docstring(node)
```

```python
# Using _get_source_segment
result = _get_source_segment(lines, start)
```

```python
# Using chunk_python_ast
result = chunk_python_ast(text, file_path)
```



---
**Generated**: 2026-03-26T09:39:02.793136
**Type**: api_reference
**Quality**: comprehensive
