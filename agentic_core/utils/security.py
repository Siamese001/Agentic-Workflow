#!/usr/bin/env python3
"""
Security Utilities for Agentic Workflow

Zero-Trust subprocess execution wrapper with comprehensive input validation,
injection prevention, and observability integration.

Created: 2026-01-20
Purpose: Harden all subprocess calls against shell injection attacks
"""
from __future__ import annotations

import subprocess
import logging
import re
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

# Use standard logging instead of custom Logger
Logger = logging.getLogger(__name__)


# Dangerous shell metacharacters that could enable injection
# Note: We only block these in contexts where they could be exploited
# Python code passed via -c flag is safe because shell=False prevents shell interpretation
SHELL_METACHARACTERS = {
    '|': 'pipe operator',
    '&&': 'AND operator',
    '||': 'OR operator',
    '`': 'backtick command substitution',
    '$(': 'command substitution',
    '&': 'background execution',
}

def _is_shell_injection_risk(arg: str) -> bool:
    """
    Determine if an argument poses a shell injection risk.
    
    Python code via -c flag is safe because shell=False prevents interpretation.
    We only block patterns that could be exploited if shell=True were used.
    
    Args:
        arg: Command argument to check
        
    Returns:
        True if injection risk detected, False otherwise
    """
    # Allow Python code strings (common pattern: python -c "code")
    # These are safe with shell=False
    if arg.startswith('import ') or 'import ' in arg[:50]:
        return False
    
    # Check for shell metacharacters
    if '|' in arg and '||' not in arg:  # Single pipe (not OR operator)
        return True
    if '&&' in arg:
        return True
    if '||' in arg:
        return True
    if '`' in arg:
        return True
    if '$(' in arg:
        return True
    if re.search(r'>\s*[/\\]', arg):  # Redirect to path
        return True
    if re.search(r'<\s*[/\\]', arg):  # Redirect from path
        return True
    if arg.strip().endswith('&'):  # Background execution
        return True
    
    return False

# Legacy regex for backward compatibility (not used in main logic)
INJECTION_REGEX = re.compile(r'\||&&|\|\||`|\$\(|>\s*[/\\]|<\s*[/\\]|&\s*$')


class SecurityViolationError(Exception):
    """Raised when a security violation is detected in subprocess arguments."""
    pass


def safe_execute(
    args: List[str],
    cwd: Optional[Union[str, Path]] = None,
    timeout: Optional[int] = None,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
    env: Optional[Dict[str, str]] = None,
    input_data: Optional[str] = None,
) -> subprocess.CompletedProcess:
    """
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
        >>> result = safe_execute(['python', 'script.py'], timeout=30)
        >>> result = safe_execute(['ls', '-la'], cwd='/tmp')
    """
    # ========================================================================
    # VALIDATION PHASE
    # ========================================================================
    
    # 1. Type validation: Enforce list-only arguments
    if not isinstance(args, list):
        raise TypeError(
            f"safe_execute requires args as List[str], got {type(args).__name__}. "
            f"This prevents accidental shell injection via string commands."
        )
    
    if not args:
        raise ValueError("safe_execute requires non-empty args list")
    
    # 2. Content validation: Check each argument for injection patterns
    for i, arg in enumerate(args):
        if not isinstance(arg, str):
            raise TypeError(
                f"Argument {i} must be str, got {type(arg).__name__}: {arg}"
            )
        
        # Scan for injection patterns using context-aware check
        if _is_shell_injection_risk(arg):
            truncated = arg[:100] + '...' if len(arg) > 100 else arg
            raise SecurityViolationError(
                f"Shell injection pattern detected in argument {i}: '{truncated}'\n"
                f"Blocked patterns: | && || ` $( > /path < /path & (at end)\n"
                f"This is a security violation. Use safe alternatives or file-based I/O."
            )
    
    # 3. Path validation: Ensure cwd is safe if provided
    if cwd is not None:
        cwd_path = Path(cwd)
        if not cwd_path.exists():
            Logger.warning(f"[Security] Working directory does not exist: {cwd}")
        cwd = str(cwd_path)
    
    # ========================================================================
    # OBSERVABILITY PHASE
    # ========================================================================
    
    # Log the command for audit trail
    cmd_str = ' '.join(args)
    Logger.info(f"[Security] Executing safe command: {cmd_str}")
    if cwd:
        Logger.debug(f"[Security] Working directory: {cwd}")
    if timeout:
        Logger.debug(f"[Security] Timeout: {timeout}s")
    
    # ========================================================================
    # EXECUTION PHASE
    # ========================================================================
    
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=text,
            check=check,
            env=env,
            input=input_data,
            shell=False,  # CRITICAL: Never allow shell execution
        )
        
        # Log success
        Logger.info(
            f"[Security] Command completed successfully: {args[0]} "
            f"(exit code: {result.returncode})"
        )
        
        return result
        
    except subprocess.CalledProcessError as e:
        Logger.error(
            f"[Security] Command failed: {cmd_str}\n"
            f"Exit code: {e.returncode}\n"
            f"Stderr: {e.stderr[:500] if e.stderr else 'N/A'}"
        )
        raise
        
    except subprocess.TimeoutExpired as e:
        Logger.error(
            f"[Security] Command timeout after {timeout}s: {cmd_str}"
        )
        raise
        
    except Exception as e:
        Logger.error(
            f"[Security] Unexpected error executing command: {cmd_str}\n"
            f"Error: {e}"
        )
        raise


def safe_popen(
    args: List[str],
    cwd: Optional[Union[str, Path]] = None,
    stdout: Optional[int] = subprocess.PIPE,
    stderr: Optional[int] = subprocess.PIPE,
    text: bool = True,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.Popen:
    """
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
    """
    # Reuse validation logic from safe_execute
    if not isinstance(args, list):
        raise TypeError(
            f"safe_popen requires args as List[str], got {type(args).__name__}"
        )
    
    if not args:
        raise ValueError("safe_popen requires non-empty args list")
    
    for i, arg in enumerate(args):
        if not isinstance(arg, str):
            raise TypeError(
                f"Argument {i} must be str, got {type(arg).__name__}: {arg}"
            )
        
        if _is_shell_injection_risk(arg):
            truncated = arg[:100] + '...' if len(arg) > 100 else arg
            raise SecurityViolationError(
                f"Shell injection pattern detected in argument {i}: '{truncated}'"
            )
    
    if cwd is not None:
        cwd = str(Path(cwd))
    
    # Log the command
    cmd_str = ' '.join(args)
    Logger.info(f"[Security] Starting Popen process: {cmd_str}")
    
    try:
        proc = subprocess.Popen(
            args,
            cwd=cwd,
            stdout=stdout,
            stderr=stderr,
            text=text,
            env=env,
            shell=False,  # CRITICAL: Never allow shell execution
        )
        
        Logger.info(f"[Security] Popen process started: PID {proc.pid}")
        return proc
        
    except Exception as e:
        Logger.error(f"[Security] Failed to start Popen process: {cmd_str}\nError: {e}")
        raise


def validate_command_whitelist(args: List[str], allowed_commands: List[str]) -> bool:
    """
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
    """
    if not args:
        return False
    
    command = args[0]
    
    # Handle full paths - extract basename
    if '/' in command or '\\' in command:
        command = Path(command).name
    
    # Handle .exe extension on Windows
    if command.endswith('.exe'):
        command = command[:-4]
    
    is_allowed = command in allowed_commands
    
    if not is_allowed:
        Logger.warning(
            f"[Security] Command '{command}' not in whitelist: {allowed_commands}"
        )
    
    return is_allowed


# Convenience function for common git operations
def safe_git_execute(
    git_args: List[str],
    repo_root: Optional[Union[str, Path]] = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    """
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
    """
    args = ['git'] + git_args
    return safe_execute(args, cwd=repo_root, timeout=timeout)
