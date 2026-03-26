# API Documentation: lazy_seam_enforcer

**Target Audience**: developers, api_users

# lazy_seam_enforcer API Documentation

**File**: `lazy_seam_enforcer.py`
**Classes**: 2
**Functions**: 15

## Classes

- **LazyUpwardImport**
- **LazySeamEnforcer**

## Functions

- **extract_import_targets** -> list[tuple[str, int]]
- **_is_inside_function_or_guarded** -> bool
- **_get_enclosing_function** -> ast.FunctionDef | ast.AsyncFunctionDef | None
- **_is_inside_try_module_scope** -> bool
- **collect_lazy_upward_imports** -> list[LazyUpwardImport]
- **lazy_upward_import_metric** -> dict
- **main**
- **__init__**
- **_load_allowlist** -> dict[str, Any]
- **_create_seam_key** -> str
- **_get_allowlist_keys** -> set[str]
- **scan_file** -> list[dict[str, Any]]
- **scan_codebase** -> list[dict[str, Any]]
- **enforce** -> list[dict[str, Any]]
- **print_results** -> None


## Class: LazyUpwardImport

**Description**: A lazy upward import excluded by function/try guard.



## Class: LazySeamEnforcer

**Description**: Enforces lazy seam allowlist compliance.

### Methods

#### __init__
**Parameters**: self, root_path, allowlist_path

#### _load_allowlist
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load allowlist from file.

#### _create_seam_key
**Parameters**: self, file_path, function_name, imported_modules, imported_symbols
**Returns**: str
**Description**: Create a unique key for a seam.

#### _get_allowlist_keys
**Parameters**: self
**Returns**: set[str]
**Description**: Get all allowed seam keys.

#### scan_file
**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: Scan a single file for lazy seams.

#### scan_codebase
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Scan entire codebase for lazy seams.

#### enforce
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Enforce allowlist compliance using Phase 3B metric.

#### print_results
**Parameters**: self
**Returns**: None
**Description**: Print enforcement results.



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

**Description**: Main execution.



## Function: __init__

**Parameters**: self, root_path, allowlist_path


## Function: _load_allowlist

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load allowlist from file.



## Function: _create_seam_key

**Parameters**: self, file_path, function_name, imported_modules, imported_symbols
**Returns**: str
**Description**: Create a unique key for a seam.



## Function: _get_allowlist_keys

**Parameters**: self
**Returns**: set[str]
**Description**: Get all allowed seam keys.



## Function: scan_file

**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: Scan a single file for lazy seams.



## Function: scan_codebase

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Scan entire codebase for lazy seams.



## Function: enforce

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Enforce allowlist compliance using Phase 3B metric.



## Function: print_results

**Parameters**: self
**Returns**: None
**Description**: Print enforcement results.



## Usage Examples

### Class Usage

```python
# Using LazyUpwardImport
lazyupwardimport = LazyUpwardImport()
```

```python
# Using LazySeamEnforcer
lazyseamenforcer = LazySeamEnforcer()
lazyseamenforcer.scan_file()
lazyseamenforcer.scan_codebase()
```

### Function Usage

```python
# Using extract_import_targets
result = extract_import_targets(node)
```

```python
# Using _is_inside_function_or_guarded
result = _is_inside_function_or_guarded(tree, target_lineno)
```

```python
# Using _get_enclosing_function
result = _get_enclosing_function(tree, target_lineno)
```



---
**Generated**: 2026-03-26T09:39:05.004960
**Type**: api_reference
**Quality**: comprehensive
