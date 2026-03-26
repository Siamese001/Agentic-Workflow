# API Documentation: TypeHintFixerAgent

**Target Audience**: developers, api_users

# TypeHintFixerAgent API Documentation

**File**: `TypeHintFixerAgent.py`
**Classes**: 1
**Functions**: 6

## Classes

- **TypeHintFixerAgent** (inherits from SovereignBaseAgent, <ast.Attribute object at 0x000001CBFAEA4050>)

## Functions

- **__init__** -> None
- **visit_FunctionDef** -> ast.FunctionDef
- **visit_AsyncFunctionDef** -> ast.AsyncFunctionDef
- **visit_Assign** -> ast.Assign | ast.AnnAssign
- **heal_repository** -> dict
- **heal**


## Class: TypeHintFixerAgent

**Description**: 
    AST transformer that adds Missing type hints to public symbols.
    

**Inherits from**: SovereignBaseAgent, ast.NodeTransformer

### Methods

#### __init__
**Parameters**: self, fallback_param, fallback_return, fallback_var
**Returns**: None
**Description**: Initialize the instance.

#### visit_FunctionDef
**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Execute visit_FunctionDef operation.

#### visit_AsyncFunctionDef
**Parameters**: self, node
**Returns**: ast.AsyncFunctionDef
**Description**: Execute visit_AsyncFunctionDef operation.

#### visit_Assign
**Parameters**: self, node
**Returns**: ast.Assign | ast.AnnAssign
**Description**: Execute visit_Assign operation.

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().

#### heal
**Parameters**: self, violation



## Function: __init__

**Parameters**: self, fallback_param, fallback_return, fallback_var
**Returns**: None
**Description**: Initialize the instance.



## Function: visit_FunctionDef

**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Execute visit_FunctionDef operation.



## Function: visit_AsyncFunctionDef

**Parameters**: self, node
**Returns**: ast.AsyncFunctionDef
**Description**: Execute visit_AsyncFunctionDef operation.



## Function: visit_Assign

**Parameters**: self, node
**Returns**: ast.Assign | ast.AnnAssign
**Description**: Execute visit_Assign operation.



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using TypeHintFixerAgent
typehintfixeragent = TypeHintFixerAgent()
typehintfixeragent.visit_FunctionDef()
typehintfixeragent.visit_AsyncFunctionDef()
```

### Function Usage

```python
# Using __init__
result = __init__(fallback_param, fallback_return)
```

```python
# Using visit_FunctionDef
result = visit_FunctionDef(node)
```

```python
# Using visit_AsyncFunctionDef
result = visit_AsyncFunctionDef(node)
```



---
**Generated**: 2026-03-26T09:39:05.444271
**Type**: api_reference
**Quality**: comprehensive
