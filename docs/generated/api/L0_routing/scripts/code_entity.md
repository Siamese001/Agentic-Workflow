# API Documentation: code_entity

**Target Audience**: developers, api_users

# code_entity API Documentation

**File**: `code_entity.py`
**Classes**: 2
**Functions**: 7

## Classes

- **CodeEntity**
- **FileAnalysis**

## Functions

- **extract_docstring** -> str
- **classify_entity_type** -> str
- **infer_domain** -> str
- **analyze_file** -> FileAnalysis | None
- **build_current_codebase_index** -> dict[str, set[str]]
- **calculate_uniqueness** -> tuple[float, list[str]]
- **main**


## Class: CodeEntity

**Description**: Represents a class or function extracted from code.



## Class: FileAnalysis

**Description**: Complete analysis of a single file.



## Function: extract_docstring

**Parameters**: node
**Returns**: str
**Description**: Extract docstring from AST node.



## Function: classify_entity_type

**Parameters**: name, bases
**Returns**: str
**Description**: Classify entity type based on name and inheritance.



## Function: infer_domain

**Parameters**: content, entities
**Returns**: str
**Description**: Infer domain from content and entity names.



## Function: analyze_file

**Parameters**: file_path, archive_folder
**Returns**: FileAnalysis | None
**Description**: Perform deep AST analysis on a file.



## Function: build_current_codebase_index

**Parameters**: dirs
**Returns**: dict[str, set[str]]
**Description**: Build index of all entities in current codebase.



## Function: calculate_uniqueness

**Parameters**: analysis, codebase_index
**Returns**: tuple[float, list[str]]
**Description**: Calculate how unique the file's entities are compared to codebase.



## Function: main



## Usage Examples

### Class Usage

```python
# Using CodeEntity
codeentity = CodeEntity()
```

```python
# Using FileAnalysis
fileanalysis = FileAnalysis()
```

### Function Usage

```python
# Using extract_docstring
result = extract_docstring(node)
```

```python
# Using classify_entity_type
result = classify_entity_type(name, bases)
```

```python
# Using infer_domain
result = infer_domain(content, entities)
```



---
**Generated**: 2026-03-26T09:39:02.807678
**Type**: api_reference
**Quality**: comprehensive
