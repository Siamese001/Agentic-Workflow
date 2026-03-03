"""
Unit tests for ProcessGuard - Runtime Process Lifecycle Management.

Tests cover:
1. Suicide Prevention: Blocked commands raise SecurityViolation
2. Zombie Hunter: Spawned processes are tracked and terminated
3. Singleton behavior
4. Command validation firewall
"""

import os
import subprocess
import time

import pytest

# from agentic_core.L5_safety.enforcement.safe_subprocess import safe_popen, safe_run  # TODO: Fix import
from agentic_core.L5_safety.enforcement.process_guard import (
    BLOCKED_COMMANDS,
    ProcessGuard,
    SecurityViolation,
)


class TestProcessGuardSingleton:
    """Test singleton behavior of ProcessGuard."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProcessGuard.reset_instance()

    def teardown_method(self):
        """Cleanup after each test."""
        ProcessGuard.reset_instance()

    def test_singleton_returns_same_instance(self):
        """ProcessGuard should return the same instance."""
        guard1 = ProcessGuard.get_instance()
        guard2 = ProcessGuard.get_instance()
        assert guard1 is guard2

    def test_singleton_via_constructor(self):
        """Direct construction should also return singleton."""
        guard1 = ProcessGuard()
        guard2 = ProcessGuard()
        assert guard1 is guard2


class TestCommandValidation:
    """Test command validation firewall."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProcessGuard.reset_instance()

    def teardown_method(self):
        """Cleanup after each test."""
        ProcessGuard.reset_instance()

    def test_valid_command_passes(self):
        """Valid commands should pass validation."""
        guard = ProcessGuard.get_instance()
        assert guard.validate_command(["python", "--version"]) is True
        assert guard.validate_command(["echo", "hello"]) is True
        assert guard.validate_command(["git", "status"]) is True

    @pytest.mark.parametrize("blocked_cmd", list(BLOCKED_COMMANDS))
    def test_blocked_commands_raise_security_violation(self, blocked_cmd):
        """All blocked commands should raise SecurityViolation."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation) as exc_info:
            guard.validate_command([blocked_cmd, "some", "args"])
        assert blocked_cmd in str(exc_info.value)
        assert "blocked" in str(exc_info.value).lower()

    def test_pip_install_blocked(self):
        """Scenario 1: pip install should be blocked (Suicide Prevention)."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation) as exc_info:
            guard.validate_command(["pip", "install", "malware"])
        assert exc_info.value.command == ["pip", "install", "malware"]
        assert "pip" in exc_info.value.reason

    def test_npm_install_blocked(self):
        """npm install should be blocked."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation):
            guard.validate_command(["npm", "install", "malware"])

    def test_rm_blocked(self):
        """rm command should be blocked."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation):
            guard.validate_command(["rm", "-rf", "/"])

    def test_sudo_blocked(self):
        """sudo command should be blocked."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation):
            guard.validate_command(["sudo", "anything"])

    def test_empty_command_raises(self):
        """Empty command should raise SecurityViolation."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation) as exc_info:
            guard.validate_command([])
        assert "Empty command" in str(exc_info.value)

    def test_path_stripped_from_command(self):
        """Commands with full paths should still be blocked."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation):
            guard.validate_command(["/usr/bin/pip", "install", "pkg"])

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_exe_extension_stripped_on_windows(self):
        """Commands with .exe extension should still be blocked on Windows."""
        guard = ProcessGuard.get_instance()
        with pytest.raises(SecurityViolation):
            guard.validate_command(["pip.exe", "install", "pkg"])

    def test_subprocess_list_args_are_safe(self):
        """
        Arguments with shell metacharacters are safe when using subprocess with list args.

        When subprocess is called with a list (not shell=True), arguments are passed
        directly to the executable without shell interpretation. This means shell
        metacharacters are treated as literal strings.
        """
        guard = ProcessGuard.get_instance()
        # These contain shell metacharacters but are safe with subprocess list args
        safe_commands = [
            ["python", "-c", "print('hello')"],
            ["python", "-c", "import time; time.sleep(1)"],
            ["python", "-c", "x = (1, 2, 3)"],
            ["python", "-c", "print('$HOME')"],
            ["echo", "arg; something"],  # semicolon is literal
            ["echo", "arg | something"],  # pipe is literal
        ]
        for cmd in safe_commands:
            assert guard.validate_command(cmd) is True


class TestPIDRegistry:
    """Test PID registration and tracking."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProcessGuard.reset_instance()

    def teardown_method(self):
        """Cleanup after each test."""
        ProcessGuard.reset_instance()

    def test_register_and_get_pids(self):
        """PIDs should be registered and retrievable."""
        guard = ProcessGuard.get_instance()
        guard.register_pid(1234)
        guard.register_pid(5678)
        pids = guard.get_active_pids()
        assert 1234 in pids
        assert 5678 in pids

    def test_unregister_pid(self):
        """PIDs should be unregisterable."""
        guard = ProcessGuard.get_instance()
        guard.register_pid(1234)
        guard.unregister_pid(1234)
        pids = guard.get_active_pids()
        assert 1234 not in pids

    def test_unregister_nonexistent_pid_is_safe(self):
        """Unregistering a non-existent PID should not raise."""
        guard = ProcessGuard.get_instance()
        guard.unregister_pid(99999)  # Should not raise


class TestZombieHunter:
    """Test process termination (Zombie Hunter)."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProcessGuard.reset_instance()

    def teardown_method(self):
        """Cleanup after each test."""
        ProcessGuard.reset_instance()

    @pytest.mark.skipif(os.name == "nt", reason="Unix sleep command")
    def test_terminate_all_kills_processes_unix(self):
        """Scenario 2: Spawned processes should be terminated (Unix)."""
        guard = ProcessGuard.get_instance()

        # Start a sleep process
        process = subprocess.Popen(["sleep", "60"])
        guard.register_pid(process.pid)

        # Verify process is running
        assert process.poll() is None

        # Terminate all
        result = guard.terminate_all()

        # Give it a moment to die
        time.sleep(0.1)

        # Verify process is dead
        assert process.poll() is not None
        assert process.pid in result["terminated"]

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_terminate_all_kills_processes_windows(self):
        """Scenario 2: Spawned processes should be terminated (Windows)."""
        guard = ProcessGuard.get_instance()

        # Start a timeout process (Windows equivalent of sleep)
        process = subprocess.Popen(
            ["python", "-c", "import time; time.sleep(60)"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        guard.register_pid(process.pid)

        # Verify process is running
        assert process.poll() is None

        # Terminate all
        result = guard.terminate_all()

        # Give it a moment to die
        time.sleep(0.5)

        # Verify process is dead
        assert process.poll() is not None
        assert process.pid in result["terminated"]

    def test_terminate_all_clears_registry(self):
        """terminate_all should clear the PID registry."""
        guard = ProcessGuard.get_instance()
        guard.register_pid(1234)
        guard.register_pid(5678)

        guard.terminate_all()

        assert len(guard.get_active_pids()) == 0

    def test_cleanup_alias(self):
        """cleanup() should be an alias for terminate_all()."""
        guard = ProcessGuard.get_instance()
        guard.register_pid(1234)

        result = guard.cleanup()

        assert "terminated" in result
        assert "failed" in result


class TestSafeRun:
    """Test safe_run subprocess wrapper."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProcessGuard.reset_instance()

    def teardown_method(self):
        """Cleanup after each test."""
        ProcessGuard.reset_instance()

    def test_safe_run_executes_valid_command(self):
        """safe_run should execute valid commands."""
        result = safe_run(["python", "--version"])
        assert result.returncode == 0
        assert "Python" in result.stdout or "Python" in result.stderr

    def test_safe_run_blocks_invalid_command(self):
        """safe_run should block invalid commands."""
        with pytest.raises(SecurityViolation):
            safe_run(["pip", "install", "malware"])

    def test_safe_run_sanitizes_output(self):
        """safe_run should sanitize long output."""
        # Generate output longer than default max
        result = safe_run(
            ["python", "-c", "print('x' * 5000)"],
            max_output_chars=100,
        )
        # Output should be truncated
        assert len(result.stdout) < 5000
        assert "Pruned" in result.stdout or len(result.stdout) <= 100

    def test_safe_run_respects_timeout(self):
        """safe_run should respect timeout."""
        with pytest.raises(subprocess.TimeoutExpired):
            safe_run(
                ["python", "-c", "import time; time.sleep(10)"],
                timeout=0.1,
            )


class TestSafePopen:
    """Test safe_popen subprocess wrapper."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProcessGuard.reset_instance()

    def teardown_method(self):
        """Cleanup after each test."""
        ProcessGuard.reset_instance()

    def test_safe_popen_registers_pid(self):
        """safe_popen should register the spawned PID."""
        guard = ProcessGuard.get_instance()

        process = safe_popen(["python", "-c", "import time; time.sleep(5)"])

        try:
            assert process.pid in guard.get_active_pids()
        finally:
            process.terminate()
            process.wait()

    def test_safe_popen_blocks_invalid_command(self):
        """safe_popen should block invalid commands."""
        with pytest.raises(SecurityViolation):
            safe_popen(["npm", "install", "malware"])


class TestIntegration:
    """Integration tests for the full runtime safety system."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProcessGuard.reset_instance()

    def teardown_method(self):
        """Cleanup after each test."""
        ProcessGuard.reset_instance()

    def test_full_lifecycle(self):
        """Test full process lifecycle: spawn, track, terminate."""
        guard = ProcessGuard.get_instance()

        # Spawn a process
        process = safe_popen(["python", "-c", "import time; time.sleep(30)"])

        # Verify it's tracked
        assert process.pid in guard.get_active_pids()

        # Terminate all
        guard.terminate_all()

        # Wait for termination
        time.sleep(0.5)

        # Verify cleanup
        assert process.poll() is not None
        assert len(guard.get_active_pids()) == 0
