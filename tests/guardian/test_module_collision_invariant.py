"""
Architectural invariant test for module collision guard.
"""

import subprocess
import sys
from pathlib import Path


class TestModuleCollisionInvariant:
    """Ensure module collision guard maintains architectural integrity."""

    def test_guard_passes_in_default_mode(self):
        """Guard must pass in default mode (no env var)."""
        result = subprocess.run(
            [sys.executable, "tools/architectural/module_collision_guard.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Module collision guard failed:\n{result.stdout}\n{result.stderr}"

    def test_baseline_file_exists(self):
        """Baseline file must exist."""
        baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
        assert baseline_path.exists(), "Baseline file not found"

    def test_baseline_file_is_tracked(self):
        """Baseline file must be tracked in git."""
        result = subprocess.run(
            ["git", "ls-files", "artifacts/architecture/module_collision_baseline.json"],
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "artifacts/architecture/module_collision_baseline.json", (
            "Baseline file not tracked in git"
        )
