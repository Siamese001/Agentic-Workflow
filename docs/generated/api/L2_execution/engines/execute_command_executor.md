# API Documentation: execute_command_executor

**Target Audience**: developers, api_users

# execute_command_executor API Documentation

**File**: `execute_command_executor.py`
**Classes**: 3
**Functions**: 10

## Classes

- **ExecuteCommandArgs** (inherits from TypedDict)
- **ExecutionTimeoutError** (inherits from Exception)
- **ExecutionError** (inherits from Exception)

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **get_project_root** -> Path
- **validate_sandbox** -> Path
- **is_command_allowed** -> bool
- **execute_with_timeout** -> subprocess.CompletedProcess
- **execute_command** -> tuple[int, str, str]
- **check_tool_installed** -> bool
- **run_linter** -> tuple[bool, str]
- **run_autofix_tools** -> dict[str, bool]


## Class: ExecuteCommandArgs

**Description**: Brief description of functionality and purpose.

**Inherits from**: TypedDict



## Class: ExecutionTimeoutError

**Description**: Raised when command execution exceeds timeout.

**Inherits from**: Exception



## Class: ExecutionError

**Description**: Raised when command execution fails.

**Inherits from**: Exception



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: get_project_root

**Returns**: Path
**Description**: 
    Determines the project root by looking for a .git directory or pyproject.toml.
    Caches the result for subsequent calls.
    



## Function: validate_sandbox

**Parameters**: path
**Returns**: Path
**Description**: 
    Validates that a given path is within the project's sandbox (project root).

    Args:
        path: The path to validate, relative to the project root.

    Returns:
        The absolute, resolved path within the sandbox.

    Raises:
        ValueError: If the path attempts to escape the project root.
    



## Function: is_command_allowed

**Parameters**: command
**Returns**: bool
**Description**: 
    Check if a command is allowed to execute.

    Args:
        command: Command to check

    Returns:
        True if command is allowed, False otherwise
    



## Function: execute_with_timeout

**Parameters**: command, timeout, cwd, capture_output, check
**Returns**: subprocess.CompletedProcess
**Description**: 
    Execute a command with timeout protection.

    Args:
        command: Command and arguments as list
        timeout: Timeout in seconds (max 300)
        cwd: Working directory (relative to project root)
        capture_output: Capture stdout and stderr
        check: Raise exception on non-zero exit code

    Returns:
        CompletedProcess instance

    Raises:
        ExecutionTimeoutError: If command exceeds timeout
        ExecutionError: If command fails and check=True
    



## Function: execute_command

**Parameters**: args
**Returns**: tuple[int, str, str]
**Description**: 
    Execute a shell command with sandbox validation and timeout protection.

    Args:
        args: ExecuteCommandArgs with command, args, and options

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        ExecutionTimeoutError: If command exceeds timeout
        ExecutionError: If command is not allowed
    



## Function: check_tool_installed

**Parameters**: tool_name
**Returns**: bool
**Description**: 
    Check if a tool is installed and available.

    Args:
        tool_name: Name of the tool to check

    Returns:
        True if tool is installed, False otherwise
    



## Function: run_linter

**Parameters**: tool, target_path, extra_args
**Returns**: tuple[bool, str]
**Description**: 
    Run a linter tool on the codebase.
    Args:
        tool: Linter tool name ('isort', 'autoflake', 'black', 'flake8', 'mypy')
        target_path: Path to lint (relative to project root)
        extra_args: Additional arguments for the linter

    Returns:
        Tuple of (success, output)
    



## Function: run_autofix_tools

**Parameters**: target_path
**Returns**: dict[str, bool]
**Description**: 
    Run auto-fix tools (isort, autoflake) on the codebase.

    Args:
        target_path: Path to fix (relative to project root)

    Returns:
        Dictionary of tool results
    



## Usage Examples

### Class Usage

```python
# Using ExecuteCommandArgs
executecommandargs = ExecuteCommandArgs()
```

```python
# Using ExecutionTimeoutError
executiontimeouterror = ExecutionTimeoutError()
```

```python
# Using ExecutionError
executionerror = ExecutionError()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using get_project_root
result = get_project_root()
```



---
**Generated**: 2026-03-26T09:39:03.760460
**Type**: api_reference
**Quality**: comprehensive
