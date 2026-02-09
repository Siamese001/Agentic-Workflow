"""Regression test: dependency_verify_imports.py must exit 1 when blocking > 0."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

VERIFIER = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "reports"
    / "plans"
    / "dependency_verify_imports.py"
)


class TestDependencyVerifierExitCode:
    def test_verifier_exists(self):
        assert VERIFIER.exists(), f"Verifier not found at {VERIFIER}"

    def test_exit_1_on_blocking_failures(self):
        """When run without all deps installed, blocking failures must produce exit code 1."""
        result = subprocess.run(
            [sys.executable, str(VERIFIER)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        stdout = result.stdout
        if "RESULT: FAIL" in stdout:
            assert result.returncode == 1, (
                f"Verifier printed FAIL but exited {result.returncode}; "
                f"blocking failures MUST produce exit code 1"
            )
        elif "RESULT: PASS" in stdout:
            assert result.returncode == 0, (
                f"Verifier printed PASS but exited {result.returncode}; passing run MUST produce exit code 0"
            )
        else:
            pytest.fail(f"Verifier produced unexpected output (no RESULT line):\n{stdout[-500:]}")

    def test_exit_0_on_pass_when_all_core_installed(self):
        """When all core deps are installed, verifier must exit 0."""
        result = subprocess.run(
            [sys.executable, str(VERIFIER)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        stdout = result.stdout
        if "RESULT: PASS" in stdout:
            assert result.returncode == 0
        else:
            pytest.skip("Core deps not fully installed in this environment; cannot test PASS path")
