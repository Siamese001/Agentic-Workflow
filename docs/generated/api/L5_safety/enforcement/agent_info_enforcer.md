# API Documentation: agent_info_enforcer

**Target Audience**: developers, api_users

# agent_info_enforcer API Documentation

**File**: `agent_info_enforcer.py`
**Classes**: 2
**Functions**: 15

## Classes

- **AgentInfo**
- **ASTNormalizer** (inherits from <ast.Attribute object at 0x000001CBFAE89AD0>)

## Functions

- **extract_layer** -> str
- **find_agent_classes** -> list[AgentInfo]
- **generate_fingerprint** -> tuple[str, str]
- **calculate_similarity** -> float
- **analyze_redundancy** -> dict
- **print_report**
- **__init__**
- **reset**
- **visit_ClassDef** -> ast.ClassDef
- **visit_FunctionDef** -> ast.FunctionDef
- **visit_AsyncFunctionDef** -> ast.AsyncFunctionDef
- **visit_Name** -> ast.Name
- **visit_Constant** -> ast.Constant
- **visit_Import** -> ast.Import | None
- **visit_ImportFrom** -> ast.ImportFrom | None


## Class: AgentInfo

**Description**: Information about a discovered agent class.



## Class: ASTNormalizer

**Description**: 
    Enhanced AST Normalizer for structural fingerprinting.

    Performs:
    - Method alphabetical sorting
    - Parameter/local variable canonicalization (param1, var1)
    - Docstring stripping
    - Long constant replacement
    - Import removal
    - Decorator normalization
    

**Inherits from**: ast.NodeTransformer

### Methods

#### __init__
**Parameters**: self

#### reset
**Parameters**: self

#### visit_ClassDef
**Parameters**: self, node
**Returns**: ast.ClassDef
**Description**: Normalize class: sort methods, strip docstrings.

#### visit_FunctionDef
**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Normalize function: canonicalize params, strip docstrings.

#### visit_AsyncFunctionDef
**Parameters**: self, node
**Returns**: ast.AsyncFunctionDef
**Description**: Same normalization for async functions.

#### visit_Name
**Parameters**: self, node
**Returns**: ast.Name
**Description**: Canonicalize variable names.

#### visit_Constant
**Parameters**: self, node
**Returns**: ast.Constant
**Description**: Replace long constants.

#### visit_Import
**Parameters**: self, node
**Returns**: ast.Import | None
**Description**: Remove imports.

#### visit_ImportFrom
**Parameters**: self, node
**Returns**: ast.ImportFrom | None
**Description**: Remove imports.



## Function: extract_layer

**Parameters**: file_path
**Returns**: str
**Description**: Extract layer designation from file path.



## Function: find_agent_classes

**Parameters**: base_path
**Returns**: list[AgentInfo]
**Description**: Find all PascalCase *Agent classes in the codebase.



## Function: generate_fingerprint

**Parameters**: file_path, class_name
**Returns**: tuple[str, str]
**Description**: Generate SHA256 fingerprint for a class using normalized AST.



## Function: calculate_similarity

**Parameters**: code1, code2
**Returns**: float
**Description**: Calculate structural similarity between two normalized ASTs.



## Function: analyze_redundancy

**Parameters**: base_path
**Returns**: dict
**Description**: Main analysis function.



## Function: print_report

**Parameters**: results
**Description**: Print formatted report.



## Function: __init__

**Parameters**: self


## Function: reset

**Parameters**: self


## Function: visit_ClassDef

**Parameters**: self, node
**Returns**: ast.ClassDef
**Description**: Normalize class: sort methods, strip docstrings.



## Function: visit_FunctionDef

**Parameters**: self, node
**Returns**: ast.FunctionDef
**Description**: Normalize function: canonicalize params, strip docstrings.



## Function: visit_AsyncFunctionDef

**Parameters**: self, node
**Returns**: ast.AsyncFunctionDef
**Description**: Same normalization for async functions.



## Function: visit_Name

**Parameters**: self, node
**Returns**: ast.Name
**Description**: Canonicalize variable names.



## Function: visit_Constant

**Parameters**: self, node
**Returns**: ast.Constant
**Description**: Replace long constants.



## Function: visit_Import

**Parameters**: self, node
**Returns**: ast.Import | None
**Description**: Remove imports.



## Function: visit_ImportFrom

**Parameters**: self, node
**Returns**: ast.ImportFrom | None
**Description**: Remove imports.



## Usage Examples

### Class Usage

```python
# Using AgentInfo
agentinfo = AgentInfo()
```

```python
# Using ASTNormalizer
astnormalizer = ASTNormalizer()
astnormalizer.reset()
astnormalizer.visit_ClassDef()
```

### Function Usage

```python
# Using extract_layer
result = extract_layer(file_path)
```

```python
# Using find_agent_classes
result = find_agent_classes(base_path)
```

```python
# Using generate_fingerprint
result = generate_fingerprint(file_path, class_name)
```



---
**Generated**: 2026-03-26T09:39:04.764801
**Type**: api_reference
**Quality**: comprehensive
