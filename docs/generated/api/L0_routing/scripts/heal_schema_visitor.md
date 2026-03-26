# API Documentation: heal_schema_visitor

**Target Audience**: developers, api_users

# heal_schema_visitor API Documentation

**File**: `heal_schema_visitor.py`
**Classes**: 1
**Functions**: 6

## Classes

- **HealSchemaVisitor** (inherits from <ast.Attribute object at 0x000001CBFAEBF150>)

## Functions

- **check_file** -> list[dict]
- **main**
- **__init__**
- **visit_FunctionDef**
- **visit_Return**
- **_check_dict_keys**


## Class: HealSchemaVisitor

**Description**: AST visitor to find @standard_heal decorated methods and check return keys.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, filepath

#### visit_FunctionDef
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_FunctionDef.

#### visit_Return
**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Return.

#### _check_dict_keys
**Parameters**: self, dict_node, lineno
**Description**: Check dict keys for non-canonical names.



## Function: check_file

**Parameters**: filepath
**Returns**: list[dict]
**Description**: Check a single file for schema compliance.



## Function: main

**Description**: TODO: Add documentation for main.



## Function: __init__

**Parameters**: self, filepath


## Function: visit_FunctionDef

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_FunctionDef.



## Function: visit_Return

**Parameters**: self, node
**Description**: TODO: Add documentation for visit_Return.



## Function: _check_dict_keys

**Parameters**: self, dict_node, lineno
**Description**: Check dict keys for non-canonical names.



## Usage Examples

### Class Usage

```python
# Using HealSchemaVisitor
healschemavisitor = HealSchemaVisitor()
healschemavisitor.visit_FunctionDef()
healschemavisitor.visit_Return()
```

### Function Usage

```python
# Using check_file
result = check_file(filepath)
```

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(filepath)
```



---
**Generated**: 2026-03-26T09:39:03.166411
**Type**: api_reference
**Quality**: comprehensive
