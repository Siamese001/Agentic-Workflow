# API Documentation: safe_subprocess_handler_enforcer

**Target Audience**: developers, api_users

# safe_subprocess_handler_enforcer API Documentation

**File**: `safe_subprocess_handler_enforcer.py`
**Classes**: 0
**Functions**: 3


## Functions

- **safe_run** -> subprocess.CompletedProcess | subprocess.Popen
- **safe_popen** -> subprocess.Popen
- **safe_communicate** -> tuple[str | bytes | None, str | bytes | None]


## Function: safe_run

**Parameters**: command
**Returns**: subprocess.CompletedProcess | subprocess.Popen
**Description**: 
    Safely run a subprocess with security validation and lifecycle tracking.

    Args:
        command: The command to run as a list of strings.
        capture_output: Whether to capture stdout/stderr (default: True).
        text: Whether to decode output as text (default: True).
        timeout: Timeout in seconds (default: 60, None for no timeout).
        cwd: Working directory for the command.
        env: Environment variables for the command.
        sanitize_output: Whether to sanitize captured output (default: True).
        max_output_chars: Max chars for sanitized output (default: 2000).
        check: Whether to raise on non-zero exit (default: False).
        **kwargs: Additional arguments passed to subprocess.run.

    Returns:
        subprocess.CompletedProcess with the result.

    Raises:
        SecurityViolation: If command is blocked by the firewall.
        subprocess.TimeoutExpired: If command exceeds timeout.
        subprocess.CalledProcessError: If check=True and command fails.
    



## Function: safe_popen

**Parameters**: command
**Returns**: subprocess.Popen
**Description**: 
    Safely spawn a subprocess with security validation and PID tracking.

    Use this for long-running processes that need to be managed asynchronously.
    The PID is automatically registered with ProcessGuard for cleanup.

    Args:
        command: The command to run as a list of strings.
        stdout: stdout handling (default: PIPE).
        stderr: stderr handling (default: PIPE).
        cwd: Working directory for the command.
        env: Environment variables for the command.
        **kwargs: Additional arguments passed to subprocess.Popen.

    Returns:
        subprocess.Popen object with registered PID.

    Raises:
        SecurityViolation: If command is blocked by the firewall.
    



## Function: safe_communicate

**Parameters**: process, input_data, timeout, sanitize_output, max_output_chars
**Returns**: tuple[str | bytes | None, str | bytes | None]
**Description**: 
    Safely communicate with a Popen process and unregister on completion.

    Args:
        process: The Popen process to communicate with.
        input_data: Data to send to stdin.
        timeout: Timeout in seconds.
        sanitize_output: Whether to sanitize output.
        max_output_chars: Max chars for sanitized output.

    Returns:
        Tuple of (stdout, stderr).
    



## Usage Examples

### Function Usage

```python
# Using safe_run
result = safe_run(command)
```

```python
# Using safe_popen
result = safe_popen(command)
```

```python
# Using safe_communicate
result = safe_communicate(process, input_data)
```



---
**Generated**: 2026-03-26T09:39:04.927568
**Type**: api_reference
**Quality**: comprehensive
