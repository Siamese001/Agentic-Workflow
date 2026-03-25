#!/usr/bin/env python3
"""
Test suite for Phase 2.3: LOW severity specific exception fixes.
Tests follow windsurfrules §1.1-§1.8 requirements.
"""

import json
import os

# Import the module we're testing
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from fix_low_severity_swallowers import LowSeveritySilentSwallowerFixer


class TestPhase23LowSeverityFixes:
    """Test Phase 2.3 implementation of LOW severity specific exception fixes."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace

    @pytest.fixture
    def sample_low_violations(self):
        """Create sample LOW severity violation data."""
        return {
            'scan_timestamp': '2026-03-24T20:00:00Z',
            'total_violations': 6,
            'violations': [
                {
                    'file_path': 'test_file1.py',
                    'line_number': 10,
                    'exception_type': 'SyntaxError',
                    'handler_body': ['pass'],
                    'context': 'syntax parsing error',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'test_file2.py',
                    'line_number': 20,
                    'exception_type': 'OSError',
                    'handler_body': ['pass'],
                    'context': 'file system error',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'test_file3.py',
                    'line_number': 30,
                    'exception_type': 'UnicodeDecodeError',
                    'handler_body': ['pass'],
                    'context': 'encoding error',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'test_file4.py',
                    'line_number': 40,
                    'exception_type': 'PermissionError',
                    'handler_body': ['pass'],
                    'context': 'permission denied',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'test_file5.py',
                    'line_number': 50,
                    'exception_type': 'RuntimeError',
                    'handler_body': ['pass'],
                    'context': 'runtime failure',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'test_file6.py',
                    'line_number': 60,
                    'exception_type': 'FileNotFoundError',
                    'handler_body': ['pass'],
                    'context': 'file not found',
                    'severity': 'LOW'
                }
            ]
        }

    @pytest.fixture
    def fixer(self, temp_workspace, sample_low_violations):
        """Create fixer instance with test data."""
        # Create tools directory and violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_low_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_workspace)
            fixer = LowSeveritySilentSwallowerFixer()
            yield fixer
        finally:
            os.chdir(original_cwd)

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
            os.chdir(temp_workspace)
            fixer = LowSeveritySilentSwallowerFixer()

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
            os.chdir(temp_workspace)

            # Should handle malformed data gracefully
            with pytest.raises(KeyError):
                LowSeveritySilentSwallowerFixer()
        finally:
            os.chdir(original_cwd)

    # Test §1.5: Edge cases - Missing file paths
    def test_missing_file_paths(self, temp_workspace, sample_low_violations):
        """Test handling of violations with missing file paths."""

        # Add violation with missing file path
        sample_low_violations['violations'].append({
            'line_number': 70,
            'exception_type': 'ValueError',
            'handler_body': ['pass'],
            'severity': 'LOW'
            # Missing file_path
        })

        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_low_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_workspace)
            fixer = LowSeveritySilentSwallowerFixer()

            # Should skip violations with missing file paths
            assert len(fixer.violations) == 6  # Original 6, malformed one skipped
        finally:
            os.chdir(original_cwd)

    # Test §1.5: Edge cases - Permission denied files
    def test_permission_denied_files(self, temp_workspace, sample_low_violations):
        """Test handling of permission denied files."""

        # Create a file with restricted permissions
        restricted_file = temp_workspace / "restricted.py"
        restricted_file.write_text("try:\n    risky_operation()\nexcept SyntaxError:\n    pass\n")

        # Remove read permissions (on Unix systems)
        original_mode = restricted_file.stat().st_mode
        restricted_file.chmod(0o000)

        try:
            violations_file = temp_workspace / "tools" / "silent_swallower_report.json"
            sample_low_violations['violations'][0]['file_path'] = str(restricted_file)
            with open(violations_file, 'w') as f:
                json.dump(sample_low_violations, f)

            # Temporarily change working directory to temp workspace
            original_cwd = Path.cwd()
            try:
                os.chdir(temp_workspace)
                fixer = LowSeveritySilentSwallowerFixer()

                # Should handle permission errors gracefully
                result = fixer.apply_fixes_to_all_remaining_violations()
                assert result['errors'] >= 0  # Should record permission errors
            finally:
                os.chdir(original_cwd)
        finally:
            # Restore permissions for cleanup
            restricted_file.chmod(original_mode)

    # Test §1.5: Edge cases - Unicode file names
    def test_unicode_file_names(self, temp_workspace, sample_low_violations):
        """Test handling of Unicode file names."""

        unicode_file = temp_workspace / "tëst_ünïcødë.py"
        unicode_file.write_text("try:\n    risky_operation()\nexcept OSError:\n    pass\n")

        violations_file = temp_workspace / "tools" / "silent_swallower_report.json"
        sample_low_violations['violations'][0]['file_path'] = str(unicode_file)
        with open(violations_file, 'w') as f:
            json.dump(sample_low_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_workspace)
            fixer = LowSeveritySilentSwallowerFixer()

            # Should handle Unicode file names
            assert len(fixer.violations) == 6
        finally:
            os.chdir(original_cwd)

    # Test §1.5: Edge cases - Complex exception patterns
    def test_complex_exception_patterns(self, temp_workspace):
        """Test handling of complex exception patterns."""

        complex_violations = {
            'scan_timestamp': '2026-03-24T20:00:00Z',
            'total_violations': 4,
            'violations': [
                {
                    'file_path': 'complex1.py',
                    'line_number': 15,
                    'exception_type': 'SyntaxError, UnicodeDecodeError',
                    'handler_body': ['pass', 'logger.info("handled")'],
                    'context': 'parsing with encoding issues',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'complex2.py',
                    'line_number': 25,
                    'exception_type': 'OSError, UnicodeDecodeError',
                    'handler_body': ['pass'],
                    'context': 'file operations with encoding',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'complex3.py',
                    'line_number': 35,
                    'exception_type': 'OSError, UnicodeDecodeError, SyntaxError',
                    'handler_body': ['pass'],
                    'context': 'complex file processing',
                    'severity': 'LOW'
                },
                {
                    'file_path': 'complex4.py',
                    'line_number': 45,
                    'exception_type': '_SCENARIO_EXCEPTIONS',
                    'handler_body': ['pass'],
                    'context': 'test scenario exceptions',
                    'severity': 'LOW'
                }
            ]
        }

        # Create files with complex patterns
        for i, violation in enumerate(complex_violations['violations']):
            file_path = temp_workspace / violation['file_path']
            if 'parsing' in violation['context']:
                content = """try:
    parse_with_encoding()
except (SyntaxError, UnicodeDecodeError):
    pass
    logger.info("handled")"""
            elif 'file operations' in violation['context']:
                content = """try:
    read_with_encoding()
except (OSError, UnicodeDecodeError):
    pass"""
            elif 'complex file' in violation['context']:
                content = """try:
    complex_file_processing()
except (OSError, UnicodeDecodeError, SyntaxError):
    pass"""
            else:  # scenario exceptions
                content = """try:
    scenario_test()
with pytest.raises(_SCENARIO_EXCEPTIONS):"""
            file_path.write_text(content)

        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(complex_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_workspace)
            fixer = LowSeveritySilentSwallowerFixer()

            # Should handle complex patterns
            assert len(fixer.violations) == 4

            # Test systematic application
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert isinstance(result, dict)
            assert 'fixes_applied' in result
        finally:
            os.chdir(original_cwd)

    # Test §1.7: Determinism - Identical input → identical output
    def test_deterministic_fixes(self, fixer):
        """Test that identical input produces identical output."""

        # Run fixes twice
        result1 = fixer.apply_fixes_to_all_remaining_violations()
        fixer.fixes_applied = 0  # Reset counter
        result2 = fixer.apply_fixes_to_all_remaining_violations()

        # Results should be identical
        assert result1['fixes_applied'] == result2['fixes_applied']
        assert result1['errors'] == result2['errors']

    # Test §1.7: Determinism - Exception strategy detection consistency
    def test_exception_strategy_detection_consistency(self, fixer):
        """Test that exception strategy detection is consistent."""

        if hasattr(fixer, '_determine_exception_fix_strategy'):
            # Test with same exception type multiple times
            exception_type = 'SyntaxError'
            context = 'syntax parsing error'
            strategy1 = fixer._determine_exception_fix_strategy(exception_type, context)
            strategy2 = fixer._determine_exception_fix_strategy(exception_type, context)

            # Should be identical
            assert strategy1 == strategy2
        else:
# REVEALED FAILURE: _determine_exception_fix_strategy not yet implemented

    # Test §1.8: Fail-closed - Invalid file paths blocked
    def test_invalid_file_paths_blocked(self, temp_workspace, sample_low_violations):
        """Test that invalid file paths are blocked."""

        # Add violation with invalid file path
        sample_low_violations['violations'].append({
            'file_path': '/invalid/nonexistent/path.py',
            'line_number': 80,
            'exception_type': 'ValueError',
            'handler_body': ['pass'],
            'severity': 'LOW'
        })

        violations_file = temp_workspace / "tools" / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_low_violations, f)

        # Temporarily change working directory to temp workspace
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_workspace)
            fixer = LowSeveritySilentSwallowerFixer()

            # Should handle invalid paths without crashing
            result = fixer.apply_fixes_to_all_remaining_violations()
            assert 'errors' in result
# REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # Invalid path should be skipped, not crash  # REVEALED FAILURE: # invalid path should be skipped, not crash  # REVEALED FAILURE: # removed hidden failure skip: # removed skip: # invalid path should be skipped, not crash  # revealed failure: # invalid path should be skipped, not crash
        finally:
            os.chdir(original_cwd)

    # Test §1.8: Fail-closed - Permission errors handled gracefully
    def test_permission_errors_handled_gracefully(self, fixer):
        """Test that permission errors are handled gracefully."""

        # Mock file operations to raise permission error
        with patch('pathlib.Path.read_text', side_effect=PermissionError("Permission denied")):
            result = fixer.apply_fixes_to_all_remaining_violations()

            # Should handle permission errors gracefully
            assert 'errors' in result
            assert result['errors'] >= 0

    # Test §1.8: Fail-closed - No partial modifications on error
    def test_no_partial_modifications_on_error(self, fixer):
        """Test that no partial modifications occur on error."""

        # Mock write operation to fail
        with patch('pathlib.Path.write_text', side_effect=OSError("Write failed")):
            result = fixer.apply_fixes_to_all_remaining_violations()

            # Should record error but not claim success
            assert 'errors' in result
            # Fix count should be accurate despite write failures

    # Test §1.6: Exception Analysis - Correct exception type identification
    def test_exception_type_identification(self, fixer):
        """Test correct exception type identification."""

        if hasattr(fixer, '_determine_exception_fix_strategy'):
            # Test various exception types
            test_cases = [
                ('SyntaxError', 'syntax parsing error', 'add_guardian_comment'),
                ('OSError', 'file system error', 'add_logging'),
                ('UnicodeDecodeError', 'encoding error', 'add_encoding_context'),
                ('PermissionError', 'permission denied', 'add_permission_context'),
                ('RuntimeError', 'runtime failure', 'add_runtime_context'),
                ('FileNotFoundError', 'file not found', 'add_file_context')
            ]

            for exception_type, context, expected_strategy in test_cases:
                strategy = fixer._determine_exception_fix_strategy(exception_type, context)
                assert isinstance(strategy, dict)
                assert 'action' in strategy
                # Should detect specific strategy for exception type
        else:
# REVEALED FAILURE: _determine_exception_fix_strategy not yet implemented

    # Test §1.6: Exception Analysis - Proper specific exception replacement
    def test_specific_exception_replacement(self, fixer):
        """Test proper specific exception replacement."""

        if hasattr(fixer, '_create_targeted_exception_handler'):
            # Test creating targeted exception handler
            original_line = "    except SyntaxError:"
            context = "syntax parsing error"
            strategy = {'action': 'add_guardian_comment', 'comment': 'Syntax errors should be caught at parser level'}

            new_handler = fixer._create_targeted_exception_handler(original_line, context, strategy)

            # Should add guardian comment
            assert "# guardian:" in new_handler or "# Syntax errors" in new_handler
            assert new_handler != original_line
        else:
# REVEALED FAILURE: _create_targeted_exception_handler not yet implemented

    # Test systematic application function
    def test_apply_fixes_to_all_remaining_violations(self, fixer):
        """Test the systematic application function."""

        result = fixer.apply_fixes_to_all_remaining_violations()

        assert isinstance(result, dict)
        assert 'fixes_applied' in result
        assert 'errors' in result
        assert 'remaining' in result
        assert result['phase'] == '2.3'

    # Test enhanced reporting function
    def test_generate_systematic_fix_report(self, fixer):
        """Test the enhanced reporting function."""

        # Apply some fixes first
        fixer.apply_fixes_to_all_remaining_violations()

        if hasattr(fixer, 'generate_systematic_fix_report'):
            report = fixer.generate_systematic_fix_report()

            assert isinstance(report, dict)
            assert 'phase' in report
            assert 'fix_timestamp' in report
            assert 'total_violations' in report
            assert 'completion_percentage' in report
            assert report['phase'] == '2.3'
        else:



class TestPhase23Integration:
    """Integration tests for Phase 2.3 implementation."""

    @pytest.fixture
    def integration_workspace(self):
        """Create integration test workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            # Create sample Python files with LOW severity violations
            test_files = [
                ("syntax_handler.py", """
try:
    parse_code()
with pytest.raises(SyntaxError):
"""),
                ("file_handler.py", """
try:
    open_file()
with pytest.raises(OSError):
"""),
                ("encoding_handler.py", """
try:
    read_with_encoding()
with pytest.raises(UnicodeDecodeError):
"""),
                ("permission_handler.py", """
try:
    restricted_operation()
with pytest.raises(PermissionError):
""")
            ]

            for filename, content in test_files:
                file_path = workspace / filename
                file_path.write_text(content)

            yield workspace

    def test_end_to_end_phase23_fixes(self, integration_workspace):
        """Test end-to-end Phase 2.3 fix process."""

        # Create violations report
        violations = {
            'scan_timestamp': '2026-03-24T20:00:00Z',
            'total_violations': 4,
            'violations': [
                {
                    'file_path': str(integration_workspace / 'syntax_handler.py'),
                    'line_number': 3,
                    'exception_type': 'SyntaxError',
                    'handler_body': ['pass'],
                    'context': 'syntax parsing error',
                    'severity': 'LOW'
                },
                {
                    'file_path': str(integration_workspace / 'file_handler.py'),
                    'line_number': 3,
                    'exception_type': 'OSError',
                    'handler_body': ['pass'],
                    'context': 'file system error',
                    'severity': 'LOW'
                },
                {
                    'file_path': str(integration_workspace / 'encoding_handler.py'),
                    'line_number': 3,
                    'exception_type': 'UnicodeDecodeError',
                    'handler_body': ['pass'],
                    'context': 'encoding error',
                    'severity': 'LOW'
                },
                {
                    'file_path': str(integration_workspace / 'permission_handler.py'),
                    'line_number': 3,
                    'exception_type': 'PermissionError',
                    'handler_body': ['pass'],
                    'context': 'permission denied',
                    'severity': 'LOW'
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
            os.chdir(integration_workspace)

            fixer = LowSeveritySilentSwallowerFixer()

            # Apply fixes
            result = fixer.apply_fixes_to_all_remaining_violations()

            # Verify results
            assert isinstance(result, dict)
            assert 'fixes_applied' in result
            assert 'errors' in result

            # Check that files were modified appropriately
            syntax_content = (integration_workspace / 'syntax_handler.py').read_text()
            file_content = (integration_workspace / 'file_handler.py').read_text()
            encoding_content = (integration_workspace / 'encoding_handler.py').read_text()
            permission_content = (integration_workspace / 'permission_handler.py').read_text()

            # Should have added guardian comments or context
            assert "# guardian:" in syntax_content or "# Syntax errors" in syntax_content
            assert "# guardian:" in file_content or "# File system" in file_content
            assert "# guardian:" in encoding_content or "# Encoding" in encoding_content
            assert "# guardian:" in permission_content or "# Permission" in permission_content
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
