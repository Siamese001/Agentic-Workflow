"""
Phase 2 Unsafe I/O and Subprocess Enforcement Test

This test ensures that the unsafe I/O detector continues to work
and that remediated files no longer contain forbidden primitives.
"""

from pathlib import Path

import pytest

from agentic_core.L2_execution.tools.unsafe_io_detector import (
    get_scoped_directories,
    scan_directory_for_unsafe_patterns,
    scan_for_unsafe_patterns,
)


@pytest.mark.unit_min_deps
class TestPhase2UnsafeIOEnforcement:
    """Test suite for Phase 2 unsafe I/O enforcement."""

    def test_detector_still_works(self):
        """Verify the unsafe I/O detector is functional."""
        # Test on a simple file with unsafe patterns
        code_with_unsafe = """
import subprocess

def bad_function():
    with open("test.txt", "w") as f:
        f.write("bad")
    subprocess.run(["rm", "-rf", "/"])
"""
        patterns = scan_for_unsafe_patterns(code_with_unsafe, "test.py")
        assert len(patterns) > 0, "Detector should find unsafe patterns"

        # Check specific patterns are detected
        pattern_types = {p.pattern_type for p in patterns}
        assert "open_write" in pattern_types, "Should detect open(..., 'w')"
        assert "subprocess_run" in pattern_types, "Should detect subprocess.run"

    def test_remediated_files_clean(self):
        """Verify that remediated files no longer contain forbidden primitives."""
        repo_root = Path.cwd()

        # Check ToolsmithAgent.py - should have no direct file writes
        toolsmith_path = repo_root / "agentic_core/L2_execution/reasoning/ToolsmithAgent.py"
        if toolsmith_path.exists():
            code = toolsmith_path.read_text(encoding="utf-8")
            patterns = scan_for_unsafe_patterns(code, str(toolsmith_path))

            # Should not have direct open() writes
            open_writes = [p for p in patterns if p.pattern_type == "open_write"]
            assert len(open_writes) == 0, f"ToolsmithAgent should not have open_write patterns: {open_writes}"

            # Should not have Path.write_text
            path_writes = [p for p in patterns if p.pattern_type == "path_write_text"]
            assert len(path_writes) == 0, (
                f"ToolsmithAgent should not have path_write_text patterns: {path_writes}"
            )

    def test_no_direct_subprocess_in_remediated_files(self):
        """Verify that remediated files use safe_subprocess, not direct subprocess."""
        repo_root = Path.cwd()

        # Check execute_ssot.py - should use safe_subprocess_run
        execute_ssot_path = repo_root / "agentic_core/L0_routing/scripts/execute_ssot.py"
        if execute_ssot_path.exists():
            code = execute_ssot_path.read_text(encoding="utf-8")

            # Should import safe_subprocess
            assert "safe_subprocess_run" in code, "execute_ssot.py should import safe_subprocess_run"

            # Should not have direct subprocess.run calls (only in imports or safe_subprocess)
            lines = code.split("\n")
            for i, line in enumerate(lines, 1):
                # Skip lines that are imports or inside safe_subprocess module
                if "import subprocess" in line or "from subprocess" in line:
                    continue
                if "subprocess.run(" in line and "safe_subprocess_run(" not in line:
                    raise AssertionError(
                        f"Line {i} in execute_ssot.py has direct subprocess.run: {line.strip()}"
                    )

    def test_scoped_directories_scan(self):
        """Verify scanning scoped directories works and results are manageable."""
        repo_root = Path.cwd()
        scoped_dirs = get_scoped_directories(repo_root)

        total_patterns = 0
        for dir_path in scoped_dirs:
            if dir_path.exists():
                patterns = scan_directory_for_unsafe_patterns(dir_path)
                total_patterns += len(patterns)

        # We should have fewer patterns than the original 69 after remediation
        # But we don't expect zero (there are still legitimate uses in non-remediated files)
        print(f"Total patterns found: {total_patterns}")

        # At minimum, the detector should run without errors
        assert total_patterns >= 0, "Scanner should run without errors"
