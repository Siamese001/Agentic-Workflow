# API Documentation: tool_invoker

**Target Audience**: developers, api_users

# tool_invoker API Documentation

**File**: `tool_invoker.py`
**Classes**: 1
**Functions**: 6

## Classes

- **ToolInvoker**

## Functions

- **__init__**
- **invoke** -> ToolCallResult
- **_validate_args** -> None
- **_validate_arg_type** -> None
- **_enforce_powershell_ban** -> None
- **_process_output** -> tuple[str, str, bool]


## Class: ToolInvoker

**Description**: Deterministic tool invoker with safety constraints.

### Methods

#### __init__
**Parameters**: self, max_stdout_bytes, max_stderr_bytes
**Description**: Initialize invoker with size limits.

        Args:
            max_stdout_bytes: Maximum stdout size before truncation
            max_stderr_bytes: Maximum stderr size before truncation
        

#### invoke
**Parameters**: self, call, registry
**Returns**: ToolCallResult
**Description**: Invoke a tool call with safety constraints.

        Args:
            call: Tool call to invoke
            registry: Tool registry

        Returns:
            Tool call result

        Raises:
            ValueError: If validation fails
        

#### _validate_args
**Parameters**: self, args, spec_args
**Returns**: None
**Description**: Validate arguments against tool specification.

        Args:
            args: Provided arguments
            spec_args: Expected argument specifications

        Raises:
            ValueError: If validation fails
        

#### _validate_arg_type
**Parameters**: self, name, value, kind
**Returns**: None
**Description**: Validate individual argument type.

        Args:
            name: Argument name
            value: Argument value
            kind: Expected kind

        Raises:
            ValueError: If type validation fails
        

#### _enforce_powershell_ban
**Parameters**: self, args
**Returns**: None
**Description**: Enforce PowerShell ban for subprocess tools.

        Args:
            args: Tool arguments

        Raises:
            ValueError: If PowerShell usage detected
        

#### _process_output
**Parameters**: self, stdout, stderr
**Returns**: tuple[str, str, bool]
**Description**: Process output with size limits and truncation.

        Args:
            stdout: Standard output
            stderr: Standard error

        Returns:
            Tuple of (processed_stdout, processed_stderr, was_truncated)
        



## Function: __init__

**Parameters**: self, max_stdout_bytes, max_stderr_bytes
**Description**: Initialize invoker with size limits.

        Args:
            max_stdout_bytes: Maximum stdout size before truncation
            max_stderr_bytes: Maximum stderr size before truncation
        



## Function: invoke

**Parameters**: self, call, registry
**Returns**: ToolCallResult
**Description**: Invoke a tool call with safety constraints.

        Args:
            call: Tool call to invoke
            registry: Tool registry

        Returns:
            Tool call result

        Raises:
            ValueError: If validation fails
        



## Function: _validate_args

**Parameters**: self, args, spec_args
**Returns**: None
**Description**: Validate arguments against tool specification.

        Args:
            args: Provided arguments
            spec_args: Expected argument specifications

        Raises:
            ValueError: If validation fails
        



## Function: _validate_arg_type

**Parameters**: self, name, value, kind
**Returns**: None
**Description**: Validate individual argument type.

        Args:
            name: Argument name
            value: Argument value
            kind: Expected kind

        Raises:
            ValueError: If type validation fails
        



## Function: _enforce_powershell_ban

**Parameters**: self, args
**Returns**: None
**Description**: Enforce PowerShell ban for subprocess tools.

        Args:
            args: Tool arguments

        Raises:
            ValueError: If PowerShell usage detected
        



## Function: _process_output

**Parameters**: self, stdout, stderr
**Returns**: tuple[str, str, bool]
**Description**: Process output with size limits and truncation.

        Args:
            stdout: Standard output
            stderr: Standard error

        Returns:
            Tuple of (processed_stdout, processed_stderr, was_truncated)
        



## Usage Examples

### Class Usage

```python
# Using ToolInvoker
toolinvoker = ToolInvoker()
toolinvoker.invoke()
```

### Function Usage

```python
# Using __init__
result = __init__(max_stdout_bytes, max_stderr_bytes)
```

```python
# Using invoke
result = invoke(call, registry)
```

```python
# Using _validate_args
result = _validate_args(args, spec_args)
```



---
**Generated**: 2026-03-26T09:39:04.252169
**Type**: api_reference
**Quality**: comprehensive
