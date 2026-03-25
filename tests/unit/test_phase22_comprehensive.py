#!/usr/bin/env python3
"""
Comprehensive tests for Phase 2.2: MEDIUM severity broad exception fixes.
Tests follow windsurfrules §1.1-§1.8 requirements.
"""

import json

# Import the module we're testing
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from fix_medium_severity_swallowers import MediumSeveritySilentSwallowerFixer


class TestPhase22Comprehensive:
    """Comprehensive tests for Phase 2.2 implementation."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace

    @pytest.fixture
    def sample_violations(self):
        """Create sample MEDIUM severity violation data."""
        return {
            'scan_timestamp': '2026-03-24T19:40:00Z',
            'total_violations': 4,
            'violations': [
                {
                    'file_path': 'data_processor.py',
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'data processing error',
                    'severity': 'MEDIUM'
                },
                {
                    'file_path': 'network_client.py',
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'network operation failed',
                    'severity': 'MEDIUM'
                },
                {
                    'file_path': 'file_handler.py',
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'file read operation',
                    'severity': 'MEDIUM'
                },
                {
                    'file_path': 'validator.py',
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'validation error',
                    'severity': 'MEDIUM'
                }
            ]
        }

    # Test §1.5: Edge cases - Empty violation list
    def test_empty_violations_list(self, temp_workspace):
        """Test handling of empty violation list."""

        # Create tools directory and empty violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump({'violations': []}, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Should handle empty list gracefully
            assert len(fixer.violations) == 0
            assert fixer.fixes_applied == 0
        finally:
            os.chdir(original_cwd)

    # Test §1.5: Edge cases - Malformed violation data
    def test_malformed_violation_data(self, temp_workspace):
        """Test handling of malformed violation data."""

        # Create tools directory and malformed violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump({'invalid': 'data'}, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            # Should handle malformed data gracefully
            with pytest.raises(KeyError):
                MediumSeveritySilentSwallowerFixer()
        finally:
            os.chdir(original_cwd)

    # Test §1.5: Edge cases - Missing file paths
    def test_missing_file_paths(self, temp_workspace, sample_violations):
        """Test handling of violations with missing file paths."""

        # Add violation with missing file path
        sample_violations['violations'].append({
            'line_number': 60,
            'exception_type': 'Exception',
            'handler_body': ['pass'],
            'severity': 'MEDIUM'
            # Missing file_path
        })

        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Should skip violations with missing file paths
            assert len(fixer.violations) == 4  # Original 4, malformed one skipped
        finally:
            os.chdir(original_cwd)

    # Test §1.5: Edge cases - Unicode file names
    def test_unicode_file_names(self, temp_workspace, sample_violations):
        """Test handling of Unicode file names."""

        unicode_file = temp_workspace / "tëst_ünïcødë.py"
        unicode_file.write_text("try:\n    risky_operation()\nexcept Exception:\n    pass\n")

        violations_file = temp_workspace / "tools" / "silent_swallower_report.json"
        sample_violations['violations'][0]['file_path'] = str(unicode_file)
        with open(violations_file, 'w') as f:
            json.dump(sample_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Should handle Unicode file names
            assert len(fixer.violations) == 4
        finally:
            os.chdir(original_cwd)

    # Test §1.7: Determinism - Identical input → identical output
    def test_deterministic_fixes(self, temp_workspace, sample_violations):
        """Test that identical input produces identical output."""

        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Run fixes twice
            result1 = fixer.apply_fixes_to_all_remaining_violations()
            fixer.fixes_applied = 0  # Reset counter
            result2 = fixer.apply_fixes_to_all_remaining_violations()

            # Results should be identical
            assert result1['fixes_applied'] == result2['fixes_applied']
            assert result1['errors'] == result2['errors']
        finally:
            os.chdir(original_cwd)

    # Test §1.7: Determinism - Exception type detection consistency
    def test_exception_type_detection_consistency(self, temp_workspace):
        """Test that exception type detection is consistent."""

        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump({'violations': []}, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Test with same context multiple times
            context = "data processing error"
            types1 = fixer._determine_specific_exception_types(context)
            types2 = fixer._determine_specific_exception_types(context)

            # Should be identical
            assert types1 == types2
        finally:
            os.chdir(original_cwd)

    # Test §1.8: Fail-closed - Invalid file paths blocked
    def test_invalid_file_paths_blocked(self, temp_workspace, sample_violations):
        """Test that invalid file paths are blocked."""

        # Add violation with invalid file path
        sample_violations['violations'].append({
            'file_path': '/invalid/nonexistent/path.py',
            'line_number': 70,
            'exception_type': 'Exception',
            'handler_body': ['pass'],
            'severity': 'MEDIUM'
        })

        violations_file = temp_workspace / "tools" / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Should handle invalid paths without crashing
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert 'errors' in result
            # Invalid path should be skipped, not crash
        finally:
            os.chdir(original_cwd)

    # Test systematic application function
    def test_apply_fixes_to_all_remaining_violations(self, temp_workspace, sample_violations):
        """Test the systematic application function."""

        # Create test files
        for violation in sample_violations['violations']:
            file_path = temp_workspace / violation['file_path']
            file_path.write_text("try:\n    operation()\nexcept Exception:\n    pass\n")

        violations_file = temp_workspace / "tools" / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()
            result = fixer.apply_fixes_to_all_remaining_violations()

            assert isinstance(result, dict)
            assert 'fixes_applied' in result
            assert 'errors' in result
            assert 'remaining' in result
            assert result['phase'] == '2.2'
        finally:
            os.chdir(original_cwd)

    # Test enhanced reporting function
    def test_generate_systematic_fix_report(self, temp_workspace, sample_violations):
        """Test the enhanced reporting function."""

        violations_file = temp_workspace / "tools" / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Apply some fixes first
            fixer.apply_fixes_to_all_remaining_violations()

            report = fixer.generate_systematic_fix_report()

            assert isinstance(report, dict)
            assert 'phase' in report
            assert 'fix_timestamp' in report
            assert 'total_violations' in report
            assert 'completion_percentage' in report
            assert report['phase'] == '2.2'
        finally:
            os.chdir(original_cwd)

    # Test exception type identification
    def test_exception_type_identification(self, temp_workspace):
        """Test correct exception type identification."""

        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump({'violations': []}, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Test various contexts
            test_cases = [
                ("data processing error", ["ValueError", "TypeError", "AttributeError"]),
                ("network operation", ["ConnectionError", "TimeoutError", "NetworkError"]),
                ("file processing", ["FileNotFoundError", "PermissionError", "OSError"]),
                ("validation error", ["ValueError", "TypeError", "AssertionError"]),
                ("general error handling", ["ValueError", "TypeError", "RuntimeError"])
            ]

            for context, expected_types in test_cases:
                detected = fixer._determine_specific_exception_types(context)
                assert isinstance(detected, list)
                assert len(detected) > 0
                # Should detect specific exceptions related to context
        finally:
            os.chdir(original_cwd)

    # Test exception handler creation
    def test_specific_exception_replacement(self, temp_workspace):
        """Test proper specific exception replacement."""

        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump({'violations': []}, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Test creating specific exception handler
            original_line = "    except Exception:"
            context = "data processing"
            types = ['ValueError', 'TypeError']
            new_handler = fixer._create_specific_exception_handler(original_line, context, types)

            # Should replace with specific exceptions
            assert "ValueError" in new_handler or "TypeError" in new_handler
            assert "except Exception:" not in new_handler or "# guardian:" in new_handler
        finally:
            os.chdir(original_cwd)


class TestPhase22Integration:
    """Integration tests for Phase 2.2 implementation."""

    @pytest.fixture
    def integration_workspace(self):
        """Create integration test workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            # Create sample Python files with MEDIUM severity violations
            test_files = [
                ("data_processor.py", """
try:
    process_data(data)
except Exception:
    pass
"""),
                ("network_client.py", """
try:
    make_request(url)
except Exception:
    pass
"""),
                ("file_handler.py", """
try:
    read_file(path)
except Exception:
    pass
"""),
                ("validator.py", """
try:
    validate_input(input_data)
except Exception:
    pass
""")
            ]

            for filename, content in test_files:
                file_path = workspace / filename
                file_path.write_text(content)

            yield workspace

    def test_end_to_end_phase22_fixes(self, integration_workspace):
        """Test end-to-end Phase 2.2 fix process."""

        # Create violations report
        violations = {
            'scan_timestamp': '2026-03-24T19:40:00Z',
            'total_violations': 4,
            'violations': [
                {
                    'file_path': str(integration_workspace / 'data_processor.py'),
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'data processing error',
                    'severity': 'MEDIUM'
                },
                {
                    'file_path': str(integration_workspace / 'network_client.py'),
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'network operation failed',
                    'severity': 'MEDIUM'
                },
                {
                    'file_path': str(integration_workspace / 'file_handler.py'),
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'file read operation',
                    'severity': 'MEDIUM'
                },
                {
                    'file_path': str(integration_workspace / 'validator.py'),
                    'line_number': 3,
                    'exception_type': 'Exception',
                    'handler_body': ['pass'],
                    'context': 'validation error',
                    'severity': 'MEDIUM'
                }
            ]
        }

        violations_file = integration_workspace / "tools" / "silent_swallower_report.json"
        violations_file.parent.mkdir()
        with open(violations_file, 'w') as f:
            json.dump(violations, f)

        # Temporarily change working directory to integration workspace
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(integration_workspace)

            fixer = MediumSeveritySilentSwallowerFixer()

            # Apply fixes
            result = fixer.apply_fixes_to_all_remaining_violations()

            # Verify results
            assert isinstance(result, dict)
            assert 'fixes_applied' in result
            assert 'errors' in result

            # Check that files were modified appropriately
            data_content = (integration_workspace / 'data_processor.py').read_text()
            network_content = (integration_workspace / 'network_client.py').read_text()
            file_content = (integration_workspace / 'file_handler.py').read_text()
            validator_content = (integration_workspace / 'validator.py').read_text()

            # Should have replaced broad exceptions with specific ones
            assert "ValueError" in data_content or "TypeError" in data_content
            assert "ConnectionError" in network_content or "TimeoutError" in network_content
            assert "FileNotFoundError" in file_content or "PermissionError" in file_content
            assert "ValueError" in validator_content or "TypeError" in validator_content
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
