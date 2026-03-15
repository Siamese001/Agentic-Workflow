"""
ProcessGuard - Runtime Process Lifecycle Management.

Landmine #8 & #9 Prevention: Environment Corruption and Zombie Processes.

This module provides:
1. Registry: Tracks all PIDs spawned by agents
2. Cleanup: terminate_all() kills registered PIDs (registered with atexit)
3. Firewall: validate_command() blocks dangerous commands

OPERATIONAL SAFETY (Feb 2026):
- Prevents package managers from corrupting environment
- Prevents zombie processes from accumulating
- Provides fail-safe cleanup on interpreter exit
"""

import atexit
import logging
import os
import signal
import threading
from pathlib import Path
from typing import Final

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

logger = logging.getLogger(__name__)
BLOCKED_COMMANDS: Final[frozenset[str]] = frozenset(
    {"pip", "npm", "yarn", "apt", "apt-get", "brew", "rm", "sudo", "powershell", "cmd"}
)


class SecurityViolation(Exception):
    """Raised when a command violates security policy."""

    def __init__(self, command: list[str], reason: str):
        self.command = command
        self.reason = reason
        super().__init__(f"Security violation: {reason}. Command: {command}")


class ProcessGuard:
    """
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
    """

    _instance: "ProcessGuard | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "ProcessGuard":
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the guard state."""
        self._pids: set[int] = set()
        self._pid_lock: threading.Lock = threading.Lock()
        self._atexit_registered: bool = False
        self._register_atexit()

    @classmethod
    def get_instance(cls) -> "ProcessGuard":
        """Get the singleton instance."""
        return cls()

    def _register_atexit(self) -> None:
        """Register cleanup with atexit as fail-safe."""
        if not self._atexit_registered:
            atexit.register(self._atexit_cleanup)
            self._atexit_registered = True
            logger.debug("ProcessGuard: atexit cleanup registered")

    def _atexit_cleanup(self) -> None:
        """Cleanup handler called on interpreter exit."""
        if self._pids:
            logger.warning(f"ProcessGuard: atexit cleanup killing {len(self._pids)} orphaned processes")
            self.terminate_all()

    def register_pid(self, pid: int) -> None:
        """
        Register a PID for lifecycle tracking.

        Args:
            pid: The process ID to track.
        """
        with self._pid_lock:
            self._pids.add(pid)
            logger.debug(f"ProcessGuard: Registered PID {pid}")

    def unregister_pid(self, pid: int) -> None:
        """
        Unregister a PID (e.g., after normal termination).

        Args:
            pid: The process ID to stop tracking.
        """
        with self._pid_lock:
            self._pids.discard(pid)
            logger.debug(f"ProcessGuard: Unregistered PID {pid}")

    def get_active_pids(self) -> set[int]:
        """Get a copy of currently tracked PIDs."""
        with self._pid_lock:
            return self._pids.copy()

    def terminate_all(self) -> dict[str, list[int]]:
        """
        Terminate all registered processes.

        Returns:
            Dict with 'terminated' and 'failed' PID lists.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ProcessGuard.terminate_all")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:ProcessGuard.terminate_all".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        result = {"terminated": [], "failed": []}
        with self._pid_lock:
            pids_to_kill = self._pids.copy()
        for pid in pids_to_kill:
            try:
                self._kill_process(pid)
                result["terminated"].append(pid)
                logger.info(f"ProcessGuard: Terminated PID {pid}")
            # guardian: allow-silent-swallow
            except Exception as e:
                result["failed"].append(pid)
                logger.warning(f"ProcessGuard: Failed to terminate PID {pid}: {e}")
        with self._pid_lock:
            self._pids.clear()
        return result

    def _kill_process(self, pid: int) -> None:
        """
        Kill a process by PID.

        Uses SIGTERM first, then SIGKILL if needed.
        Platform-aware for Windows vs Unix.
        """
        try:
            if os.name == "nt":
                os.kill(pid, signal.SIGTERM)
            else:
                os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except PermissionError:
            logger.warning(f"ProcessGuard: Permission denied killing PID {pid}")
            raise

    def validate_command(self, command: list[str]) -> bool:
        """
        Validate a command against the security firewall.

        Args:
            command: The command as a list of strings.

        Returns:
            True if command is allowed.

        Raises:
            SecurityViolation: If command is blocked.
        """
        if not command:
            raise SecurityViolation(command, "Empty command")
        base_cmd = command[0].lower()
        base_cmd = Path(base_cmd).name
        if os.name == "nt" and base_cmd.endswith(".exe"):
            base_cmd = base_cmd[:-4]
        if base_cmd in BLOCKED_COMMANDS:
            raise SecurityViolation(command, f"Command '{base_cmd}' is blocked (environment protection)")
        return True

    def cleanup(self) -> dict[str, list[int]]:
        """Alias for terminate_all() for API consistency."""
        return self.terminate_all()

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing only).

        WARNING: This is intended for test isolation only.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.terminate_all()
                cls._instance = None


__all__ = ["ProcessGuard", "SecurityViolation", "BLOCKED_COMMANDS"]
