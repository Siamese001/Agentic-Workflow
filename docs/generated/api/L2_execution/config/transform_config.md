# API Documentation: transform_config

**Target Audience**: developers, api_users

# transform_config API Documentation

**File**: `transform_config.py`
**Classes**: 5
**Functions**: 23

## Classes

- **TransformOperation** (inherits from str, Enum)
- **CodeTransformArgs** (inherits from BaseModel)
- **TransformResult**
- **SymbolRenamer** (inherits from <ast.Attribute object at 0x000001CBFADD9C10>)
- **DecoratorModifier** (inherits from <ast.Attribute object at 0x000001CBFADFE010>)

## Functions

- **_parse_code** -> tuple[ast.AST | None, str | None]
- **_unparse_code** -> str
- **rename_symbol** -> TransformResult
- **extract_function** -> TransformResult
- **add_decorator** -> TransformResult
- **remove_decorator** -> TransformResult
- **code_transform** -> dict[str, Any]
- **quick_rename** -> str
- **quick_extract** -> str
- **to_dict** -> dict[str, Any]
- **__init__**
- **_push_scope**
- **_pop_scope**
- **_is_shadowed** -> bool
- **visit_Name** -> ast.Name
- **visit_FunctionDef** -> ast.FunctionDef
- **visit_AsyncFunctionDef** -> ast.AsyncFunctionDef
- **visit_ClassDef** -> ast.ClassDef
- **visit_arg** -> ast.arg
- **visit_alias** -> ast.alias
- **__init__**
- **visit_FunctionDef** -> ast.FunctionDef
- **visit_ClassDef** -> ast.ClassDef


## Class: TransformOperation

**Description**: Supported transformation operations.

**Inherits from**: str, Enum



## Class: CodeTransformArgs

**Description**: Arguments for code transformation operations.

**Inherits from**: BaseModel



## Class: TransformResult

**Description**: Result of a code transformation.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: SymbolRenamer

**Description**: AST transformer for renaming symbols with scope awareness.

**Inherits from**: ast.NodeTransformer

### Methods

#### __init__
**Parameters**: self, old_name, new_name

#### _push_scope
**Parameters**: self, names
**Description**: Push a new scope onto the stack.

#### _pop_scope
**Parameters**: self
**Description**: Pop the current scope.

#### _is_shadowed
**Parameters**: self
**Returns**: bool
**Description**: Check if the target name is shadowed in current scope.

#### visit_Name
**Parameters**: self, node
**Returns**: ast.Name
**Description**: Rename Name nodes.

#### visit_FunctionDef
**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Handle function definitions with scope tracking.

#### visit_AsyncFunctionDef
**Parameters**: self, node
**Returns**: ast.AsyncFunctionDef
**Description**: Handle async function definitions.

#### visit_ClassDef
**Parameters**: self, node
**Returns**: ast.ClassDef
**Description**: Handle class definitions.

#### visit_arg
**Parameters**: self, node
**Returns**: ast.arg
**Description**: Handle function arguments.

#### visit_alias
**Parameters**: self, node
**Returns**: ast.alias
**Description**: Handle import aliases.



## Class: DecoratorModifier

**Description**: AST transformer for adding/removing decorators.

**Inherits from**: ast.NodeTransformer

### Methods

#### __init__
**Parameters**: self, target_name, decorator_name, add

#### visit_FunctionDef
**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Modify decorators on function definitions.

#### visit_ClassDef
**Parameters**: self, node
**Returns**: ast.ClassDef
**Description**: Modify decorators on class definitions.



## Function: _parse_code

**Parameters**: code
**Returns**: tuple[ast.AST | None, str | None]
**Description**: Parse code into AST, returning tree and error if any.



## Function: _unparse_code

**Parameters**: tree
**Returns**: str
**Description**: Convert AST back to code.



## Function: rename_symbol

**Parameters**: code, old_name, new_name
**Returns**: TransformResult
**Description**: 
    Rename a symbol throughout the code with scope awareness.

    Args:
        code: Source code
        old_name: Current symbol name
        new_name: New symbol name

    Returns:
        TransformResult with renamed code
    



## Function: extract_function

**Parameters**: code, line_start, line_end, function_name
**Returns**: TransformResult
**Description**: 
    Extract lines into a new function.

    Args:
        code: Source code
        line_start: Start line (1-indexed)
        line_end: End line (1-indexed)
        function_name: Name for the extracted function

    Returns:
        TransformResult with extracted function
    



## Function: add_decorator

**Parameters**: code, target_name, decorator_name
**Returns**: TransformResult
**Description**: 
    Add a decorator to a function or class.

    Args:
        code: Source code
        target_name: Name of function/class to decorate
        decorator_name: Name of decorator to add

    Returns:
        TransformResult with decorated code
    



## Function: remove_decorator

**Parameters**: code, target_name, decorator_name
**Returns**: TransformResult
**Description**: 
    Remove a decorator from a function or class.

    Args:
        code: Source code
        target_name: Name of function/class
        decorator_name: Name of decorator to remove

    Returns:
        TransformResult with decorator removed
    



## Function: code_transform

**Parameters**: args
**Returns**: dict[str, Any]
**Description**: 
    Main entry point for code transformations.

    Dispatches to specific transformation functions based on operation type.

    Args:
        args: CodeTransformArgs with operation details

    Returns:
        Dict with transformation results
    



## Function: quick_rename

**Parameters**: code, old_name, new_name
**Returns**: str
**Description**: Quick rename without full args model. Returns transformed code or original on failure.



## Function: quick_extract

**Parameters**: code, start, end, func_name
**Returns**: str
**Description**: Quick extract without full args model. Returns transformed code or original on failure.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: __init__

**Parameters**: self, old_name, new_name


## Function: _push_scope

**Parameters**: self, names
**Description**: Push a new scope onto the stack.



## Function: _pop_scope

**Parameters**: self
**Description**: Pop the current scope.



## Function: _is_shadowed

**Parameters**: self
**Returns**: bool
**Description**: Check if the target name is shadowed in current scope.



## Function: visit_Name

**Parameters**: self, node
**Returns**: ast.Name
**Description**: Rename Name nodes.



## Function: visit_FunctionDef

**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Handle function definitions with scope tracking.



## Function: visit_AsyncFunctionDef

**Parameters**: self, node
**Returns**: ast.AsyncFunctionDef
**Description**: Handle async function definitions.



## Function: visit_ClassDef

**Parameters**: self, node
**Returns**: ast.ClassDef
**Description**: Handle class definitions.



## Function: visit_arg

**Parameters**: self, node
**Returns**: ast.arg
**Description**: Handle function arguments.



## Function: visit_alias

**Parameters**: self, node
**Returns**: ast.alias
**Description**: Handle import aliases.



## Function: __init__

**Parameters**: self, target_name, decorator_name, add


## Function: visit_FunctionDef

**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Modify decorators on function definitions.



## Function: visit_ClassDef

**Parameters**: self, node
**Returns**: ast.ClassDef
**Description**: Modify decorators on class definitions.



## Usage Examples

### Class Usage

```python
# Using TransformOperation
transformoperation = TransformOperation()
```

```python
# Using CodeTransformArgs
codetransformargs = CodeTransformArgs()
```

```python
# Using TransformResult
transformresult = TransformResult()
transformresult.to_dict()
```

### Function Usage

```python
# Using _parse_code
result = _parse_code(code)
```

```python
# Using _unparse_code
result = _unparse_code(tree)
```

```python
# Using rename_symbol
result = rename_symbol(code, old_name)
```



---
**Generated**: 2026-03-26T09:39:03.638688
**Type**: api_reference
**Quality**: comprehensive
