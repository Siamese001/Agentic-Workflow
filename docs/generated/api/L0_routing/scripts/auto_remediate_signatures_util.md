# API Documentation: auto_remediate_signatures_util

**Target Audience**: developers, api_users

# auto_remediate_signatures_util API Documentation

**File**: `auto_remediate_signatures_util.py`
**Classes**: 0
**Functions**: 7


## Functions

- **has_kwargs_in_signature** -> bool
- **find_heal_repository_methods** -> list[ast.FunctionDef]
- **inject_kwargs_in_signature** -> tuple[str, bool]
- **inject_kwargs_in_super_calls** -> tuple[str, bool]
- **remediate_file** -> bool
- **main**
- **replacer**


## Function: has_kwargs_in_signature

**Parameters**: func_node
**Returns**: bool
**Description**: Check if function definition already has **kwargs.



## Function: find_heal_repository_methods

**Parameters**: tree
**Returns**: list[ast.FunctionDef]
**Description**: Find all heal_repository method definitions in AST.



## Function: inject_kwargs_in_signature

**Parameters**: content, func_node
**Returns**: tuple[str, bool]
**Description**: 
    Inject **kwargs into function signature using line-based approach.
    Returns (modified_content, was_modified).
    



## Function: inject_kwargs_in_super_calls

**Parameters**: content
**Returns**: tuple[str, bool]
**Description**: 
    Inject **kwargs into super().heal_repository() calls.
    Returns (modified_content, was_modified).
    



## Function: remediate_file

**Parameters**: file_path
**Returns**: bool
**Description**: 
    Scans a file for heal_repository definition.
    If missing **kwargs, injects it into the signature and super() call.
    



## Function: main



## Function: replacer

**Parameters**: match


## Usage Examples

### Function Usage

```python
# Using has_kwargs_in_signature
result = has_kwargs_in_signature(func_node)
```

```python
# Using find_heal_repository_methods
result = find_heal_repository_methods(tree)
```

```python
# Using inject_kwargs_in_signature
result = inject_kwargs_in_signature(content, func_node)
```



---
**Generated**: 2026-03-26T09:39:02.759368
**Type**: api_reference
**Quality**: comprehensive
