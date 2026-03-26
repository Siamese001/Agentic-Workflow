# API Documentation: builtin_tools

**Target Audience**: developers, api_users

# builtin_tools API Documentation

**File**: `builtin_tools.py`
**Classes**: 0
**Functions**: 5


## Functions

- **repo_rg_handler** -> str
- **expr_eval_handler** -> str
- **_evaluate_expression** -> Any
- **register_builtin_tools**
- **_eval**


## Function: repo_rg_handler

**Parameters**: args
**Returns**: str
**Description**: Search repository using Python (no external rg dependency).

    Args:
        args: Tool arguments

    Returns:
        JSON string with search results
    



## Function: expr_eval_handler

**Parameters**: args
**Returns**: str
**Description**: Evaluate simple arithmetic expressions without Python eval.

    Args:
        args: Tool arguments

    Returns:
        String result of evaluation
    



## Function: _evaluate_expression

**Parameters**: expr
**Returns**: Any
**Description**: Evaluate a simple arithmetic expression safely.

    Args:
        expr: Expression string

    Returns:
        Evaluated result
    



## Function: register_builtin_tools

**Description**: Register all built-in PTC tools. Idempotent.



## Function: _eval

**Parameters**: node


## Usage Examples

### Function Usage

```python
# Using repo_rg_handler
result = repo_rg_handler(args)
```

```python
# Using expr_eval_handler
result = expr_eval_handler(args)
```

```python
# Using _evaluate_expression
result = _evaluate_expression(expr)
```



---
**Generated**: 2026-03-26T09:39:04.241746
**Type**: api_reference
**Quality**: comprehensive
