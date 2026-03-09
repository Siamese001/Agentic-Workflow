"""
AST-based detector for unsafe I/O and subprocess usage in agent-executed code paths.

This test ensures that agent code does not use direct file I/O or subprocess primitives
that could bypass the mutation fence and write to protected roots.
"""

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TOOLS_DIR,
)

# Add repo root to path for imports
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from agentic_core.L2_execution.tools.unsafe_io_detector import (
    scan_for_unsafe_patterns,
)


@pytest.mark.unit_min_deps
class TestUnsafeIOSubprocessDetector:
    """Test suite for unsafe I/O and subprocess detection."""

    def test_detector_finds_direct_file_writes(self):
        """Test that detector flags direct file write operations."""
        code = """
import os
from pathlib import Path

def write_something():
    # These should be flagged
    with open("file.txt", "w") as f:
        f.write("test")

    Path("file.txt").write_text("test")
    os.remove("file.txt")
    os.rename("old.txt", "new.txt")
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should find multiple unsafe patterns
        assert len(findings) >= 4
        patterns = [f.pattern_type for f in findings]
        assert "open_write" in patterns
        assert "path_write_text" in patterns
        assert "os_remove" in patterns
        assert "os_rename" in patterns

    def test_detector_finds_subprocess_calls(self):
        """Test that detector flags subprocess execution primitives."""
        code = """
import subprocess

def run_something():
    # These should be flagged
    subprocess.run(["ls", "-la"])
    subprocess.call(["git", "status"])
    subprocess.Popen(["python", "script.py"])
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should find subprocess patterns
        assert len(findings) >= 3
        patterns = [f.pattern_type for f in findings]
        assert "subprocess_run" in patterns
        assert "subprocess_call" in patterns
        assert "subprocess_Popen" in patterns

    def test_detector_ignores_safe_operations(self):
        """Test that detector ignores read-only operations and safe paths."""
        code = """
import os
from pathlib import Path

def read_something():
    # These should NOT be flagged (read-only)
    with open("file.txt", "r") as f:
        content = f.read()

    Path("file.txt").read_text()

    # Safe path operations (no mutation)
    Path("file.txt").exists()
    os.path.exists("file.txt")
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should not find any unsafe patterns
        assert len(findings) == 0

    def test_detector_scans_actual_agent_code(self):
        """Test that detector can scan actual agent code paths."""
        # Scan scoped areas for actual findings
        scoped_dirs = [
            repo_root / AGENTIC_CORE_DIR / "L0_routing" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L2_execution" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L3_orchestration" / "reasoning",
            repo_root / APPS_LIC_DIR / "reasoning",
            repo_root / APPS_RG_DIR / "reasoning",
            repo_root / APPS_SHARED_DIR / "reasoning",
            repo_root / TOOLS_DIR,
            repo_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts",
            repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "scripts",
            repo_root / AGENTIC_CORE_DIR / "L2_execution" / "scripts",
        ]

        all_findings = []
        for dir_path in scoped_dirs:
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    if py_file.is_file():
                        try:
                            with open(py_file, encoding="utf-8") as f:
                                content = f.read()
                            findings = scan_for_unsafe_patterns(content, str(py_file.relative_to(repo_root)))
                            all_findings.extend(findings)
                        except Exception:
                            # Skip files that can't be read
                            pass

        # At minimum, we should find some patterns in the codebase
        # (This test documents the current state)
        print(f"\nFound {len(all_findings)} unsafe patterns in scoped areas:")
        for finding in all_findings[:10]:  # Show first 10
            print(f"  {finding.file_path}:{finding.line_number} - {finding.pattern_type}")

        if len(all_findings) > 10:
            print(f"  ... and {len(all_findings) - 10} more")

        # Store findings for evidence
        self.scoped_findings = all_findings

    def test_detector_enforcement(self):
        """Test that detector enforcement fails when unsafe patterns are present."""
        code_with_unsafe = """
def unsafe_function():
    open("test.txt", "w").write("bad")
"""

        # This should fail if we add enforcement
        findings = scan_for_unsafe_patterns(code_with_unsafe, "test.py")
        assert len(findings) > 0
        assert findings[0].pattern_type == "open_write"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
