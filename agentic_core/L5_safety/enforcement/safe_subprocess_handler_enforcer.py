"""
Safe Subprocess Wrapper - Secure Process Execution.

Landmine #8 & #9 Prevention: Environment Corruption and Zombie Processes.

This module provides safe_run(), a secure wrapper around subprocess.Popen that:
1. Validates commands against the security firewall
2. Registers spawned PIDs for lifecycle tracking
3. Sanitizes captured output to prevent token overload

OPERATIONAL SAFETY (Feb 2026):
- All subprocess calls should go through safe_run()
- Automatic PID registration ensures cleanup on exit
- Output sanitization prevents context pollution
"""

import logging
import subprocess
from typing import Any

from agentic_core.L4_state.utils.telemetry_sanitizer_util import sanitize_tool_output
from agentic_core.L5_safety.enforcement.process_guardrail import ProcessGuard

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


def safe_run(
    command: list[str],
    *,
    capture_output: bool = True,
    text: bool = True,
    timeout: float | None = 60.0,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    sanitize_output: bool = True,
    max_output_chars: int = 2000,
    check: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess | subprocess.Popen:
    """
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
    """
    guard = ProcessGuard.get_instance()

    # Step 1: Validate command against firewall
    guard.validate_command(command)

    logger.debug(f"safe_run: Executing command: {command}")

    # Step 2: Run the command
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=text,
            timeout=timeout,
            cwd=cwd,
            env=env,
            check=check,
            **kwargs,
        )

        # Step 3: Sanitize output if requested
        if sanitize_output and capture_output:
            if result.stdout:
                result.stdout = sanitize_tool_output(result.stdout, max_chars=max_output_chars)
            if result.stderr:
                result.stderr = sanitize_tool_output(result.stderr, max_chars=max_output_chars)

        logger.debug(f"safe_run: Command completed with return code {result.returncode}")
        return result

    except subprocess.TimeoutExpired:
        logger.warning(f"safe_run: Command timed out after {timeout}s: {command}")
        raise


def safe_popen(
    command: list[str],
    *,
    stdout: int | None = subprocess.PIPE,
    stderr: int | None = subprocess.PIPE,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    **kwargs: Any,
) -> subprocess.Popen:
    """
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
    """
    guard = ProcessGuard.get_instance()

    # Step 1: Validate command against firewall
    guard.validate_command(command)

    logger.debug(f"safe_popen: Spawning command: {command}")

    # Step 2: Spawn the process
    process = subprocess.Popen(
        command,
        stdout=stdout,
        stderr=stderr,
        cwd=cwd,
        env=env,
        **kwargs,
    )

    # Step 3: Register PID for lifecycle tracking
    guard.register_pid(process.pid)

    logger.debug(f"safe_popen: Spawned PID {process.pid}")

    return process


def safe_communicate(
    process: subprocess.Popen,
    input_data: str | bytes | None = None,
    timeout: float | None = 60.0,
    sanitize_output: bool = True,
    max_output_chars: int = 2000,
) -> tuple[str | bytes | None, str | bytes | None]:
    """
    Safely communicate with a Popen process and unregister on completion.

    Args:
        process: The Popen process to communicate with.
        input_data: Data to send to stdin.
        timeout: Timeout in seconds.
        sanitize_output: Whether to sanitize output.
        max_output_chars: Max chars for sanitized output.

    Returns:
        Tuple of (stdout, stderr).
    """
    guard = ProcessGuard.get_instance()

    try:
        stdout, stderr = process.communicate(input=input_data, timeout=timeout)

        # Sanitize output if requested
        if sanitize_output:
            if stdout and isinstance(stdout, str):
                stdout = sanitize_tool_output(stdout, max_chars=max_output_chars)
            if stderr and isinstance(stderr, str):
                stderr = sanitize_tool_output(stderr, max_chars=max_output_chars)

        return stdout, stderr

    finally:
        # Unregister PID since process has completed
        guard.unregister_pid(process.pid)


__all__ = ["safe_run", "safe_popen", "safe_communicate"]
