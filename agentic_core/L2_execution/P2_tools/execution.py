"""
Secure Subprocess Execution - Timeout-Protected Command Execution
Prevents livelocks and provides safe subprocess management.
"""
from typing import Any, Optional, Protocol, Dict, List


import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from agentic_core.L2_execution.P2_tools.definitions import ExecuteCommandArgs
from agentic_core.L2_execution.P2_tools.filesystem import get_project_root, validate_sandbox


class ExecutionTimeoutError(Exception):
    """Raised when command execution exceeds timeout."""


class ExecutionError(Exception):
    """Raised when command execution fails."""


ALLOWED_COMMANDS: Dict[str, List[str]] = {
    'python': [sys.executable, 'python', 'python3'],
    'isort': ['isort'],
    'autoflake': ['autoflake'],
    'black': ['black'],
    'flake8': ['flake8'],
    'mypy': ['mypy'],
    'pytest': ['pytest'],
    'pip': ['pip', 'pip3'],
}


DANGEROUS_COMMANDS: List[str] = [
    'rm',
    'del',
    'rmdir',
    'format',
    'dd',
    'mkfs',
    'fdisk',
    'shutdown',
    'reboot',
    'halt',
    'poweroff',
    'init',
]


def is_command_allowed(command: str) -> bool:
    """
    Check if a command is allowed to execute.
    
    Args:
        command: Command to check
        
    Returns:
        True if command is allowed, False otherwise
    """
    command_lower = command.lower()
    
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command_lower:
            return False
    
    command_name = Path(command).stem.lower()
    
    for allowed_list in ALLOWED_COMMANDS.values():
        for allowed in allowed_list:
            if command_name == Path(allowed).stem.lower():
                return True
    
    return False


def execute_with_timeout(
    command: List[str],
    timeout: int = 30,
    cwd: Optional[str] = None,
    capture_output: bool = True,
    check: bool = False
) -> subprocess.CompletedProcess:
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
        raise ValueError("Timeout cannot exceed 300 seconds")
    
    if not command or not command[0]:
        raise ValueError("Command cannot be empty")
    
    if not is_command_allowed(command[0]):
        raise ExecutionError(f"Command not allowed: {command[0]}")
    
    project_root = get_project_root()
    work_dir = project_root
    
    if cwd:
        work_dir = validate_sandbox(cwd)
    
    try:
        result = subprocess.run(
            command,
            cwd=str(work_dir),
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=check
        )
        return result
    except subprocess.TimeoutExpired as e:
        raise ExecutionTimeoutError(
            f"Command timed out after {timeout}s: {' '.join(command)}"
        ) from e
    except subprocess.CalledProcessError as e:
        raise ExecutionError(
            f"Command failed with exit code {e.returncode}: {' '.join(command)}"
        ) from e


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
    full_command = [args.command] + args.args
    
    try:
        result = execute_with_timeout(
            command=full_command,
            timeout=args.timeout,
            cwd=args.cwd,
            capture_output=args.capture_output,
            check=False
        )
        
        return (
            result.returncode,
            result.stdout if result.stdout else "",
            result.stderr if result.stderr else ""
        )
    except ExecutionTimeoutError:
        raise
    except Exception as e:
        raise ExecutionError(f"Command execution failed: {e}") from e


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
            result = subprocess.run(
                [command, '--version'],
                capture_output=True,
                timeout=5,
                check=False
            )
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return False


def run_linter(
    tool: str,
    target_path: str = ".",
    extra_args: Optional[List[str]] = None
) -> Tuple[bool, str]:
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
        return False, f"{tool} is not installed"
    
    command = ALLOWED_COMMANDS.get(tool, [tool])[0]
    args = [command]
    
    if extra_args:
        args.extend(extra_args)
    
    args.append(target_path)
    
    try:
        result = execute_with_timeout(
            command=args,
            timeout=120,
            capture_output=True,
            check=False
        )
        
        success = result.returncode == 0
        output = result.stdout if result.stdout else result.stderr
        
        return success, output
    except Exception as e:
        return False, str(e)


def run_autofix_tools(target_path: str = ".") -> Dict[str, bool]:
    """
    Run auto-fix tools (isort, autoflake) on the codebase.
    
    Args:
        target_path: Path to fix (relative to project root)
        
    Returns:
        Dictionary of tool results
    """
    results = {}
    
    if check_tool_installed('autoflake'):
        success, _ = run_linter(
            'autoflake',
            target_path,
            ['--in-place', '--remove-unused-variables', '--remove-all-unused-imports']
        )
        results['autoflake'] = success
    
    if check_tool_installed('isort'):
        success, _ = run_linter(
            'isort',
            target_path,
            ['--skip', '.venv', '--skip', 'venv']
        )
        results['isort'] = success
    
    return results