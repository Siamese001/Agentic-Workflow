# API Documentation: hardened_anti_pattern_visitor

**Target Audience**: developers, api_users

# hardened_anti_pattern_visitor API Documentation

**File**: `hardened_anti_pattern_visitor.py`
**Classes**: 1
**Functions**: 13

## Classes

- **HardenedAntiPatternVisitor** (inherits from <ast.Attribute object at 0x000001CBFAE4DF50>)

## Functions

- **main**
- **unparse**
- **__init__**
- **add_finding**
- **_is_docstring** -> bool
- **visit_Import**
- **visit_ImportFrom**
- **visit_ClassDef**
- **visit_FunctionDef**
- **visit_Assign**
- **_check_string_bleed**
- **visit_Constant**
- **visit_Str**


## Class: HardenedAntiPatternVisitor

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, filepath

#### add_finding
**Parameters**: self, pattern_type, evidence, recommendation
**Description**: TODO: Add documentation for add_finding.

#### _is_docstring
**Parameters**: self, node
**Returns**: bool

#### visit_Import
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Import.

#### visit_ImportFrom
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_ImportFrom.

#### visit_ClassDef
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_ClassDef.

#### visit_FunctionDef
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_FunctionDef.

#### visit_Assign
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Assign.

#### _check_string_bleed
**Parameters**: self, s

#### visit_Constant
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Constant.

#### visit_Str
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Str.



## Function: main

**Description**: TODO: Add documentation for main.



## Function: unparse

**Parameters**: node
**Description**: TODO: Add documentation for unparse.



## Function: __init__

**Parameters**: self, filepath


## Function: add_finding

**Parameters**: self, pattern_type, evidence, recommendation
**Description**: TODO: Add documentation for add_finding.



## Function: _is_docstring

**Parameters**: self, node
**Returns**: bool


## Function: visit_Import

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Import.



## Function: visit_ImportFrom

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_ImportFrom.



## Function: visit_ClassDef

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_ClassDef.



## Function: visit_FunctionDef

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_FunctionDef.



## Function: visit_Assign

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Assign.



## Function: _check_string_bleed

**Parameters**: self, s


## Function: visit_Constant

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Constant.



## Function: visit_Str

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Str.



## Usage Examples

### Class Usage

```python
# Using HardenedAntiPatternVisitor
hardenedantipatternvisitor = HardenedAntiPatternVisitor()
hardenedantipatternvisitor.add_finding()
hardenedantipatternvisitor.visit_Import()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using unparse
result = unparse(node)
```

```python
# Using __init__
result = __init__(filepath)
```



---
**Generated**: 2026-03-26T09:39:03.161761
**Type**: api_reference
**Quality**: comprehensive
