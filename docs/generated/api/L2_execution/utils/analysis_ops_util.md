# API Documentation: analysis_ops_util

**Target Audience**: developers, api_users

# analysis_ops_util API Documentation

**File**: `analysis_ops_util.py`
**Classes**: 0
**Functions**: 6


## Functions

- **validate_python_syntax** -> tuple[bool, str | None]
- **run_ruff_check** -> tuple[int, str, str]
- **run_black_format** -> tuple[int, str, str]
- **analyze_ast** -> dict[str, Any]
- **count_lines_of_code** -> dict[str, int]
- **detect_security_issues** -> list[dict[str, Any]]


## Function: validate_python_syntax

**Parameters**: file_path
**Returns**: tuple[bool, str | None]
**Description**: 
    Parse a Python file to check for syntax errors without executing it.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple[bool, Optional[str]]: (True, None) if valid, (False, error_message) if invalid
    



## Function: run_ruff_check

**Parameters**: file_path, fix
**Returns**: tuple[int, str, str]
**Description**: 
    Run Ruff linter on a file.

    Args:
        file_path: Path to the file to check
        fix: Whether to apply fixes automatically

    Returns:
        Tuple[int, str, str]: (returncode, stdout, stderr)
    



## Function: run_black_format

**Parameters**: file_path, check_only
**Returns**: tuple[int, str, str]
**Description**: 
    Run Black formatter on a file.

    Args:
        file_path: Path to the file to format
        check_only: Only check formatting without modifying

    Returns:
        Tuple[int, str, str]: (returncode, stdout, stderr)
    



## Function: analyze_ast

**Parameters**: file_path
**Returns**: dict[str, Any]
**Description**: 
    Analyze Python file AST for structural information.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dict with AST analysis results
    



## Function: count_lines_of_code

**Parameters**: file_path
**Returns**: dict[str, int]
**Description**: 
    Count lines of code, comments, and blank lines.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dict with line counts
    



## Function: detect_security_issues

**Parameters**: file_path
**Returns**: list[dict[str, Any]]
**Description**: 
    Detect common security issues in Python code.

    Args:
        file_path: Path to the file to analyze

    Returns:
        List of detected security issues
    



## Usage Examples

### Function Usage

```python
# Using validate_python_syntax
result = validate_python_syntax(file_path)
```

```python
# Using run_ruff_check
result = run_ruff_check(file_path, fix)
```

```python
# Using run_black_format
result = run_black_format(file_path, check_only)
```



---
**Generated**: 2026-03-26T09:39:04.049491
**Type**: api_reference
**Quality**: comprehensive
