from __future__ import annotations
"""
Secure Subprocess Execution - Timeout-Protected Command Execution
Prevents livelocks and provides safe subprocess management.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, TypedDict
from agentic_core.utils.security import safe_execute

class ExecuteCommandArgs(TypedDict):
    """Brief description of functionality and purpose."""
    command: str
    args: List[str]
    timeout: int
    cwd: Optional[str]
    capture_output: bool
_cached_project_root: Optional[Path] = None

def get_project_root() -> Path:
    """
    Determines the project root by looking for a .git directory or pyproject.toml.
    Caches the result for subsequent calls.
    """
    global _cached_project_root
    if _cached_project_root:
        return _cached_project_root
    current_path: Any = Path(__file__).resolve().parent
    while current_path != current_path.parent:
        if (current_path / '.git').exists() or (current_path / 'pyproject.toml').exists():
            _cached_project_root = current_path
            return current_path
    _cached_project_root = Path(__file__).resolve().parent
    return _cached_project_root

def validate_sandbox(path: str) -> Path:
    """
    Validates that a given path is within the project's sandbox (project root).

    Args:
        path: The path to validate, relative to the project root.

    Returns:
        The absolute, resolved path within the sandbox.

    Raises:
        ValueError: If the path attempts to escape the project root.
    """
    project_root: Any = get_project_root()
    abs_path: Any = (project_root / path).resolve()
    try:
        abs_path.relative_to(project_root)
    except ValueError:
        raise ValueError(f"Path '{path}' resolves to '{abs_path}' which is outside the project sandbox '{project_root}'.")
    return abs_path

class ExecutionTimeoutError(Exception):
    """Raised when command execution exceeds timeout."""

class ExecutionError(Exception):
    """Raised when command execution fails."""
ALLOWED_COMMANDS: Dict[str, List[str]] = {'python': [sys.executable, 'python', 'python3'], 'isort': ['isort'], 'autoflake': ['autoflake'], 'black': ['black'], 'flake8': ['flake8'], 'mypy': ['mypy'], 'pytest': ['pytest'], 'pip': ['pip', 'pip3']}
DANGEROUS_COMMANDS: List[str] = ['rm', 'del', 'rmdir', 'format', 'dd', 'mkfs', 'fdisk', 'shutdown', 'reboot', 'halt', 'poweroff', 'init']

def is_command_allowed(command: str) -> bool:
    """
    Check if a command is allowed to execute.

    Args:
        command: Command to check

    Returns:
        True if command is allowed, False otherwise
    """
    command_lower: Any = command.lower()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command_lower:
            return False
    command_name: Any = Path(command).stem.lower()
    for allowed_list in ALLOWED_COMMANDS.values():
        for allowed in allowed_list:
            if command_name == Path(allowed).stem.lower():
                return True
    return False

def execute_with_timeout(command: List[str], timeout: int=30, cwd: Optional[str]=None, capture_output: bool=True, check: bool=False) -> subprocess.CompletedProcess:
    """
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
    """
    if timeout > 300:
        raise ValueError('Timeout cannot exceed 300 seconds')
    if not command or not command[0]:
        raise ValueError('Command cannot be empty')
    if not is_command_allowed(command[0]):
        raise ExecutionError(f'Command not allowed: {command[0]}')
    project_root: Any = get_project_root()
    work_dir: Any = project_root
    if cwd:
        work_dir: Any = validate_sandbox(cwd)
    try:
        result: Any = safe_execute(command, cwd=str(work_dir), capture_output=capture_output, text=True, timeout=timeout, check=check)
        return result
    except subprocess.TimeoutExpired as e:
        raise ExecutionTimeoutError(f"Command timed out after {timeout}s: {' '.join(command)}") from e
    except subprocess.CalledProcessError as e:
        raise ExecutionError(f"Command failed with exit code {e.returncode}: {' '.join(command)}") from e

def execute_command(args: ExecuteCommandArgs) -> Tuple[int, str, str]:
    """
    Execute a shell command with sandbox validation and timeout protection.

    Args:
        args: ExecuteCommandArgs with command, args, and options

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        ExecutionTimeoutError: If command exceeds timeout
        ExecutionError: If command is not allowed
    """
    full_command: Any = [args.command] + args.args
    try:
        result: Any = execute_with_timeout(command=full_command, timeout=args.timeout, cwd=args.cwd, capture_output=args.capture_output, check=False)
        return (result.returncode, result.stdout if result.stdout else '', result.stderr if result.stderr else '')
    except ExecutionTimeoutError:
        raise
    except Exception as e:
        raise ExecutionError(f'Command execution failed: {e}') from e

def check_tool_installed(tool_name: str) -> bool:
    """
    Check if a tool is installed and available.

    Args:
        tool_name: Name of the tool to check

    Returns:
        True if tool is installed, False otherwise
    """
    if tool_name not in ALLOWED_COMMANDS:
        return False
    for command in ALLOWED_COMMANDS[tool_name]:
        try:
            result: Any = safe_execute([command, '--version'], capture_output=True, timeout=5, check=False)
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return False

def run_linter(tool: str, target_path: str='.', extra_args: Optional[List[str]]=None) -> Tuple[bool, str]:
    """
    Run a linter tool on the codebase.
    Args:
        tool: Linter tool name ('isort', 'autoflake', 'black', 'flake8', 'mypy')
        target_path: Path to lint (relative to project root)
        extra_args: Additional arguments for the linter

    Returns:
        Tuple of (success, output)
    """
    if not check_tool_installed(tool):
        return (False, f'{tool} is not installed')
    command: Any = ALLOWED_COMMANDS.get(tool, [tool])[0]
    args: Any = [command]
    if extra_args:
        args.extend(extra_args)
    args.append(target_path)
    try:
        result: Any = execute_with_timeout(command=args, timeout=120, capture_output=True, check=False)
        success: Any = result.returncode == 0
        output: Any = result.stdout if result.stdout else result.stderr
        return (success, output)
    except Exception as e:
        return (False, str(e))

def run_autofix_tools(target_path: str='.') -> Dict[str, bool]:
    """
    Run auto-fix tools (isort, autoflake) on the codebase.

    Args:
        target_path: Path to fix (relative to project root)

    Returns:
        Dictionary of tool results
    """
    results: Any = {}
    if check_tool_installed('autoflake'):
        success, _ = run_linter('autoflake', target_path, ['--in-place', '--remove-unused-variables', '--remove-all-unused-imports'])
        results['autoflake'] = success
    if check_tool_installed('isort'):
        success, _ = run_linter('isort', target_path, ['--skip', '.venv', '--skip', 'venv'])
        results['isort'] = success
    return results
