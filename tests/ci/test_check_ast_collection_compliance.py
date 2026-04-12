#!/usr/bin/env python3
"""
Tests for AST Collection Compliance Checker
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ops_scripts.ci.check_ast_collection_compliance import ASTComplianceChecker


def test_check_directory_with_string_path():
    """Test that check_directory accepts string paths."""
    checker = ASTComplianceChecker()

    # Should not raise an exception
    checker.check_directory("tools")
    assert isinstance(checker.violations, list)


def test_check_directory_with_path_object():
    """Test that check_directory accepts Path objects."""
    checker = ASTComplianceChecker()

    # Should not raise an exception
    checker.check_directory(Path("tools"))
    assert isinstance(checker.violations, list)


def test_self_exclusion():
    """Test that compliance checker excludes itself from violations."""
    checker = ASTComplianceChecker()

    # Create a temporary file with subprocess call (actual forbidden pattern)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('import subprocess\nsubprocess.run(["grep", "skip"], shell=True)\n')
        temp_file = Path(f.name)

    try:
        # Check the compliance checker itself - should be skipped
        checker_file = (
            Path(__file__).resolve().parents[2] / "ops_scripts" / "ci" / "check_ast_collection_compliance.py"
        )
        if checker_file.exists():
            checker._check_file(checker_file)
            # Should have no violations from self-check
            violations_from_self = [
                v for v in checker.violations if "check_ast_collection_compliance.py" in str(v[0])
            ]
            assert len(violations_from_self) == 0, f"Self-check found violations: {violations_from_self}"

        # Now check temp file - should detect violations
        checker._check_file(temp_file)
        assert len(checker.violations) > 0, "Temp file should still trigger violations"
    finally:
        temp_file.unlink(missing_ok=True)


def test_path_handling_outside_repo():
    """Test that files outside repo are handled gracefully."""
    checker = ASTComplianceChecker()

    # Create a temporary file outside repo with subprocess call
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('import subprocess\nsubprocess.run(["grep", "skip"], shell=True)\n')
        temp_file = Path(f.name)

    try:
        # Should handle files outside repo without crashing
        checker._check_file(temp_file)
        assert len(checker.violations) > 0, (
            f"Expected violations from temp file, got {len(checker.violations)}"
        )
        # Violation should use absolute path since file is outside repo
        assert any(str(temp_file) in str(v[0]) for v in checker.violations), (
            "Expected absolute path for outside-repo file"
        )
    finally:
        temp_file.unlink(missing_ok=True)


def test_has_violations():
    """Test has_violations method."""
    checker = ASTComplianceChecker()

    # Initially no violations
    assert not checker.has_violations()

    # Add a fake violation
    checker.violations.append(("test.py", 1, "test violation"))

    # Should have violations now
    assert checker.has_violations()


if __name__ == "__main__":
    test_check_directory_with_string_path()
    test_check_directory_with_path_object()
    test_self_exclusion()
    test_path_handling_outside_repo()
    test_has_violations()
    print("✅ All AST compliance checker tests passed")
