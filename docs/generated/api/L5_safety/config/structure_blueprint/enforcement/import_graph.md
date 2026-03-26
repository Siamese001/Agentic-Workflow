# API Documentation: import_graph

**Target Audience**: developers, api_users

# import_graph API Documentation

**File**: `import_graph.py`
**Classes**: 2
**Functions**: 11

## Classes

- **ImportEdge**
- **ImportGraph**

## Functions

- **__init__** -> None
- **__repr__** -> str
- **__init__** -> None
- **edges_from** -> list[ImportEdge]
- **files_importing_module** -> set[str]
- **files_importing_territory** -> set[str]
- **resolve_module_path** -> Path | None
- **all_files** -> set[str]
- **_build** -> None
- **_parse_file** -> None
- **_extract_dynamic_import** -> str | None


## Class: ImportEdge

**Description**: A single import relationship extracted from AST.

### Methods

#### __init__
**Parameters**: self, source_file, target_module, imported_names, lineno
**Returns**: None

#### __repr__
**Parameters**: self
**Returns**: str



## Class: ImportGraph

**Description**: Cached adjacency map of all internal imports across SCAN_ROOTS.

    Built once, queried by multiple enforcement modules.
    

### Methods

#### __init__
**Parameters**: self, root, scan_roots
**Returns**: None

#### edges_from
**Parameters**: self, file
**Returns**: list[ImportEdge]
**Description**: All import edges originating from a file (repo-relative path).

#### files_importing_module
**Parameters**: self, module_prefix
**Returns**: set[str]
**Description**: All files that import from a module matching the prefix.

#### files_importing_territory
**Parameters**: self, territory
**Returns**: set[str]
**Description**: All files outside a territory that import FROM that territory.

#### resolve_module_path
**Parameters**: self, module
**Returns**: Path | None
**Description**: Resolve a dotted module path to a filesystem Path, or None.

#### all_files
**Parameters**: self
**Returns**: set[str]
**Description**: All repo-relative file paths that were parsed.

#### _build
**Parameters**: self
**Returns**: None
**Description**: Walk SCAN_ROOTS, AST-parse each .py file, extract internal imports.

#### _parse_file
**Parameters**: self, fpath, rel
**Returns**: None
**Description**: Parse a single file and extract internal import edges.

#### _extract_dynamic_import
**Parameters**: node
**Returns**: str | None
**Description**: Extract module string from __import__("x") or importlib.import_module("x").



## Function: __init__

**Parameters**: self, source_file, target_module, imported_names, lineno
**Returns**: None


## Function: __repr__

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self, root, scan_roots
**Returns**: None


## Function: edges_from

**Parameters**: self, file
**Returns**: list[ImportEdge]
**Description**: All import edges originating from a file (repo-relative path).



## Function: files_importing_module

**Parameters**: self, module_prefix
**Returns**: set[str]
**Description**: All files that import from a module matching the prefix.



## Function: files_importing_territory

**Parameters**: self, territory
**Returns**: set[str]
**Description**: All files outside a territory that import FROM that territory.



## Function: resolve_module_path

**Parameters**: self, module
**Returns**: Path | None
**Description**: Resolve a dotted module path to a filesystem Path, or None.



## Function: all_files

**Parameters**: self
**Returns**: set[str]
**Description**: All repo-relative file paths that were parsed.



## Function: _build

**Parameters**: self
**Returns**: None
**Description**: Walk SCAN_ROOTS, AST-parse each .py file, extract internal imports.



## Function: _parse_file

**Parameters**: self, fpath, rel
**Returns**: None
**Description**: Parse a single file and extract internal import edges.



## Function: _extract_dynamic_import

**Parameters**: node
**Returns**: str | None
**Description**: Extract module string from __import__("x") or importlib.import_module("x").



## Usage Examples

### Class Usage

```python
# Using ImportEdge
importedge = ImportEdge()
```

```python
# Using ImportGraph
importgraph = ImportGraph()
importgraph.edges_from()
importgraph.files_importing_module()
```

### Function Usage

```python
# Using __init__
result = __init__(source_file, target_module)
```

```python
# Using __repr__
result = __repr__()
```

```python
# Using __init__
result = __init__(root, scan_roots)
```



---
**Generated**: 2026-03-26T09:39:05.984414
**Type**: api_reference
**Quality**: comprehensive
