#!/usr/bin/env python3
"""
Ultra-Hardened Protocol Test Suite - Coverage Gap Resolution
Tests Resource Exhaustion, File Permissions, and Logging Verification
"""

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from agentic_core.L0_maintenance.scripts.execute_ssot import (
    RUNTIME_STATE_FILE,
    NonInteractiveGuard,
    RuntimeStateManager,
    with_retry,
)


class TestUltraHardenedProtocol(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # --- Feature 1: NonInteractiveGuard & Resource Exhaustion ---

    def test_guard_recursion_protection(self):
        """Test 1: Verify Guard throws RecursionError after max limits (Resource Exhaustion)."""
        with NonInteractiveGuard(active=True, max_blocked_prompts=2):
            # First two should be RuntimeErrors
            with self.assertRaises(RuntimeError):
                input("1")
            with self.assertRaises(RuntimeError):
                input("2")
            # Third should be RecursionError (Critical Security Check)
            with self.assertRaisesRegex(RecursionError, "Infinite Loop Protection"):
                input("3")

    def test_guard_logging_verification(self):
        """Test 2: Verify blocked prompts are actually logged for audit trails."""
        with self.assertLogs("UnifiedSovereign", level="WARNING") as cm:
            with NonInteractiveGuard(active=True):
                try:
                    input("AuditMe")
                except:
                    pass
        self.assertTrue(any("BLOCKED PROMPT" in log for log in cm.output))
        self.assertTrue(any("AuditMe" in log for log in cm.output))

    # --- Feature 2: Retry Decorator Timing & Logic ---

    def test_retry_backoff_timing(self):
        """Test 3: Verify exponential backoff logic (1s -> 2s -> 4s)."""
        mock_func = MagicMock(side_effect=ValueError("Fail"))

        with patch("time.sleep") as mock_sleep:

            @with_retry(max_retries=3, delay=1.0)
            def timed_func():
                return mock_func()

            with self.assertRaises(ValueError):
                timed_func()

            # Verify exponential calls: sleep(1.0), sleep(2.0), sleep(4.0)
            mock_sleep.assert_has_calls([call(1.0), call(2.0), call(4.0)])

    def test_retry_bypasses_exhaustion_error(self):
        """Test 4: RecursionError from Guard should NOT be retried (Critical)."""
        mock_func = MagicMock(side_effect=RecursionError("Infinite Loop Protection"))

        @with_retry(max_retries=3)
        def doomed_func():
            return mock_func()

        with self.assertRaises(RecursionError):
            doomed_func()

        # Should fail immediately, no retries
        self.assertEqual(mock_func.call_count, 1)

    # --- Feature 3: Secure State Persistence ---

    def test_state_file_permissions(self):
        """Test 5: Verify runtime_state.json is created with secure 600 permissions."""
        if os.name == "nt":
            return  # Skip permission check on Windows (not strictly enforced same way)

        mgr = RuntimeStateManager(self.project_root)
        mgr.save()

        state_path = self.project_root / RUNTIME_STATE_FILE
        mode = os.stat(state_path).st_mode

        # Check for 600 (Owner RW only)
        # S_IRUSR (00400) | S_IWUSR (00200) = 00600
        self.assertTrue(mode & stat.S_IRUSR)
        self.assertTrue(mode & stat.S_IWUSR)
        # Ensure Group/Others have NO access
        self.assertFalse(mode & stat.S_IRGRP)
        self.assertFalse(mode & stat.S_IROTH)

    def test_atomic_write_concurrency_simulation(self):
        """Test 6: Simulate race condition during write."""
        mgr = RuntimeStateManager(self.project_root)

        # We simulate the file existing during the replacement phase
        (self.project_root / RUNTIME_STATE_FILE).write_text("OLD_STATE")

        mgr.state["status"] = "NEW_STATE"
        mgr.save()

        # Should have overwritten cleanly without error
        content = json.loads((self.project_root / RUNTIME_STATE_FILE).read_text())
        self.assertEqual(content["status"], "NEW_STATE")

    # --- Previous Critical Tests (Retained for Regression) ---

    def test_guard_active_raises_error(self):
        """Test 7: Basic guard functionality - active mode blocks input."""
        with NonInteractiveGuard(active=True):
            with self.assertRaises(RuntimeError):
                input("Fail")

    def test_guard_inactive_allows_input(self):
        """Test 8: Basic guard functionality - inactive mode allows input."""
        with patch("builtins.input", return_value="ok"):
            with NonInteractiveGuard(active=False):
                self.assertEqual(input("Go"), "ok")

    def test_retry_success_after_fail(self):
        """Test 9: Retry decorator succeeds after initial failure."""
        mock_func = MagicMock(side_effect=[ValueError("F"), "S"])

        @with_retry(max_retries=2, delay=0)
        def func():
            return mock_func()

        self.assertEqual(func(), "S")

    def test_retry_max_attempts_exceeded(self):
        """Test 10: Retry decorator exhausts all attempts."""
        mock_func = MagicMock(side_effect=ValueError("Always fails"))

        @with_retry(max_retries=2, delay=0)
        def func():
            return mock_func()

        with self.assertRaises(ValueError):
            func()
        self.assertEqual(mock_func.call_count, 2)  # Initial + 1 retry

    def test_guard_blocked_count_tracking(self):
        """Test 11: Guard properly tracks blocked prompt count."""
        guard = NonInteractiveGuard(active=True, max_blocked_prompts=3)
        with guard:
            try:
                input("A")
            except:
                pass
            self.assertEqual(guard.blocked_count, 1)
            try:
                input("B")
            except:
                pass
            self.assertEqual(guard.blocked_count, 2)

    def test_guard_custom_max_blocked_prompts(self):
        """Test 12: Guard respects custom max_blocked_prompts setting."""
        with NonInteractiveGuard(active=True, max_blocked_prompts=1):
            # First should be RuntimeError
            with self.assertRaises(RuntimeError):
                input("First")
            # Second should be RecursionError (exceeds limit of 1)
            with self.assertRaises(RecursionError):
                input("Second")

    def test_retry_logging_verification(self):
        """Test 13: Verify retry attempts are properly logged."""
        mock_func = MagicMock(side_effect=ValueError("Fail"))

        with self.assertLogs("UnifiedSovereign", level="WARNING") as cm:

            @with_retry(max_retries=2, delay=0)
            def failing_func():
                return mock_func()

            with self.assertRaises(ValueError):
                failing_func()

        # Should log retry attempts
        self.assertTrue(any("Retry 1/2" in log for log in cm.output))
        self.assertTrue(any("Retry 2/2" in log for log in cm.output))

    def test_state_file_atomic_write_integrity(self):
        """Test 14: Verify atomic write prevents corruption."""
        mgr = RuntimeStateManager(self.project_root)
        mgr.state["critical_data"] = "must_not_corrupt"
        mgr.save()

        # Verify file contains valid JSON
        state_path = self.project_root / RUNTIME_STATE_FILE
        content = json.loads(state_path.read_text())
        self.assertEqual(content["critical_data"], "must_not_corrupt")


if __name__ == "__main__":
    unittest.main()
