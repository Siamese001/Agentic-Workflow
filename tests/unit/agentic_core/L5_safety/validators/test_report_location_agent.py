"""
Unit tests for ReportLocationAgent - Phase 4 SSOT Report Storage.

Tests cover:
- Agent initialization
- Validation functionality
- Healing operations
- Git integration
- Standard heal interface
- Inventory generation
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.Reportlocation_agent import (
    ReportLocationAgent,
    ReportLocationHealResult,
)


class TestReportLocationAgentInit:
    """Tests for ReportLocationAgent initialization."""

    def test_default_project_root_is_cwd(self) -> None:
        """Test that default project root is current working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                agent = ReportLocationAgent()
                assert agent.project_root == Path(tmpdir).resolve()
            finally:
                os.chdir(original_cwd)

    def test_custom_project_root(self) -> None:
        """Test that custom project root is used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            assert agent.project_root == Path(tmpdir).resolve()

    def test_dry_run_defaults_to_true(self) -> None:
        """Test that dry_run defaults to True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            assert agent.dry_run is True

    def test_dry_run_can_be_disabled(self) -> None:
        """Test that dry_run can be disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir), dry_run=False)
            assert agent.dry_run is False

    def test_agent_name_is_set(self) -> None:
        """Test that agent name is set correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            assert agent.agent_name == "ReportLocationAgent"

    def test_backup_dir_is_set(self) -> None:
        """Test that backup directory is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            assert ".sovereign_healing_backup" in str(agent.backup_dir)


class TestValidation:
    """Tests for validation functionality."""

    def test_validate_returns_dict(self) -> None:
        """Test that validate returns a dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            result = agent.validate()
            assert isinstance(result, dict)

    def test_validate_contains_required_keys(self) -> None:
        """Test that validate result contains required keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            result = agent.validate()

            assert "total_reports" in result
            assert "compliant_reports" in result
            assert "misplaced_reports" in result
            assert "compliance_percentage" in result
            assert "violations" in result
            assert "ssot_location" in result

    def test_validate_detects_misplaced_reports(self) -> None:
        """Test that validate detects misplaced reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "PHASE1_REPORT.md").write_text("Test")

            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["misplaced_reports"] == 1

    def test_validate_detects_compliant_reports(self) -> None:
        """Test that validate detects compliant reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)
            (docs_reports / "test_report.md").write_text("Test")

            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["compliant_reports"] == 1
            assert result["misplaced_reports"] == 0

    def test_get_violations_returns_list(self) -> None:
        """Test that get_violations returns a list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            violations = agent.get_violations()
            assert isinstance(violations, list)

    def test_get_inventory_returns_inventory(self) -> None:
        """Test that get_inventory returns ReportInventory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            inventory = agent.get_inventory()
            assert hasattr(inventory, "total_reports")
            assert hasattr(inventory, "compliance_percentage")


class TestHealing:
    """Tests for healing operations."""

    def test_heal_returns_result(self) -> None:
        """Test that heal returns ReportLocationHealResult."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            result = agent.heal()
            assert isinstance(result, ReportLocationHealResult)

    def test_heal_dry_run_does_not_move_files(self) -> None:
        """Test that heal in dry_run mode does not move files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            source = project_root / "test_report.md"
            source.write_text("Test")

            agent = ReportLocationAgent(project_root=project_root, dry_run=True)
            agent.heal()

            assert source.exists()

    def test_heal_moves_files_when_not_dry_run(self) -> None:
        """Test that heal moves files when dry_run is False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "test_report.md"
            source.write_text("Test content")

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            result = agent.heal()

            assert not source.exists()
            assert (docs_reports / "test_report.md").exists()
            assert result.healed_count == 1

    def test_heal_respects_limit(self) -> None:
        """Test that heal respects the limit parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            for i in range(5):
                (project_root / f"report_{i}.md").write_text(f"Report {i}")

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            result = agent.heal(limit=2)

            assert result.total_violations == 2

    def test_heal_creates_backup(self) -> None:
        """Test that heal creates backup before moving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "test_report.md"
            source.write_text("Test content")

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            agent.heal()

            backup_dir = project_root / ".sovereign_healing_backup" / "reports"
            assert backup_dir.exists()

    def test_heal_skips_existing_destination(self) -> None:
        """Test that heal skips if destination already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create both source and destination
            source = project_root / "test_report.md"
            source.write_text("Source content")
            (docs_reports / "test_report.md").write_text("Existing content")

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            result = agent.heal()

            assert result.skipped_count == 1
            assert source.exists()  # Source should still exist


class TestHealFile:
    """Tests for individual file healing."""

    def test_heal_file_dry_run(self) -> None:
        """Test heal_file in dry_run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            source = project_root / "test_report.md"
            source.write_text("Test")

            agent = ReportLocationAgent(project_root=project_root, dry_run=True)
            violations = agent.get_violations()

            if violations:
                result = agent.heal_file(violations[0])
                assert result["status"] == "dry_run"

    def test_heal_file_success(self) -> None:
        """Test successful file healing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "test_report.md"
            source.write_text("Test")

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            violations = agent.get_violations()

            if violations:
                result = agent.heal_file(violations[0])
                assert result["status"] == "healed"


class TestStandardHealInterface:
    """Tests for standard heal interface."""

    def test_standard_heal_returns_dict(self) -> None:
        """Test that standard_heal returns a dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            result = agent.standard_heal()
            assert isinstance(result, dict)

    def test_standard_heal_contains_required_keys(self) -> None:
        """Test that standard_heal result contains required keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            result = agent.standard_heal()

            assert "violations_found" in result
            assert "violations_fixed" in result
            assert "errors" in result
            assert "skipped" in result

    def test_standard_heal_counts_violations(self) -> None:
        """Test that standard_heal correctly counts violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "test_report.md").write_text("Test")

            agent = ReportLocationAgent(project_root=project_root, dry_run=True)
            result = agent.standard_heal()

            assert result["violations_found"] == 1


class TestGitIntegration:
    """Tests for git integration."""

    def test_is_git_tracked_returns_false_for_untracked(self) -> None:
        """Test that is_git_tracked returns False for untracked files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            untracked = project_root / "untracked.md"
            untracked.touch()

            agent = ReportLocationAgent(project_root=project_root)
            assert agent.is_git_tracked(untracked) is False

    @patch("subprocess.run")
    def test_git_move_calls_git_mv(self, mock_run: MagicMock) -> None:
        """Test that git_move calls git mv."""
        mock_run.return_value = MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            agent = ReportLocationAgent(project_root=project_root)

            source = project_root / "source.md"
            dest = project_root / "docs" / "reports" / "source.md"

            agent.git_move(source, dest)

            mock_run.assert_called()


class TestBackup:
    """Tests for backup functionality."""

    def test_backup_file_creates_backup(self) -> None:
        """Test that backup_file creates a backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            source = project_root / "test_report.md"
            source.write_text("Test content")

            agent = ReportLocationAgent(project_root=project_root)
            backup_path = agent.backup_file(source)

            assert backup_path is not None
            assert backup_path.exists()

    def test_backup_file_preserves_content(self) -> None:
        """Test that backup preserves file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            source = project_root / "test_report.md"
            content = "Important content"
            source.write_text(content)

            agent = ReportLocationAgent(project_root=project_root)
            backup_path = agent.backup_file(source)

            assert backup_path.read_text() == content


class TestSaveInventory:
    """Tests for inventory saving."""

    def test_save_inventory_creates_file(self) -> None:
        """Test that save_inventory creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            agent = ReportLocationAgent(project_root=project_root)
            output_path = agent.save_inventory()

            assert output_path.exists()

    def test_save_inventory_contains_valid_json(self) -> None:
        """Test that saved inventory contains valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            agent = ReportLocationAgent(project_root=project_root)
            output_path = agent.save_inventory()

            with open(output_path) as f:
                data = json.load(f)

            assert "timestamp" in data
            assert "total_reports" in data


class TestReportLocationHealResult:
    """Tests for ReportLocationHealResult dataclass."""

    def test_default_values(self) -> None:
        """Test default values of ReportLocationHealResult."""
        result = ReportLocationHealResult()

        assert result.total_violations == 0
        assert result.healed_count == 0
        assert result.failed_count == 0
        assert result.skipped_count == 0
        assert result.healed_files == []
        assert result.failed_files == []
        assert result.timestamp is not None

    def test_custom_values(self) -> None:
        """Test custom values of ReportLocationHealResult."""
        result = ReportLocationHealResult(
            total_violations=5,
            healed_count=3,
            failed_count=1,
            skipped_count=1,
        )

        assert result.total_violations == 5
        assert result.healed_count == 3
        assert result.failed_count == 1
        assert result.skipped_count == 1


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_project(self) -> None:
        """Test handling of empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReportLocationAgent(project_root=Path(tmpdir))
            result = agent.validate()

            assert result["total_reports"] == 0
            assert result["compliance_percentage"] == 0.0

    def test_all_compliant_project(self) -> None:
        """Test handling of fully compliant project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "report1.md").write_text("Report 1")
            (docs_reports / "report2.md").write_text("Report 2")

            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["compliance_percentage"] == 100.0
            assert result["misplaced_reports"] == 0
