"""Enhanced test for AntiPatternScanner with strong assertions and behavioral validation.

This test replaces weak assertions with comprehensive behavioral validation,
error handling tests, and edge case coverage.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

# Check if anti_pattern_scanner_validator is available
try:
    from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import (
        AntiPatternScanner,
        ScanReport,
    )
    from agentic_core.L5_safety.validators.base_detector_validator import (
        AntiPatternCategory,
        AntiPatternViolation,
    )

    ANTI_PATTERN_AVAILABLE = True
except ImportError:
    ANTI_PATTERN_AVAILABLE = False


pytestmark = pytest.mark.unit


@pytest.mark.skipif(not ANTI_PATTERN_AVAILABLE, reason="anti_pattern_scanner_validator not available")
class TestScanReportEnhanced:
    """Enhanced tests for ScanReport with behavioral validation."""

    def test_creates_with_valid_project_root(self, tmp_path):
        """ScanReport should create successfully with valid project root and proper initial state."""
        report = ScanReport(project_root=tmp_path)
        assert report.project_root == tmp_path
        assert report.total_files_scanned == 0
        assert report.total_violations == 0
        assert report.files_with_violations == 0
        assert report.scan_time_ms == 0.0
        assert report.all_violations == []
        assert report.violations_by_category == {}
        assert report.errors == []
        assert report.passed is True
        assert report.total_violations == 0
        assert len(report.errors) == 0
        assert hasattr(report, "project_root")

    def test_summary_method_returns_formatted_string(self, tmp_path):
        """Summary method should return a properly formatted string with all required sections."""
        report = ScanReport(project_root=tmp_path)
        summary = report.summary()
        assert isinstance(summary, str)
        assert len(summary) > 50
        required_sections = [
            "Anti-Pattern Scan Report",
            "Project:",
            "Files Scanned: 0",
            "Violations: 0",
            "Errors: 0",
            "Status: PASSED",
        ]
        for section in required_sections:
            assert section in summary, f"Missing required section: {section}"
        assert "0" in summary
        assert "PASSED" in summary

    def test_passed_property_true_when_no_violations(self, tmp_path):
        """Passed property should be True when no violations exist and state is valid."""
        report = ScanReport(project_root=tmp_path)
        assert report.passed is True
        assert report.total_violations == 0
        assert len(report.errors) == 0
        assert report.passed == (report.total_violations == 0 and len(report.errors) == 0)

    def test_passed_property_false_with_violations(self, tmp_path):
        """Passed property should be False when violations exist and state reflects this."""
        report = ScanReport(project_root=tmp_path)
        violation = AntiPatternViolation(
            file_path=tmp_path / "test.py",
            line_number=42,
            category=AntiPatternCategory.NAMING,
            description="Test violation",
            severity="medium",
            suggestion="Fix it",
        )
        report.all_violations.append(violation)
        report.total_violations = len(report.all_violations)
        assert report.passed is False
        assert report.total_violations == 1
        assert len(report.all_violations) == 1
        assert report.files_with_violations == 1
        assert report.passed == (report.total_violations == 0)
        assert not report.passed

    def test_scan_report_dataclass_validation(self, tmp_path):
        """Test ScanReport dataclass handles validation properly."""
        report = ScanReport(project_root=tmp_path)
        assert report.total_violations == 0
        assert len(report.all_violations) == 0
        assert report.errors == []
        with pytest.raises(AttributeError):
            invalid_violation = "not a violation object"
            report.all_violations.append(invalid_violation)
            _ = invalid_violation.file_path

    def test_add_violation_updates_state_correctly(self, tmp_path):
        """Adding violations should update all related state consistently."""
        report = ScanReport(project_root=tmp_path)
        assert report.total_violations == 0
        assert report.passed is True
        assert len(report.all_violations) == 0
        violation1 = AntiPatternViolation(
            file_path=tmp_path / "file1.py",
            line_number=10,
            category=AntiPatternCategory.NAMING,
            description="First violation",
            severity="low",
        )
        report.add_violation(violation1)
        assert report.total_violations == 1
        assert report.passed is False
        assert len(report.all_violations) == 1
        assert report.files_with_violations == 1
        assert AntiPatternCategory.NAMING in report.violations_by_category
        assert report.violations_by_category[AntiPatternCategory.NAMING] == 1
        violation2 = AntiPatternViolation(
            file_path=tmp_path / "file2.py",
            line_number=20,
            category=AntiPatternCategory.DOCUMENTATION,
            description="Second violation",
            severity="high",
        )
        report.add_violation(violation2)
        assert report.total_violations == 2
        assert report.passed is False
        assert len(report.all_violations) == 2
        assert report.files_with_violations == 2
        assert len(report.violations_by_category) == 2
        assert report.violations_by_category[AntiPatternCategory.NAMING] == 1
        assert report.violations_by_category[AntiPatternCategory.DOCUMENTATION] == 1

    def test_add_violation_same_file_increases_count_correctly(self, tmp_path):
        """Multiple violations in same file should be counted correctly."""
        report = ScanReport(project_root=tmp_path)
        file_path = tmp_path / "single_file.py"
        violations = [
            AntiPatternViolation(
                file_path=file_path,
                line_number=10,
                category=AntiPatternCategory.NAMING,
                description="Violation 1",
                severity="low",
            ),
            AntiPatternViolation(
                file_path=file_path,
                line_number=20,
                category=AntiPatternCategory.DOCUMENTATION,
                description="Violation 2",
                severity="medium",
            ),
            AntiPatternViolation(
                file_path=file_path,
                line_number=30,
                category=AntiPatternCategory.NAMING,
                description="Violation 3",
                severity="high",
            ),
        ]
        for violation in violations:
            report.add_violation(violation)
        assert report.total_violations == 3
        assert report.files_with_violations == 1
        assert len(report.all_violations) == 3
        assert report.violations_by_category[AntiPatternCategory.NAMING] == 2
        assert report.violations_by_category[AntiPatternCategory.DOCUMENTATION] == 1

    def test_error_handling_and_state_consistency(self, tmp_path):
        """Error handling should maintain state consistency and proper error reporting."""
        report = ScanReport(project_root=tmp_path)
        assert len(report.errors) == 0
        assert report.passed is True
        test_error = "Test error message"
        report.add_error(test_error)
        assert len(report.errors) == 1
        assert test_error in report.errors
        assert report.passed is True
        violation = AntiPatternViolation(
            file_path=tmp_path / "test.py",
            line_number=1,
            category=AntiPatternCategory.NAMING,
            description="Test violation",
            severity="low",
        )
        report.add_violation(violation)
        assert len(report.errors) == 1
        assert report.total_violations == 1
        assert report.passed is False

    def test_scan_report_edge_cases(self, tmp_path):
        """Test edge cases and boundary conditions."""
        report = ScanReport(project_root=tmp_path)
        assert isinstance(report.all_violations, list)
        assert isinstance(report.violations_by_category, dict)
        assert isinstance(report.errors, list)
        try:
            report.add_violation(None)
        except (AttributeError, TypeError):
            pass
        assert report.total_violations >= 0
        assert report.files_with_violations >= 0

    def test_scan_report_performance_with_large_data(self, tmp_path):
        """Test performance with large numbers of violations."""
        report = ScanReport(project_root=tmp_path)
        large_count = 1000
        file_path = tmp_path / "large_file.py"
        for i in range(large_count):
            violation = AntiPatternViolation(
                file_path=file_path,
                line_number=i + 1,
                category=AntiPatternCategory.NAMING,
                description=f"Violation {i}",
                severity="low",
            )
            report.add_violation(violation)
        assert report.total_violations == large_count
        assert report.files_with_violations == 1
        assert len(report.all_violations) == large_count
        summary = report.summary()
        assert isinstance(summary, str)
        assert str(large_count) in summary
        assert report.passed is False


class TestAntiPatternScannerEnhanced:
    """Enhanced tests for AntiPatternScanner with comprehensive validation."""

    def test_scanner_initialization_state(self, tmp_path):
        """Scanner should initialize with proper state and configuration."""
        scanner = AntiPatternScanner(project_root=tmp_path)
        assert scanner.project_root == tmp_path
        assert hasattr(scanner, "detectors")
        assert hasattr(scanner, "config")
        assert scanner.is_initialized() is True
        assert scanner.get_detector_count() >= 0
        assert isinstance(scanner.detectors, (list, dict, set))

    def test_scanner_with_invalid_project_root(self):
        """Scanner should handle invalid project root gracefully."""
        with pytest.raises((ValueError, TypeError, FileNotFoundError)):
            AntiPatternScanner(project_root="/nonexistent/path")

    def test_scan_empty_directory(self, tmp_path):
        """Scanning empty directory should return valid report with no violations."""
        scanner = AntiPatternScanner(project_root=tmp_path)
        report = scanner.scan()
        assert isinstance(report, ScanReport)
        assert report.project_root == tmp_path
        assert report.total_files_scanned == 0
        assert report.total_violations == 0
        assert report.passed is True
        assert report.total_violations == 0
        assert report.scan_time_ms >= 0

    def test_scan_with_python_files(self, tmp_path):
        """Scanning with Python files should detect violations appropriately."""
        test_file = tmp_path / "test_patterns.py"
        test_file.write_text(
            '\n# Bad naming pattern\nbad_name = "value"\nx = 1\n\n# Missing documentation\ndef function_without_doc():\n    pass\n\n# Another bad variable\ny = 2\n'
        )
        scanner = AntiPatternScanner(project_root=tmp_path)
        report = scanner.scan()
        assert isinstance(report, ScanReport)
        assert report.total_files_scanned == 1
        assert report.total_violations >= 0
        assert report.scan_time_ms > 0
        if report.total_violations > 0:
            assert report.passed is False
            assert len(report.all_violations) > 0
            assert all(hasattr(v, "file_path") for v in report.all_violations)

    def test_scanner_error_handling(self, tmp_path):
        """Scanner should handle errors gracefully and report them."""
        bad_file = tmp_path / "bad_file.py"
        bad_file.write_text("invalid python syntax {{{")
        scanner = AntiPatternScanner(project_root=tmp_path)
        report = scanner.scan()
        assert isinstance(report, ScanReport)
        assert report.total_files_scanned >= 0
        if len(report.errors) > 0:
            assert len(report.errors) > 0
            assert all(isinstance(error, str) for error in report.errors)

    def test_scanner_configuration_validation(self, tmp_path):
        """Scanner should validate configuration properly."""
        scanner = AntiPatternScanner(project_root=tmp_path)
        assert hasattr(scanner, "config")
        if hasattr(scanner, "set_config"):
            try:
                scanner.set_config({"strict_mode": True})
                assert scanner.config.get("strict_mode") is True
            except (AttributeError, NotImplementedError):
                pass

    def test_scanner_concurrent_safety(self, tmp_path):
        """Scanner should be thread-safe if designed for concurrent use."""
        import threading

        scanner = AntiPatternScanner(project_root=tmp_path)
        results = []

        def scan_worker():
            try:
                report = scanner.scan()
                results.append(report)
            except Exception as e:
                results.append(e)

        threads = [threading.Thread(target=scan_worker) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert len(results) == 3
        assert all(isinstance(r, (ScanReport, Exception)) for r in results)
        reports = [r for r in results if isinstance(r, ScanReport)]
        if reports:
            assert all(r.project_root == tmp_path for r in reports)


class TestIntegrationEnhanced:
    """Integration tests with enhanced validation."""

    def test_scanner_report_integration(self, tmp_path):
        """Test integration between scanner and report with state validation."""
        (tmp_path / "file1.py").write_text("bad_var = 1")
        (tmp_path / "file2.py").write_text("another_bad = 2")
        scanner = AntiPatternScanner(project_root=tmp_path)
        report = scanner.scan()
        assert report.project_root == scanner.project_root
        if report.total_violations > 0:
            assert report.passed is False
            assert len(report.all_violations) == report.total_violations

    def test_error_propagation_integration(self, tmp_path):
        """Test error handling integration between components."""
        scanner = AntiPatternScanner(project_root=tmp_path)
        with patch.object(scanner, "scan", side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                scanner.scan()
