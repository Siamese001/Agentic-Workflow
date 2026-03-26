# API Documentation: complexity_analyzer_util

**Target Audience**: developers, api_users

# complexity_analyzer_util API Documentation

**File**: `complexity_analyzer_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **calculate_mccabe_complexity** -> int
- **check_function_complexity** -> tuple[bool, int]
- **analyze_file_complexity** -> list[dict[str, any]]


## Function: calculate_mccabe_complexity

**Parameters**: node
**Returns**: int
**Description**: 
    Calculate cyclomatic complexity of an AST node.

    Complexity = 1 + number of decision points (if, for, while, and, or, except)

    Args:
        node: AST node to analyze (typically FunctionDef or AsyncFunctionDef)

    Returns:
        Cyclomatic complexity score (minimum 1)

    Example:
        >>> import ast
        >>> code = "def foo(x):\n    if x > 0:\n        return 1\n    return 0"
        >>> tree = ast.parse(code)
        >>> calculate_mccabe_complexity(tree.body[0])
        2
    



## Function: check_function_complexity

**Parameters**: node, max_complexity
**Returns**: tuple[bool, int]
**Description**: 
    Check if function exceeds complexity threshold.

    Args:
        node: AST node to analyze
        max_complexity: Maximum allowed complexity (default 10)

    Returns:
        Tuple of (passes_check, actual_complexity)

    Example:
        >>> import ast
        >>> code = "def simple(): return 1"
        >>> tree = ast.parse(code)
        >>> check_function_complexity(tree.body[0], max_complexity=10)
        (True, 1)
    



## Function: analyze_file_complexity

**Parameters**: file_path, max_complexity
**Returns**: list[dict[str, any]]
**Description**: 
    Analyze all functions in a file for complexity violations.

    Args:
        file_path: Path to Python file
        max_complexity: Maximum allowed complexity

    Returns:
        List of violations with file_path, line_number, function_name, complexity
    



## Usage Examples

### Function Usage

```python
# Using calculate_mccabe_complexity
result = calculate_mccabe_complexity(node)
```

```python
# Using check_function_complexity
result = check_function_complexity(node, max_complexity)
```

```python
# Using analyze_file_complexity
result = analyze_file_complexity(file_path, max_complexity)
```



---
**Generated**: 2026-03-26T09:39:04.661085
**Type**: api_reference
**Quality**: comprehensive
