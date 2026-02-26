"""
Unit tests for ReportLocationValidator - Phase 1 SSOT Report Storage.

Tests cover:
- Report file pattern matching
- Location validation
- Inventory generation
- Compliance checking
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

# from agentic_core.utils.report_location_validator_types_util import (
#     APPROVED_REPORT_LOCATIONS,
#     REPORT_FILE_PATTERNS,
#     SSOT_REPORTS_DIR,
#     ReportInventory,
#     ReportLocationValidator,
#     generate_report_inventory,
#     get_misplaced_reports,
#     validate_report_location,
# )


class TestReportFilePatternMatching:
    """Tests for report file pattern matching."""

    def test_matches_report_md_files(self) -> None:
        """Test that *report*.md files are matched."""
        validator = ReportLocationValidator()

        assert validator.is_report_file(Path("NUCLEAR_AUDIT_REPORT.md"))
        assert validator.is_report_file(Path("compliance_report.md"))
        assert validator.is_report_file(Path("Report_2026.md"))

    def test_matches_rca_files(self) -> None:
        """Test that RCA*.md files are matched."""
        validator = ReportLocationValidator()

        assert validator.is_report_file(Path("RCA_pre_commit_process.md"))
        assert validator.is_report_file(Path("RCA_HIERARCHY_AGENT_GAPS.md"))

    def test_matches_phase_files(self) -> None:
        """Test that PHASE*.md files are matched."""
        validator = ReportLocationValidator()

        assert validator.is_report_file(Path("PHASE1_OPTIMIZATION_SUMMARY.md"))
        assert validator.is_report_file(Path("PHASE12_FINAL_COMPLIANCE_REPORT.json"))

    def test_matches_summary_files(self) -> None:
        """Test that *_SUMMARY.md files are matched."""
        validator = ReportLocationValidator()

        assert validator.is_report_file(Path("OPTIMIZATION_SUMMARY.md"))
        assert validator.is_report_file(Path("PHASE6_FINAL_STATUS.md"))

    def test_matches_analysis_files(self) -> None:
        """Test that *_ANALYSIS.md files are matched."""
        validator = ReportLocationValidator()

        assert validator.is_report_file(Path("CORE_REFINERY_ANALYSIS.md"))
        assert validator.is_report_file(Path("K_NODE_EVOLUTION_ANALYSIS.md"))

    def test_matches_audit_files(self) -> None:
        """Test that *_AUDIT*.md files are matched."""
        validator = ReportLocationValidator()

        assert validator.is_report_file(Path("NUCLEAR_AUDIT_REPORT.md"))
        assert validator.is_report_file(Path("RG_SOVEREIGN_AUDIT_REPORT.md"))

    def test_does_not_match_non_report_files(self) -> None:
        """Test that non-report files are not matched."""
        validator = ReportLocationValidator()

        assert not validator.is_report_file(Path("main.py"))
        assert not validator.is_report_file(Path("README.md"))
        assert not validator.is_report_file(Path("config.yaml"))
        assert not validator.is_report_file(Path("test_something.py"))

    def test_matches_json_reports(self) -> None:
        """Test that *report*.json files are matched."""
        validator = ReportLocationValidator()

        assert validator.is_report_file(Path("compliance_report.json"))
        assert validator.is_report_file(Path("sovereign_contract_report.json"))


class TestLocationValidation:
    """Tests for location validation logic."""

    def test_docs_reports_is_approved(self) -> None:
        """Test that docs/reports/ is an approved location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            report_file = docs_reports / "test_report.md"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            assert validator.is_approved_location(report_file)

    def test_docs_reports_mcp_is_approved(self) -> None:
        """Test that docs/reports/MCP/ is an approved location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            mcp_dir = project_root / "docs" / "reports" / "MCP"
            mcp_dir.mkdir(parents=True)

            report_file = mcp_dir / "mcp_report.md"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            assert validator.is_approved_location(report_file)

    def test_project_root_is_not_approved(self) -> None:
        """Test that project root is not an approved location for reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            report_file = project_root / "PHASE1_REPORT.md"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            assert not validator.is_approved_location(report_file)

    def test_random_directory_is_not_approved(self) -> None:
        """Test that random directories are not approved locations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            random_dir = project_root / "some" / "random" / "dir"
            random_dir.mkdir(parents=True)

            report_file = random_dir / "report.md"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            assert not validator.is_approved_location(report_file)

    def test_logs_compliance_reports_is_approved(self) -> None:
        """Test that logs/compliance_reports/ is an approved location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            compliance_dir = project_root / "logs" / "compliance_reports"
            compliance_dir.mkdir(parents=True)

            report_file = compliance_dir / "compliance_report.json"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            assert validator.is_approved_location(report_file)


class TestExcludedDirectories:
    """Tests for excluded directory handling."""

    def test_git_directory_is_excluded(self) -> None:
        """Test that .git directory is excluded."""
        validator = ReportLocationValidator()
        assert validator.is_excluded_directory(Path(".git/objects/report.md"))

    def test_pycache_is_excluded(self) -> None:
        """Test that __pycache__ is excluded."""
        validator = ReportLocationValidator()
        assert validator.is_excluded_directory(Path("src/__pycache__/report.md"))

    def test_sovereign_healing_backup_is_excluded(self) -> None:
        """Test that .sovereign_healing_backup is excluded."""
        validator = ReportLocationValidator()
        assert validator.is_excluded_directory(Path(".sovereign_healing_backup/report.md"))

    def test_archives_is_excluded(self) -> None:
        """Test that archives directory is excluded."""
        validator = ReportLocationValidator()
        assert validator.is_excluded_directory(Path("archives/old_report.md"))

    def test_normal_directory_is_not_excluded(self) -> None:
        """Test that normal directories are not excluded."""
        validator = ReportLocationValidator()
        assert not validator.is_excluded_directory(Path("docs/reports/report.md"))
        assert not validator.is_excluded_directory(Path("src/module/file.py"))


class TestValidateFile:
    """Tests for single file validation."""

    def test_compliant_file_returns_compliant_result(self) -> None:
        """Test that compliant files return compliant results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            report_file = docs_reports / "test_report.md"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            result = validator.validate_file(report_file)

            assert result.is_compliant
            assert result.violation_type is None

    def test_misplaced_file_returns_violation(self) -> None:
        """Test that misplaced files return violation results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            report_file = project_root / "PHASE1_REPORT.md"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            result = validator.validate_file(report_file)

            assert not result.is_compliant
            assert result.violation_type == "misplaced_report"
            assert SSOT_REPORTS_DIR in result.expected_location

    def test_suggested_action_is_provided(self) -> None:
        """Test that suggested action is provided for violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            report_file = project_root / "test_report.md"
            report_file.touch()

            validator = ReportLocationValidator(project_root)
            result = validator.validate_file(report_file)

            assert result.suggested_action is not None
            assert "Move to" in result.suggested_action


class TestInventoryGeneration:
    """Tests for inventory generation."""

    def test_empty_project_returns_empty_inventory(self) -> None:
        """Test that empty project returns empty inventory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            validator = ReportLocationValidator(project_root)
            inventory = validator.generate_inventory()

            assert inventory.total_reports == 0
            assert inventory.compliant_reports == 0
            assert inventory.misplaced_reports == 0

    def test_inventory_counts_compliant_reports(self) -> None:
        """Test that inventory correctly counts compliant reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "report1.md").write_text("Report 1")
            (docs_reports / "report2.md").write_text("Report 2")

            validator = ReportLocationValidator(project_root)
            inventory = validator.generate_inventory()

            assert inventory.total_reports == 2
            assert inventory.compliant_reports == 2
            assert inventory.misplaced_reports == 0
            assert inventory.compliance_percentage == 100.0

    def test_inventory_counts_misplaced_reports(self) -> None:
        """Test that inventory correctly counts misplaced reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            (project_root / "PHASE1_REPORT.md").write_text("Phase 1")
            (project_root / "RCA_test.md").write_text("RCA")

            validator = ReportLocationValidator(project_root)
            inventory = validator.generate_inventory()

            assert inventory.total_reports == 2
            assert inventory.compliant_reports == 0
            assert inventory.misplaced_reports == 2
            assert inventory.compliance_percentage == 0.0

    def test_inventory_calculates_compliance_percentage(self) -> None:
        """Test that compliance percentage is calculated correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "compliant_report.md").write_text("Compliant")
            (project_root / "misplaced_report.md").write_text("Misplaced")

            validator = ReportLocationValidator(project_root)
            inventory = validator.generate_inventory()

            assert inventory.total_reports == 2
            assert inventory.compliant_reports == 1
            assert inventory.misplaced_reports == 1
            assert inventory.compliance_percentage == 50.0

    def test_inventory_groups_by_location(self) -> None:
        """Test that inventory groups reports by location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "report1.md").write_text("Report 1")
            (project_root / "root_report.md").write_text("Root")

            validator = ReportLocationValidator(project_root)
            inventory = validator.generate_inventory()

            assert "docs/reports" in inventory.reports_by_location
            assert "." in inventory.reports_by_location


class TestSaveInventory:
    """Tests for saving inventory to file."""

    def test_save_inventory_creates_file(self) -> None:
        """Test that save_inventory creates a JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            validator = ReportLocationValidator(project_root)
            output_path = validator.save_inventory()

            assert output_path.exists()
            assert output_path.suffix == ".json"

    def test_save_inventory_contains_valid_json(self) -> None:
        """Test that saved inventory contains valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "test_report.md").write_text("Test")

            validator = ReportLocationValidator(project_root)
            output_path = validator.save_inventory()

            with open(output_path) as f:
                data = json.load(f)

            assert "timestamp" in data
            assert "total_reports" in data
            assert "compliance_percentage" in data

    def test_save_inventory_custom_path(self) -> None:
        """Test that save_inventory respects custom output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            custom_path = project_root / "custom" / "inventory.json"

            validator = ReportLocationValidator(project_root)
            output_path = validator.save_inventory(custom_path)

            assert output_path == custom_path
            assert output_path.exists()


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_validate_report_location_function(self) -> None:
        """Test the validate_report_location convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            compliant_file = docs_reports / "report.md"
            compliant_file.touch()

            misplaced_file = project_root / "report.md"
            misplaced_file.touch()

            assert validate_report_location(compliant_file, project_root)
            assert not validate_report_location(misplaced_file, project_root)

    def test_get_misplaced_reports_function(self) -> None:
        """Test the get_misplaced_reports convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            (project_root / "misplaced_report.md").write_text("Misplaced")

            misplaced = get_misplaced_reports(project_root)

            assert len(misplaced) == 1
            assert not misplaced[0].is_compliant

    def test_generate_report_inventory_function(self) -> None:
        """Test the generate_report_inventory convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "report.md").write_text("Report")

            inventory = generate_report_inventory(project_root)

            assert isinstance(inventory, ReportInventory)
            assert inventory.total_reports == 1


class TestConstants:
    """Tests for module constants."""

    def test_ssot_reports_dir_is_docs_reports(self) -> None:
        """Test that SSOT_REPORTS_DIR is docs/reports."""
        assert SSOT_REPORTS_DIR == "docs/reports"

    def test_approved_locations_include_docs_reports(self) -> None:
        """Test that approved locations include docs/reports."""
        assert "docs/reports" in APPROVED_REPORT_LOCATIONS

    def test_report_patterns_are_valid_regex(self) -> None:
        """Test that all report patterns are valid regex."""
        import re

        for pattern in REPORT_FILE_PATTERNS:
            # Should not raise
            re.compile(pattern)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_handles_nonexistent_project_root(self) -> None:
        """Test handling of nonexistent project root."""
        nonexistent = Path("/nonexistent/path/that/does/not/exist")

        validator = ReportLocationValidator(nonexistent)
        reports = validator.find_all_reports()

        assert reports == []

    def test_handles_file_outside_project_root(self) -> None:
        """Test handling of files outside project root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            outside_file = Path("/tmp/outside_report.md")

            validator = ReportLocationValidator(project_root)
            result = validator.validate_file(outside_file)

            # Should not crash, should return non-compliant
            assert not result.is_compliant

    def test_handles_empty_filename(self) -> None:
        """Test handling of edge case filenames."""
        validator = ReportLocationValidator()

        # Should not crash
        assert not validator.is_report_file(Path(""))
        assert not validator.is_report_file(Path("."))
