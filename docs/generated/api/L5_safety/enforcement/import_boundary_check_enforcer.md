# API Documentation: import_boundary_check_enforcer

**Target Audience**: developers, api_users

# import_boundary_check_enforcer API Documentation

**File**: `import_boundary_check_enforcer.py`
**Classes**: 1
**Functions**: 6

## Classes

- **_ImportBoundaryVisitor** (inherits from <ast.Attribute object at 0x000001CBFCC2B310>)

## Functions

- **check_file_import_boundaries** -> list[str]
- **check_agentic_core_boundaries** -> bool
- **__init__** -> None
- **_check** -> None
- **visit_Import** -> None
- **visit_ImportFrom** -> None


## Class: _ImportBoundaryVisitor

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### _check
**Parameters**: self, module, lineno
**Returns**: None

#### visit_Import
**Parameters**: self, node
**Returns**: None

#### visit_ImportFrom
**Parameters**: self, node
**Returns**: None



## Function: check_file_import_boundaries

**Parameters**: file_path
**Returns**: list[str]
**Description**: Return list of violation strings for a single file (empty = clean).



## Function: check_agentic_core_boundaries

**Returns**: bool
**Description**: Check all agentic_core files for import boundary compliance.

    Prints violations and returns False if any found, True if clean.
    



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: _check

**Parameters**: self, module, lineno
**Returns**: None


## Function: visit_Import

**Parameters**: self, node
**Returns**: None


## Function: visit_ImportFrom

**Parameters**: self, node
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using _ImportBoundaryVisitor
_importboundaryvisitor = _ImportBoundaryVisitor()
_importboundaryvisitor.visit_Import()
_importboundaryvisitor.visit_ImportFrom()
```

### Function Usage

```python
# Using check_file_import_boundaries
result = check_file_import_boundaries(file_path)
```

```python
# Using check_agentic_core_boundaries
result = check_agentic_core_boundaries()
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:04.852699
**Type**: api_reference
**Quality**: comprehensive
