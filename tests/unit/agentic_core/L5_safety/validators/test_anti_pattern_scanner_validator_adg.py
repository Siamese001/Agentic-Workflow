"""ADG-driven tests for anti_pattern_scanner_validator."""

from __future__ import annotations

import pytest

_validator = pytest.importorskip(
    "agentic_core.L5_safety.validators.anti_pattern_scanner_validator",
    reason="Requires anti_pattern_scanner_validator from the monorepo checkout.",
)
_base = pytest.importorskip(
    "agentic_core.L5_safety.validators.base_detector_validator",
    reason="Requires base detector validator types from the monorepo checkout.",
)

AntiPatternScanner = _validator.AntiPatternScanner
ScanReport = _validator.ScanReport
AntiPatternCategory = _base.AntiPatternCategory
AntiPatternViolation = _base.AntiPatternViolation

pytestmark = pytest.mark.unit


class TestScanReport:
    def test_creates_with_valid_project_root(self, tmp_path):
        """ScanReport should create successfully with valid project root."""
        report = ScanReport(project_root=tmp_path)
        assert report.project_root == tmp_path
        assert report.total_files_scanned == 0
        assert report.total_violations == 0
        assert report.files_with_violations == 0
        assert report.scan_time_ms == 0.0
        assert report.all_violations == []
        assert report.violations_by_category == {}
        assert report.errors == []

    def test_summary_method_returns_string(self, tmp_path):
        """Summary method should return a formatted string."""
        report = ScanReport(project_root=tmp_path)
        summary = report.summary()
        assert isinstance(summary, str)
        assert "Anti-Pattern Scan Report" in summary
        assert "Project:" in summary
        assert "Files Scanned: 0" in summary

    def test_passed_property_true_when_no_violations(self, tmp_path):
        """Passed property should be True when no violations exist."""
        report = ScanReport(project_root=tmp_path)
        assert report.passed is True

    def test_passed_property_false_with_violations(self, tmp_path):
        """Passed property should be False when violations exist with state validation."""
        from agentic_core.L5_safety.validators.base_detector_validator import (
            AntiPatternCategory,
            AntiPatternViolation,
        )

        report = ScanReport(project_root=tmp_path)
        assert report.passed is True
        assert report.total_violations == 0
        assert len(report.all_violations) == 0
        violation = AntiPatternViolation(
            file_path=tmp_path / "test.py",
            line_number=1,
            category=AntiPatternCategory.SILENT_DEGRADATION,
            message="Test violation",
            evidence="test evidence",
        )
        report.all_violations.append(violation)
        report.total_violations = 1
        report.files_with_violations = 1
        assert report.passed is False
        assert report.total_violations == 1
        assert len(report.all_violations) == 1
        assert report.files_with_violations == 1
        assert violation in report.all_violations
        assert report.passed == (report.total_violations == 0)
        assert report.to_dict()["total_violations"] == 1


class TestAntiPatternScanner:
    def test_creates_with_default_settings(self, tmp_path):
        """AntiPatternScanner should create with default settings."""
        scanner = AntiPatternScanner(project_root=tmp_path)
        assert scanner.project_root == tmp_path
        assert scanner.enforcement_level.value == "warning"
        assert len(scanner.scan_dirs) > 0
        assert len(scanner.exclude_patterns) > 0
        assert scanner.composite is not None
        assert len(scanner.composite.detectors) > 0

    def test_scan_repository_returns_report(self, tmp_path):
        """Scan repository should return a ScanReport instance."""
        scanner = AntiPatternScanner(project_root=tmp_path)
        report = scanner.scan_repository()
        assert isinstance(report, ScanReport)
        assert report.project_root == tmp_path

    def test_scan_file_returns_violations_list(self, tmp_path):
        """Scan file should return list of violations with error handling."""
        test_file = tmp_path / "bad_code.py"
        test_file.write_text("# Bad naming pattern\nbad_var = 1\n")
        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(test_file)
        assert isinstance(violations, list)
        if violations:
            assert all(hasattr(v, "file_path") for v in violations)
            assert all(hasattr(v, "line_number") for v in violations)
            assert all(v.file_path == test_file for v in violations)
        non_existent = tmp_path / "does_not_exist.py"
        error_violations = scanner.scan_file(non_existent)
        assert isinstance(error_violations, list)
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("invalid python syntax {{{")
        error_violations = scanner.scan_file(invalid_file)
        assert isinstance(error_violations, list)
        assert len(violations) > 0
        assert all(hasattr(v, "category") for v in violations)

    def test_scan_changed_files_returns_report(self, tmp_path):
        """Scan changed files should return ScanReport for specified files."""
        file1 = tmp_path / "file1.py"
        file2 = tmp_path / "file2.py"
        file1.write_text("# Good code\nprint('hello')")
        file2.write_text("\ntry:\n    import missing_module\nexcept ImportError:\n    pass\n")
        scanner = AntiPatternScanner(project_root=tmp_path)
        report = scanner.scan_changed_files([file1, file2])
        assert isinstance(report, ScanReport)
        assert report.total_files_scanned == 2
        assert report.total_violations >= 1

    def test_get_enforcement_action(self, tmp_path):
        """Get enforcement action should return correct action string."""
        scanner = AntiPatternScanner(project_root=tmp_path)
        clean_report = ScanReport(project_root=tmp_path)
        action = scanner.get_enforcement_action(clean_report)
        assert action == "pass"
        report_with_violations = ScanReport(project_root=tmp_path)
        report_with_violations.total_violations = 1
        action = scanner.get_enforcement_action(report_with_violations)
        assert action == "warn"
