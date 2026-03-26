# API Documentation: lazy_seam_scanner

**Target Audience**: developers, api_users

# lazy_seam_scanner API Documentation

**File**: `lazy_seam_scanner.py`
**Classes**: 2
**Functions**: 11

## Classes

- **LazyUpwardImport**
- **LazySeamScanner**

## Functions

- **layer_of_path** -> int | None
- **extract_import_targets** -> list[tuple[str, int]]
- **_is_inside_function_or_guarded** -> bool
- **_get_enclosing_function** -> ast.FunctionDef | ast.AsyncFunctionDef | None
- **_is_inside_try_module_scope** -> bool
- **collect_lazy_upward_imports** -> list[LazyUpwardImport]
- **lazy_upward_import_metric** -> dict
- **main**
- **__init__**
- **scan_codebase** -> list[dict[str, Any]]
- **export_allowlist** -> None


## Class: LazyUpwardImport

**Description**: A lazy upward import excluded by function/try guard.



## Class: LazySeamScanner

**Description**: Scanner for lazy loader seams using Phase 3B metric output.

### Methods

#### __init__
**Parameters**: self, root_path

#### scan_codebase
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Scan codebase using Phase 3B lazy upward import metric.

#### export_allowlist
**Parameters**: self, output_path
**Returns**: None
**Description**: Export allowlist to JSON file.



## Function: layer_of_path

**Parameters**: path, agentic_root
**Returns**: int | None
**Description**: Extract layer number from a path.



## Function: extract_import_targets

**Parameters**: node
**Returns**: list[tuple[str, int]]
**Description**: Extract import target strings and line numbers from an AST node.



## Function: _is_inside_function_or_guarded

**Parameters**: tree, target_lineno
**Returns**: bool
**Description**: Check if a line is inside a function, method, or try/except block.



## Function: _get_enclosing_function

**Parameters**: tree, target_lineno
**Returns**: ast.FunctionDef | ast.AsyncFunctionDef | None
**Description**: Return the innermost FunctionDef/AsyncFunctionDef enclosing target_lineno.



## Function: _is_inside_try_module_scope

**Parameters**: tree, target_lineno
**Returns**: bool
**Description**: Return True if target_lineno is inside a Try block at module scope.



## Function: collect_lazy_upward_imports

**Parameters**: agentic_root
**Returns**: list[LazyUpwardImport]
**Description**: Collect all upward imports excluded ONLY because they are inside a
    function/try guard (the 'lazy seam').



## Function: lazy_upward_import_metric

**Parameters**: agentic_root
**Returns**: dict
**Description**: Compute the LAZY_UPWARD_IMPORTS metric.



## Function: main

**Description**: Main entry point.



## Function: __init__

**Parameters**: self, root_path


## Function: scan_codebase

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Scan codebase using Phase 3B lazy upward import metric.



## Function: export_allowlist

**Parameters**: self, output_path
**Returns**: None
**Description**: Export allowlist to JSON file.



## Usage Examples

### Class Usage

```python
# Using LazyUpwardImport
lazyupwardimport = LazyUpwardImport()
```

```python
# Using LazySeamScanner
lazyseamscanner = LazySeamScanner()
lazyseamscanner.scan_codebase()
lazyseamscanner.export_allowlist()
```

### Function Usage

```python
# Using layer_of_path
result = layer_of_path(path, agentic_root)
```

```python
# Using extract_import_targets
result = extract_import_targets(node)
```

```python
# Using _is_inside_function_or_guarded
result = _is_inside_function_or_guarded(tree, target_lineno)
```



---
**Generated**: 2026-03-26T09:39:05.008574
**Type**: api_reference
**Quality**: comprehensive
