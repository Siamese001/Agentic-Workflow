"""H1 governance tests: PreventativeSandbox full-spectrum patching.

Validates:
- Write vectors blocked during sandbox activation
- Originals restored after context exit
- Double-activation prevented (idempotent guard)
- SandboxViolationError raised with function name
- Custom target registration
"""

import os
import subprocess

import pytest

from agentic_core.L2_execution.enforcement.preventative_sandbox import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    PreventativeSandbox,
    SandboxViolationError,
)

pytestmark = pytest.mark.governance


class TestSandboxBlocking:
    """Write vectors must raise SandboxViolationError when active."""

    def test_os_remove_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                os.remove("nonexistent.txt")
            assert "os.remove" in str(exc.value)

    def test_subprocess_run_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                subprocess.run(["echo", "test"])
            assert "subprocess.run" in str(exc.value)

    def test_os_system_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                os.system("echo test")
            assert "os.system" in str(exc.value)

    def test_builtins_open_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                open("nonexistent.txt", "w")  # noqa: SIM115
            assert "builtins.open" in str(exc.value)


class TestSandboxRestoration:
    """Originals must be restored after context exit."""

    def test_os_remove_restored(self):
        original = os.remove
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            assert os.remove is not original
        assert os.remove is original

    def test_subprocess_run_restored(self):
        original = subprocess.run
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            assert subprocess.run is not original
        assert subprocess.run is original

    def test_restored_on_exception(self):
        original = os.remove
        sandbox = PreventativeSandbox()
        with pytest.raises(ValueError, match="test error"):
            with sandbox.activated():
                raise ValueError("test error")
        assert os.remove is original


class TestDoubleActivation:
    """Double activation must be prevented."""

    def test_double_activation_raises(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(RuntimeError, match="already active"):
                with sandbox.activated():
                    pass


class TestCustomTargets:
    """Custom write vectors can be registered."""

    def test_custom_target_blocked(self):
        sandbox = PreventativeSandbox()
        sandbox.register_target("os.path", "exists", "custom")
        original = os.path.exists
        with sandbox.activated():
            with pytest.raises(SandboxViolationError):
                os.path.exists("test")
        assert os.path.exists is original


class TestSandboxState:
    """Sandbox state tracking."""

    def test_inactive_by_default(self):
        sandbox = PreventativeSandbox()
        assert sandbox.is_active is False

    def test_active_inside_context(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            assert sandbox.is_active is True
        assert sandbox.is_active is False
