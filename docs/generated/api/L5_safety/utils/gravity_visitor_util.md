# API Documentation: gravity_visitor_util

**Target Audience**: developers, api_users

# gravity_visitor_util API Documentation

**File**: `gravity_visitor_util.py`
**Classes**: 1
**Functions**: 7

## Classes

- **GravityVisitor** (inherits from <ast.Attribute object at 0x000001CBFAE04F10>)

## Functions

- **get_file_imports** -> list[tuple[str, int]]
- **extract_layer_from_path** -> str | None
- **extract_layer_from_import** -> str | None
- **check_gravity_violation** -> bool
- **__init__** -> None
- **visit_Import** -> None
- **visit_ImportFrom** -> None


## Class: GravityVisitor

**Description**: 
    Standardized AST visitor for architectural gravity enforcement.

    Extracts all import statements from a Python file for layer analysis.
    

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, source_layer, file_path
**Returns**: None

#### visit_Import
**Parameters**: self, node
**Returns**: None
**Description**: Handle 'import x' statements.

#### visit_ImportFrom
**Parameters**: self, node
**Returns**: None
**Description**: Handle 'from x import y' statements.



## Function: get_file_imports

**Parameters**: file_path
**Returns**: list[tuple[str, int]]
**Description**: 
    Centralized utility to extract imports from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of (module_name, line_number) tuples
    



## Function: extract_layer_from_path

**Parameters**: file_path
**Returns**: str | None
**Description**: 
    Extract the layer (L0-L6, Apps) from a file path.

    Args:
        file_path: Path to analyze

    Returns:
        Layer string (e.g., "L3") or None if not determinable
    



## Function: extract_layer_from_import

**Parameters**: import_path
**Returns**: str | None
**Description**: 
    Extract the layer from an import path.

    Args:
        import_path: Import module path (e.g., "agentic_core.L5_safety.validators")

    Returns:
        Layer string (e.g., "L5") or None if not determinable
    



## Function: check_gravity_violation

**Parameters**: source_layer, target_layer, gravity_rules
**Returns**: bool
**Description**: 
    Check if importing from target_layer violates gravity rules.

    Args:
        source_layer: Layer of the file doing the import
        target_layer: Layer being imported from
        gravity_rules: Optional custom gravity rules dict

    Returns:
        True if this is a violation, False if allowed
    



## Function: __init__

**Parameters**: self, source_layer, file_path
**Returns**: None


## Function: visit_Import

**Parameters**: self, node
**Returns**: None
**Description**: Handle 'import x' statements.



## Function: visit_ImportFrom

**Parameters**: self, node
**Returns**: None
**Description**: Handle 'from x import y' statements.



## Usage Examples

### Class Usage

```python
# Using GravityVisitor
gravityvisitor = GravityVisitor()
gravityvisitor.visit_Import()
gravityvisitor.visit_ImportFrom()
```

### Function Usage

```python
# Using get_file_imports
result = get_file_imports(file_path)
```

```python
# Using extract_layer_from_path
result = extract_layer_from_path(file_path)
```

```python
# Using extract_layer_from_import
result = extract_layer_from_import(import_path)
```



---
**Generated**: 2026-03-26T09:39:05.654645
**Type**: api_reference
**Quality**: comprehensive
