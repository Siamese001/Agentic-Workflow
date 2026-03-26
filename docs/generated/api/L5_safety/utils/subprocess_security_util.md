# API Documentation: subprocess_security_util

**Target Audience**: developers, api_users

# subprocess_security_util API Documentation

**File**: `subprocess_security_util.py`
**Classes**: 1
**Functions**: 5

## Classes

- **SecurityViolationError** (inherits from Exception)

## Functions

- **_is_shell_injection_risk** -> bool
- **safe_execute** -> subprocess.CompletedProcess
- **safe_popen** -> subprocess.Popen
- **validate_command_whitelist** -> bool
- **safe_git_execute** -> subprocess.CompletedProcess


## Class: SecurityViolationError

**Description**: Raised when a security violation is detected in subprocess arguments.

**Inherits from**: Exception



## Function: _is_shell_injection_risk

**Parameters**: arg
**Returns**: bool
**Description**: 
    Determine if an argument poses a shell injection risk.

    Python code via -c flag is safe because shell=False prevents interpretation.
    We only block patterns that could be exploited if shell=True were used.

    Args:
        arg: Command argument to check

    Returns:
        True if injection risk detected, False otherwise
    



## Function: safe_execute

**Parameters**: args, cwd, timeout, capture_output, text, check, env, input_data
**Returns**: subprocess.CompletedProcess
**Description**: 
    Hardened wrapper for subprocess.run with zero-trust security constraints.

    **Security Guarantees:**
    - NO shell execution (shell=False enforced)
    - List-only arguments (no string commands)
    - Input sanitization (blocks injection characters)
    - Comprehensive logging for observability
    - Timeout enforcement

    Args:
        args: Command and arguments as a list of strings (REQUIRED)
        cwd: Working directory for command execution
        timeout: Maximum execution time in seconds (default: None)
        capture_output: Capture stdout/stderr (default: True)
        text: Return output as text instead of bytes (default: True)
        check: Raise CalledProcessError on non-zero exit (default: True)
        env: Environment variables dict (default: None = inherit)
        input_data: Data to send to stdin (default: None)

    Returns:
        subprocess.CompletedProcess with stdout, stderr, returncode

    Raises:
        SecurityViolationError: If injection patterns detected
        TypeError: If args is not a list
        subprocess.CalledProcessError: If check=True and command fails
        subprocess.TimeoutExpired: If timeout exceeded

    Example:
        >>> result = safe_execute(['git', 'status'])
        >>> result = safe_execute(['python', 'script.py'], timeout=DEFAULT_TIMEOUT)
        >>> result = safe_execute(['ls', '-la'], cwd='/tmp')
    



## Function: safe_popen

**Parameters**: args, cwd, stdout, stderr, text, env
**Returns**: subprocess.Popen
**Description**: 
    Hardened wrapper for subprocess.Popen with zero-trust security constraints.

    Use this for long-running processes that need streaming output.
    For simple command execution, prefer safe_execute().

    Args:
        args: Command and arguments as a list of strings (REQUIRED)
        cwd: Working directory for command execution
        stdout: stdout handling (default: PIPE)
        stderr: stderr handling (default: PIPE)
        text: Return output as text instead of bytes (default: True)
        env: Environment variables dict (default: None = inherit)

    Returns:
        subprocess.Popen object for process management

    Raises:
        SecurityViolationError: If injection patterns detected
        TypeError: If args is not a list

    Example:
        >>> proc = safe_popen(['python', 'server.py'])
        >>> for line in proc.stdout:
        ...     print(line, end='')
        >>> proc.wait()
    



## Function: validate_command_whitelist

**Parameters**: args, allowed_commands
**Returns**: bool
**Description**: 
    Validate that the command is in an allowed whitelist.

    Use this for additional security when only specific commands should be allowed.

    Args:
        args: Command and arguments list
        allowed_commands: List of allowed command names (e.g., ['git', 'python', 'black'])

    Returns:
        True if command is allowed, False otherwise

    Example:
        >>> args = ['git', 'status']
        >>> if validate_command_whitelist(args, ['git', 'python']):
        ...     safe_execute(args)
    



## Function: safe_git_execute

**Parameters**: git_args, repo_root, timeout
**Returns**: subprocess.CompletedProcess
**Description**: 
    Convenience wrapper for safe git command execution.

    Args:
        git_args: Git subcommand and arguments (without 'git' prefix)
        repo_root: Repository root directory (default: current directory)
        timeout: Command timeout in seconds (default: 30)

    Returns:
        subprocess.CompletedProcess

    Example:
        >>> result = safe_git_execute(['status'])
        >>> result = safe_git_execute(['commit', '-m', 'message'], repo_root='/path/to/repo')
    



## Usage Examples

### Class Usage

```python
# Using SecurityViolationError
securityviolationerror = SecurityViolationError()
```

### Function Usage

```python
# Using _is_shell_injection_risk
result = _is_shell_injection_risk(arg)
```

```python
# Using safe_execute
result = safe_execute(args, cwd)
```

```python
# Using safe_popen
result = safe_popen(args, cwd)
```



---
**Generated**: 2026-03-26T09:39:05.692771
**Type**: api_reference
**Quality**: comprehensive
