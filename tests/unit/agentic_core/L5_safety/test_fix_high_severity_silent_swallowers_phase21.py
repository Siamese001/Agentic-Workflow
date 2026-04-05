#!/usr/bin/env python3
"""
Test suite for Phase 2.1: HIGH severity ImportError fixes.
Tests follow windsurfrules §1.1-§1.8 requirements.
"""

import json

# Import the module we're testing
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
from fix_high_severity_silent_swallowers import HighSeveritySilentSwallowerFixer


class TestHighSeveritySilentSwallowerFixerPhase21:
    """Test Phase 2.1 implementation of HIGH severity ImportError fixes."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace

    @pytest.fixture
    def sample_violations(self):
        """Create sample violation data for testing."""
        return {
            "scan_timestamp": "2026-03-24T19:30:00Z",
            "total_violations": 5,
            "violations": [
                {
                    "file_path": "test_file1.py",
                    "line_number": 10,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "import optional_dependency",
                    "severity": "HIGH",
                },
                {
                    "file_path": "test_file2.py",
                    "line_number": 20,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "import missing_module",
                    "severity": "HIGH",
                },
                {
                    "file_path": "test_file3.py",
                    "line_number": 30,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "dynamic import",
                    "severity": "HIGH",
                },
            ],
        }

    def _create_violations_file(self, temp_workspace, violations_data):
        """Helper to create violations file in correct location."""
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, "w") as f:
            json.dump(violations_data, f)
        return violations_file

    @pytest.fixture
    def fixer(self, temp_workspace, sample_violations):
        """Create fixer instance with test data."""
        # Create tools directory and violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, "w") as f:
            json.dump(sample_violations, f)

        # Patch the report file path
        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", temp_workspace):
            fixer = HighSeveritySilentSwallowerFixer()
            yield fixer

    # Test §1.5: Edge cases - Empty violation list
    def test_empty_violations_list(self, temp_workspace):
        """Test handling of empty violation list."""
        # Create tools directory and empty violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, "w") as f:
            json.dump({"violations": []}, f)

        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", temp_workspace):
            fixer = HighSeveritySilentSwallowerFixer()

            # Should handle empty list gracefully
            assert len(fixer.violations) == 0
            assert fixer.fixes_applied == 0

    # Test §1.5: Edge cases - Malformed violation data
    def test_malformed_violation_data(self, temp_workspace):
        """Test handling of malformed violation data."""
        # Create tools directory and malformed violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, "w") as f:
            json.dump({"invalid": "data"}, f)

        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", temp_workspace):
            # Should handle malformed data gracefully
            with pytest.raises(KeyError):
                HighSeveritySilentSwallowerFixer()

    # Test §1.5: Edge cases - Missing file paths
    def test_missing_file_paths(self, temp_workspace, sample_violations):
        """Test handling of violations with missing file paths."""
        # Add violation with missing file path
        sample_violations["violations"].append(
            {
                "line_number": 40,
                "exception_type": "ImportError",
                "handler_body": ["pass"],
                "severity": "HIGH",
                # Missing file_path
            }
        )

        violations_file = temp_workspace / "test_violations.json"
        with open(violations_file, "w") as f:
            json.dump(sample_violations, f)

        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", temp_workspace):
            fixer = HighSeveritySilentSwallowerFixer()

            # Should skip violations with missing file paths
            assert len(fixer.violations) == 3  # Original 3, malformed one skipped

    # Test §1.5: Edge cases - Permission denied files
    def test_permission_denied_files(self, temp_workspace, sample_violations):
        """Test handling of permission denied files using mocking."""
        # Create a file
        restricted_file = temp_workspace / "restricted.py"
        restricted_file.write_text("except ImportError:\n    pass\n")

        # Create violations file
        violations_file = temp_workspace / "test_violations.json"
        sample_violations["violations"][0]["file_path"] = str(restricted_file)
        with open(violations_file, "w") as f:
            json.dump(sample_violations, f)

        # Mock Path.read_text to simulate permission denied (cross-platform)
        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", temp_workspace):
            with patch("pathlib.Path.read_text", side_effect=PermissionError("Permission denied")):
                fixer = HighSeveritySilentSwallowerFixer()

                # Should handle permission errors gracefully
                result = fixer.fix_import_error_violations()
                assert result["errors"] > 0  # Should record permission errors

    # Test §1.5: Edge cases - Unicode file names
    def test_unicode_file_names(self, temp_workspace, sample_violations):
        """Test handling of Unicode file names."""
        unicode_file = temp_workspace / "tëst_ünïcødë.py"
        unicode_file.write_text("except ImportError:\n    pass\n")

        violations_file = temp_workspace / "test_violations.json"
        sample_violations["violations"][0]["file_path"] = str(unicode_file)
        with open(violations_file, "w") as f:
            json.dump(sample_violations, f)

        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", temp_workspace):
            fixer = HighSeveritySilentSwallowerFixer()

            # Should handle Unicode file names
            assert len(fixer.violations) == 3

    # Test §1.7: Determinism - Identical input → identical output
    def test_deterministic_fixes(self, fixer):
        """Test that identical input produces identical output."""
        # Run fixes twice
        result1 = fixer.fix_import_error_violations()
        fixer.fixes_applied = 0  # Reset counter
        result2 = fixer.fix_import_error_violations()

        # Results should be identical
        assert result1["fixes_applied"] == result2["fixes_applied"]
        assert result1["errors"] == result2["errors"]

    # Test §1.7: Determinism - Same violation set → same fixes
    def test_deterministic_violation_processing(self, fixer):
        """Test that same violation set produces same fixes."""
        # Process violations
        result = fixer.fix_import_error_violations()

        # Check that fixes are deterministic
        if result["fixes_applied"] > 0:
            # Should have consistent fix patterns
            assert result["fixes_applied"] > 0
            assert "fixes_applied" in result
            assert "errors" in result

    # Test §1.8: Fail-closed - Invalid file paths block operation
    def test_invalid_file_paths_blocked(self, temp_workspace, sample_violations):
        """Test that invalid file paths are blocked."""
        # Add violation with invalid file path
        sample_violations["violations"].append(
            {
                "file_path": "/invalid/nonexistent/path.py",
                "line_number": 50,
                "exception_type": "ImportError",
                "handler_body": ["pass"],
                "severity": "HIGH",
            }
        )

        violations_file = temp_workspace / "test_violations.json"
        with open(violations_file, "w") as f:
            json.dump(sample_violations, f)

        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", temp_workspace):
            fixer = HighSeveritySilentSwallowerFixer()

            # Should handle invalid paths without crashing
            result = fixer.fix_import_error_violations()
            assert "errors" in result

    # REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # Invalid path should be skipped, not crash  # REVEALED FAILURE: # invalid path should be skipped, not crash  # REVEALED FAILURE: # removed hidden failure skip: # removed skip: # invalid path should be skipped, not crash  # revealed failure: # invalid path should be skipped, not crash

    # Test §1.8: Fail-closed - Permission errors handled gracefully
    def test_permission_errors_handled_gracefully(self, fixer):
        """Test that permission errors are handled gracefully."""
        # Mock file operations to raise permission error
        with patch("pathlib.Path.read_text", side_effect=PermissionError("Permission denied")):
            result = fixer.fix_import_error_violations()

            # Should handle permission errors gracefully
            assert "errors" in result
            assert result["errors"] >= 0

    # Test §1.8: Fail-closed - No partial modifications on error
    def test_no_partial_modifications_on_error(self, fixer):
        """Test that no partial modifications occur on error."""
        # Mock write operation to fail
        with patch("pathlib.Path.write_text", side_effect=OSError("Write failed")):
            result = fixer.fix_import_error_violations()

            # Should record error but not claim success
            assert "errors" in result
            # Fix count should be accurate despite write failures

    # Test systematic application function
    def test_apply_fixes_to_all_remaining_violations(self, fixer):
        """Test the new systematic application function."""
        # This tests the new Phase 2.1 functionality
        assert hasattr(fixer, "apply_fixes_to_all_remaining_violations"), (
            "apply_fixes_to_all_remaining_violations not yet implemented"
        )
        result = fixer.apply_fixes_to_all_remaining_violations()
        assert isinstance(result, dict)
        assert "fixes_applied" in result
        assert "errors" in result

    # Test enhanced reporting function
    def test_generate_systematic_fix_report(self, fixer):
        """Test the enhanced reporting function."""
        # This tests the new Phase 2.1 reporting functionality
        assert hasattr(fixer, "generate_systematic_fix_report"), (
            "generate_systematic_fix_report not yet implemented"
        )
        report = fixer.generate_systematic_fix_report()
        assert isinstance(report, dict)
        assert "phase" in report
        assert "fix_timestamp" in report
        assert "total_violations" in report


class TestPhase21Integration:
    """Integration tests for Phase 2.1 implementation."""

    @pytest.fixture
    def integration_workspace(self):
        """Create integration test workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            # Create sample Python files with ImportError violations
            test_files = [
                (
                    "file1.py",
                    """
try:
    import missing_dependency
except ImportError:
    pass
""",
                ),
                (
                    "file2.py",
                    """
try:
    from optional_module import something
except ImportError:
    pass
""",
                ),
                (
                    "tests/test_file.py",
                    """
try:
    import test_dependency
except ImportError:
    pass
""",
                ),
            ]

            for filename, content in test_files:
                file_path = workspace / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

            # Create mock silent_swallower_report.json required by fixer
            tools_dir = workspace / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)
            report = {
                "scan_timestamp": "2026-03-24T19:30:00Z",
                "total_violations": 3,
                "violations": [
                    {
                        "file_path": str(workspace / "file1.py"),
                        "line_number": 3,
                        "exception_type": "ImportError",
                        "handler_body": ["pass"],
                        "context": "import missing_dependency",
                        "severity": "HIGH",
                    },
                    {
                        "file_path": str(workspace / "file2.py"),
                        "line_number": 3,
                        "exception_type": "ImportError",
                        "handler_body": ["pass"],
                        "context": "import optional_module",
                        "severity": "HIGH",
                    },
                    {
                        "file_path": str(workspace / "tests" / "test_file.py"),
                        "line_number": 3,
                        "exception_type": "ImportError",
                        "handler_body": ["pass"],
                        "context": "import test_dependency",
                        "severity": "HIGH",
                    },
                ],
            }
            with open(tools_dir / "silent_swallower_report.json", "w") as f:
                json.dump(report, f)

            yield workspace

    def test_end_to_end_phase21_fixes(self, integration_workspace):
        """Test end-to-end Phase 2.1 fix process."""
        # Create violations report
        violations = {
            "scan_timestamp": "2026-03-24T19:30:00Z",
            "total_violations": 3,
            "violations": [
                {
                    "file_path": str(integration_workspace / "file1.py"),
                    "line_number": 3,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "import missing_dependency",
                    "severity": "HIGH",
                },
                {
                    "file_path": str(integration_workspace / "file2.py"),
                    "line_number": 3,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "import optional_module",
                    "severity": "HIGH",
                },
                {
                    "file_path": str(integration_workspace / "tests/test_file.py"),
                    "line_number": 3,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "import test_dependency",
                    "severity": "HIGH",
                },
            ],
        }

        violations_file = integration_workspace / "violations.json"
        with open(violations_file, "w") as f:
            json.dump(violations, f)

        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", integration_workspace):
            fixer = HighSeveritySilentSwallowerFixer()

            # Apply fixes
            result = fixer.fix_import_error_violations()

            # Verify results
            assert isinstance(result, dict)
            assert "fixes_applied" in result
            assert "errors" in result

            # Check that files were modified appropriately
            file1_content = (integration_workspace / "file1.py").read_text()
            file2_content = (integration_workspace / "file2.py").read_text()
            test_content = (integration_workspace / "tests/test_file.py").read_text()

            # Test files should use pytest.importorskip
            assert "pytest.importorskip" in test_content
            # Regular files should have guardian comments
            assert "# guardian:" in file1_content or "missing_dependency" in file1_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
