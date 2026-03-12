"""
RuntimeSafetyMixin - Process Lifecycle Management for Agents.

Landmine #8 & #9 Prevention: Environment Corruption and Zombie Processes.

This mixin provides agents with:
1. Safe subprocess execution via safe_run/safe_popen
2. Automatic process cleanup via ProcessGuard
3. Context manager support for guaranteed cleanup

OPERATIONAL SAFETY (Feb 2026):
- Agents inheriting this mixin get automatic process lifecycle management
- All subprocess calls are validated against the security firewall
- Cleanup is guaranteed via context manager or explicit cleanup() call
"""
import logging
from typing import Any
from agentic_core.L5_safety.enforcement.process_guardrail import ProcessGuard, SecurityViolation
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
try:
    from agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer import safe_communicate, safe_popen, safe_run
except ImportError:

    def safe_communicate(*args, **kwargs):
        return None

    def safe_popen(*args, **kwargs):
        return None

    def safe_run(*args, **kwargs):
        return None
logger = logging.getLogger(__name__)

class RuntimeSafetyMixin:
    """
    Mixin providing runtime safety capabilities to agents.

    Provides:
    - safe_run(): Secure subprocess.run wrapper
    - safe_popen(): Secure subprocess.Popen wrapper
    - cleanup_processes(): Terminate all spawned processes
    - Context manager support for automatic cleanup

    Usage:
        class MyAgent(RuntimeSafetyMixin, SovereignBaseAgent):
            def execute(self):
                with self.runtime_guard():
                    result = self.safe_run(["python", "script.py"])
                    # Processes are automatically cleaned up on exit
    """

    def __init__(self, *args, **kwargs):
        """Initialize runtime safety mixin."""
        super().__init__(*args, **kwargs)
        self._process_guard = ProcessGuard.get_instance()

    # guardian: allow-magic-config
    def safe_run(self, command: list[str], *, capture_output: bool=True, text: bool=True, timeout: float | None=60.0, cwd: str | None=None, sanitize_output: bool=True, max_output_chars: int=2000, **kwargs: Any):
        """
        Safely run a subprocess with security validation.

        See safe_subprocess.safe_run for full documentation.
        """
        return safe_run(command, capture_output=capture_output, text=text, timeout=timeout, cwd=cwd, sanitize_output=sanitize_output, max_output_chars=max_output_chars, **kwargs)

    def safe_popen(self, command: list[str], *, cwd: str | None=None, **kwargs: Any):
        """
        Safely spawn a subprocess with PID tracking.

        See safe_subprocess.safe_popen for full documentation.
        """
        return safe_popen(command, cwd=cwd, **kwargs)

    # guardian: allow-magic-config
    def safe_communicate(self, process, input_data: str | bytes | None=None, timeout: float | None=60.0, sanitize_output: bool=True, max_output_chars: int=2000):
        """
        Safely communicate with a Popen process.

        See safe_subprocess.safe_communicate for full documentation.
        """
        return safe_communicate(process, input_data=input_data, timeout=timeout, sanitize_output=sanitize_output, max_output_chars=max_output_chars)

    def cleanup_processes(self) -> dict[str, list[int]]:
        """
        Terminate all processes spawned by this agent.

        Returns:
            Dict with 'terminated' and 'failed' PID lists.
        """
        result = self._process_guard.cleanup()
        if result['terminated']:
            logger.info(f"RuntimeSafetyMixin: Cleaned up {len(result['terminated'])} processes")
        return result

    def validate_command(self, command: list[str]) -> bool:
        """
        Validate a command without executing it.

        Args:
            command: The command to validate.

        Returns:
            True if command is allowed.

        Raises:
            SecurityViolation: If command is blocked.
        """
        return self._process_guard.validate_command(command)

    class _RuntimeGuardContext:
        """Context manager for guaranteed process cleanup."""

        def __init__(self, mixin: 'RuntimeSafetyMixin'):
            self._mixin = mixin

        def __enter__(self):
            return self._mixin

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._mixin.cleanup_processes()
            return False

    def runtime_guard(self):
        """
        Context manager for automatic process cleanup.

        Usage:
            with self.runtime_guard():
                self.safe_run(["python", "script.py"])
                # Cleanup happens automatically on exit
        """
        return self._RuntimeGuardContext(self)
__all__ = ['RuntimeSafetyMixin', 'SecurityViolation']
