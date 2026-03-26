# API Documentation: process_guardrail

**Target Audience**: developers, api_users

# process_guardrail API Documentation

**File**: `process_guardrail.py`
**Classes**: 2
**Functions**: 14

## Classes

- **SecurityViolation** (inherits from Exception)
- **ProcessGuard**

## Functions

- **__init__**
- **__new__** -> 'ProcessGuard'
- **_initialize** -> None
- **get_instance** -> 'ProcessGuard'
- **_register_atexit** -> None
- **_atexit_cleanup** -> None
- **register_pid** -> None
- **unregister_pid** -> None
- **get_active_pids** -> set[int]
- **terminate_all** -> dict[str, list[int]]
- **_kill_process** -> None
- **validate_command** -> bool
- **cleanup** -> dict[str, list[int]]
- **reset_instance** -> None


## Class: SecurityViolation

**Description**: Raised when a command violates security policy.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, command, reason



## Class: ProcessGuard

**Description**: 
    Singleton Process Guard for managing spawned process lifecycles.

    Features:
    - Thread-safe PID registry
    - Automatic cleanup on interpreter exit via atexit
    - Command validation firewall

    Usage:
        guard = ProcessGuard.get_instance()
        guard.validate_command(["python", "script.py"])  # OK
        guard.validate_command(["pip", "install", "pkg"])  # Raises SecurityViolation

        # After spawning a process:
        guard.register_pid(process.pid)

        # Cleanup:
        guard.terminate_all()
    

### Methods

#### __new__
**Parameters**: cls
**Returns**: 'ProcessGuard'
**Description**: Ensure singleton pattern.

#### _initialize
**Parameters**: self
**Returns**: None
**Description**: Initialize the guard state.

#### get_instance
**Parameters**: cls
**Returns**: 'ProcessGuard'
**Description**: Get the singleton instance.

#### _register_atexit
**Parameters**: self
**Returns**: None
**Description**: Register cleanup with atexit as fail-safe.

#### _atexit_cleanup
**Parameters**: self
**Returns**: None
**Description**: Cleanup handler called on interpreter exit.

#### register_pid
**Parameters**: self, pid
**Returns**: None
**Description**: 
        Register a PID for lifecycle tracking.

        Args:
            pid: The process ID to track.
        

#### unregister_pid
**Parameters**: self, pid
**Returns**: None
**Description**: 
        Unregister a PID (e.g., after normal termination).

        Args:
            pid: The process ID to stop tracking.
        

#### get_active_pids
**Parameters**: self
**Returns**: set[int]
**Description**: Get a copy of currently tracked PIDs.

#### terminate_all
**Parameters**: self
**Returns**: dict[str, list[int]]
**Description**: 
        Terminate all registered processes.

        Returns:
            Dict with 'terminated' and 'failed' PID lists.
        

#### _kill_process
**Parameters**: self, pid
**Returns**: None
**Description**: 
        Kill a process by PID.

        Uses SIGTERM first, then SIGKILL if needed.
        Platform-aware for Windows vs Unix.
        

#### validate_command
**Parameters**: self, command
**Returns**: bool
**Description**: 
        Validate a command against the security firewall.

        Args:
            command: The command as a list of strings.

        Returns:
            True if command is allowed.

        Raises:
            SecurityViolation: If command is blocked.
        

#### cleanup
**Parameters**: self
**Returns**: dict[str, list[int]]
**Description**: Alias for terminate_all() for API consistency.

#### reset_instance
**Parameters**: cls
**Returns**: None
**Description**: 
        Reset the singleton instance (for testing only).

        WARNING: This is intended for test isolation only.
        



## Function: __init__

**Parameters**: self, command, reason


## Function: __new__

**Parameters**: cls
**Returns**: 'ProcessGuard'
**Description**: Ensure singleton pattern.



## Function: _initialize

**Parameters**: self
**Returns**: None
**Description**: Initialize the guard state.



## Function: get_instance

**Parameters**: cls
**Returns**: 'ProcessGuard'
**Description**: Get the singleton instance.



## Function: _register_atexit

**Parameters**: self
**Returns**: None
**Description**: Register cleanup with atexit as fail-safe.



## Function: _atexit_cleanup

**Parameters**: self
**Returns**: None
**Description**: Cleanup handler called on interpreter exit.



## Function: register_pid

**Parameters**: self, pid
**Returns**: None
**Description**: 
        Register a PID for lifecycle tracking.

        Args:
            pid: The process ID to track.
        



## Function: unregister_pid

**Parameters**: self, pid
**Returns**: None
**Description**: 
        Unregister a PID (e.g., after normal termination).

        Args:
            pid: The process ID to stop tracking.
        



## Function: get_active_pids

**Parameters**: self
**Returns**: set[int]
**Description**: Get a copy of currently tracked PIDs.



## Function: terminate_all

**Parameters**: self
**Returns**: dict[str, list[int]]
**Description**: 
        Terminate all registered processes.

        Returns:
            Dict with 'terminated' and 'failed' PID lists.
        



## Function: _kill_process

**Parameters**: self, pid
**Returns**: None
**Description**: 
        Kill a process by PID.

        Uses SIGTERM first, then SIGKILL if needed.
        Platform-aware for Windows vs Unix.
        



## Function: validate_command

**Parameters**: self, command
**Returns**: bool
**Description**: 
        Validate a command against the security firewall.

        Args:
            command: The command as a list of strings.

        Returns:
            True if command is allowed.

        Raises:
            SecurityViolation: If command is blocked.
        



## Function: cleanup

**Parameters**: self
**Returns**: dict[str, list[int]]
**Description**: Alias for terminate_all() for API consistency.



## Function: reset_instance

**Parameters**: cls
**Returns**: None
**Description**: 
        Reset the singleton instance (for testing only).

        WARNING: This is intended for test isolation only.
        



## Usage Examples

### Class Usage

```python
# Using SecurityViolation
securityviolation = SecurityViolation()
```

```python
# Using ProcessGuard
processguard = ProcessGuard()
processguard.get_instance()
processguard.register_pid()
```

### Function Usage

```python
# Using __init__
result = __init__(command, reason)
```

```python
# Using __new__
result = __new__(cls)
```

```python
# Using _initialize
result = _initialize()
```



---
**Generated**: 2026-03-26T09:39:04.905319
**Type**: api_reference
**Quality**: comprehensive
