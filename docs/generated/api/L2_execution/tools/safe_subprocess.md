# API Documentation: safe_subprocess

**Target Audience**: developers, api_users

# safe_subprocess API Documentation

**File**: `safe_subprocess.py`
**Classes**: 0
**Functions**: 7


## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **safe_subprocess_run** -> subprocess.CompletedProcess
- **safe_subprocess_call** -> int
- **safe_subprocess_check_call** -> None
- **safe_subprocess_check_output** -> str | bytes
- **safe_subprocess_popen** -> subprocess.Popen


## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: safe_subprocess_run

**Parameters**: argv
**Returns**: subprocess.CompletedProcess
**Description**: 
    Safe subprocess.run wrapper with mutation fence protection.

    Args:
        argv: Command arguments as a list (no shell)
        cwd: Working directory for the command
        capture_output: Whether to capture stdout/stderr
        text: Whether to decode output as text
        check: Whether to raise exception on non-zero exit
        allow_protected_root_mutation: Whether to allow commands that can mutate protected roots
        **kwargs: Additional arguments passed to subprocess.run

    Returns:
        subprocess.CompletedProcess result

    Raises:
        RuntimeError: If command attempts protected root mutation without override
    



## Function: safe_subprocess_call

**Parameters**: argv
**Returns**: int
**Description**: Safe subprocess.call wrapper.



## Function: safe_subprocess_check_call

**Parameters**: argv
**Returns**: None
**Description**: Safe subprocess.check_call wrapper.



## Function: safe_subprocess_check_output

**Parameters**: argv
**Returns**: str | bytes
**Description**: Safe subprocess.check_output wrapper.



## Function: safe_subprocess_popen

**Parameters**: argv
**Returns**: subprocess.Popen
**Description**: Safe subprocess.Popen wrapper.



## Usage Examples

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
# Using safe_subprocess_run
result = safe_subprocess_run(argv)
```



---
**Generated**: 2026-03-26T09:39:03.918232
**Type**: api_reference
**Quality**: comprehensive
