# API Documentation: structural_namespace_fence_enforcer

**Target Audience**: developers, api_users

# structural_namespace_fence_enforcer API Documentation

**File**: `structural_namespace_fence_enforcer.py`
**Classes**: 3
**Functions**: 15

## Classes

- **ProvenanceTracker**
- **ProvenanceLoader** (inherits from <ast.Attribute object at 0x000001CBFAE437D0>)
- **StructuralNamespaceFinder** (inherits from <ast.Attribute object at 0x000001CBFADAFB90>)

## Functions

- **_extract_namespace** -> str
- **_namespace_from_module_name** -> str
- **install_structural_namespace_fence** -> StructuralNamespaceFinder
- **uninstall_structural_namespace_fence** -> None
- **get_provenance_tracker** -> ProvenanceTracker
- **__init__** -> None
- **register** -> None
- **namespace_of** -> str
- **is_forbidden_cross_import** -> bool
- **__init__** -> None
- **create_module**
- **exec_module**
- **__init__** -> None
- **find_spec**
- **_get_caller_from_loaded_modules** -> str | None


## Class: ProvenanceTracker

**Description**: Tracks module-to-namespace mapping at module load time.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register
**Parameters**: self, module_name, origin
**Returns**: None
**Description**: Register module provenance from its file path origin.

#### namespace_of
**Parameters**: self, module_name
**Returns**: str
**Description**: Return namespace for a registered module ('external' if unknown).

#### is_forbidden_cross_import
**Parameters**: self, caller_ns, target_module
**Returns**: bool
**Description**: Return True iff importing target_module from caller_ns is forbidden.



## Class: ProvenanceLoader

**Description**: Wraps an existing loader to register module provenance on creation.

**Inherits from**: importlib.abc.Loader

### Methods

#### __init__
**Parameters**: self, original_loader, tracker, module_name, origin
**Returns**: None

#### create_module
**Parameters**: self, spec

#### exec_module
**Parameters**: self, module



## Class: StructuralNamespaceFinder

**Description**: MetaPathFinder that enforces cross-namespace import rules.

    Returns None for all modules to let the normal import machinery resolve
    them — it only raises ImportError when a forbidden cross-namespace import
    is detected.  Namespace determination uses load-time provenance, not
    frame stack inspection.
    

**Inherits from**: importlib.abc.MetaPathFinder

### Methods

#### __init__
**Parameters**: self, tracker
**Returns**: None

#### find_spec
**Parameters**: self, fullname, path, target

#### _get_caller_from_loaded_modules
**Parameters**: self
**Returns**: str | None
**Description**: Determine calling module by scanning loaded sys.modules for tracked roots.



## Function: _extract_namespace

**Parameters**: path
**Returns**: str
**Description**: Derive namespace string from file path.



## Function: _namespace_from_module_name

**Parameters**: module_name
**Returns**: str
**Description**: Derive namespace from a dotted module name.



## Function: install_structural_namespace_fence

**Returns**: StructuralNamespaceFinder
**Description**: Install the namespace fence into sys.meta_path (idempotent).



## Function: uninstall_structural_namespace_fence

**Returns**: None
**Description**: Remove the namespace fence from sys.meta_path.



## Function: get_provenance_tracker

**Returns**: ProvenanceTracker
**Description**: Return the global ProvenanceTracker.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register

**Parameters**: self, module_name, origin
**Returns**: None
**Description**: Register module provenance from its file path origin.



## Function: namespace_of

**Parameters**: self, module_name
**Returns**: str
**Description**: Return namespace for a registered module ('external' if unknown).



## Function: is_forbidden_cross_import

**Parameters**: self, caller_ns, target_module
**Returns**: bool
**Description**: Return True iff importing target_module from caller_ns is forbidden.



## Function: __init__

**Parameters**: self, original_loader, tracker, module_name, origin
**Returns**: None


## Function: create_module

**Parameters**: self, spec


## Function: exec_module

**Parameters**: self, module


## Function: __init__

**Parameters**: self, tracker
**Returns**: None


## Function: find_spec

**Parameters**: self, fullname, path, target


## Function: _get_caller_from_loaded_modules

**Parameters**: self
**Returns**: str | None
**Description**: Determine calling module by scanning loaded sys.modules for tracked roots.



## Usage Examples

### Class Usage

```python
# Using ProvenanceTracker
provenancetracker = ProvenanceTracker()
provenancetracker.register()
provenancetracker.namespace_of()
```

```python
# Using ProvenanceLoader
provenanceloader = ProvenanceLoader()
provenanceloader.create_module()
provenanceloader.exec_module()
```

```python
# Using StructuralNamespaceFinder
structuralnamespacefinder = StructuralNamespaceFinder()
structuralnamespacefinder.find_spec()
```

### Function Usage

```python
# Using _extract_namespace
result = _extract_namespace(path)
```

```python
# Using _namespace_from_module_name
result = _namespace_from_module_name(module_name)
```

```python
# Using install_structural_namespace_fence
result = install_structural_namespace_fence()
```



---
**Generated**: 2026-03-26T09:39:04.957781
**Type**: api_reference
**Quality**: comprehensive
