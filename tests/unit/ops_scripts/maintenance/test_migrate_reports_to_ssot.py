"""
Unit tests for Report Migration Script - Phase 2 SSOT Report Storage.

Tests cover:
- Migration entry and manifest creation
- Git-aware moves
- Dry-run mode
- Pilot migrations
- Rollback capability
- Backup creation
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


import sys

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from ops_scripts.maintenance.migrate_reports_to_ssot import (
    MigrationEntry,
    MigrationManifest,
    ReportMigrator,
)


class TestMigrationEntry:
    """Tests for MigrationEntry dataclass."""

    def test_default_status_is_pending(self) -> None:
        """Test that default status is pending."""
        entry = MigrationEntry(
            source="test.md",
            destination="docs/reports/test.md",
            timestamp="2026-02-01T12:00:00",
        )
        assert entry.status == "pending"

    def test_error_is_none_by_default(self) -> None:
        """Test that error is None by default."""
        entry = MigrationEntry(
            source="test.md",
            destination="docs/reports/test.md",
            timestamp="2026-02-01T12:00:00",
        )
        assert entry.error is None

    def test_git_tracked_is_false_by_default(self) -> None:
        """Test that git_tracked is False by default."""
        entry = MigrationEntry(
            source="test.md",
            destination="docs/reports/test.md",
            timestamp="2026-02-01T12:00:00",
        )
        assert entry.git_tracked is False


class TestMigrationManifest:
    """Tests for MigrationManifest dataclass."""

    def test_id_is_auto_generated(self) -> None:
        """Test that ID is auto-generated."""
        manifest = MigrationManifest()
        assert manifest.id is not None
        assert len(manifest.id) > 0

    def test_timestamp_is_auto_generated(self) -> None:
        """Test that timestamp is auto-generated."""
        manifest = MigrationManifest()
        assert manifest.timestamp is not None

    def test_counters_start_at_zero(self) -> None:
        """Test that counters start at zero."""
        manifest = MigrationManifest()
        assert manifest.total_files == 0
        assert manifest.migrated_files == 0
        assert manifest.failed_files == 0
        assert manifest.skipped_files == 0

    def test_entries_is_empty_list(self) -> None:
        """Test that entries is an empty list."""
        manifest = MigrationManifest()
        assert manifest.entries == []

    def test_rollback_available_is_true(self) -> None:
        """Test that rollback is available by default."""
        manifest = MigrationManifest()
        assert manifest.rollback_available is True


class TestReportMigratorInit:
    """Tests for ReportMigrator initialization."""

    def test_default_dry_run_is_false(self) -> None:
        """Test that dry_run defaults to False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            migrator = ReportMigrator(Path(tmpdir))
            assert migrator.dry_run is False

    def test_dry_run_can_be_enabled(self) -> None:
        """Test that dry_run can be enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            migrator = ReportMigrator(Path(tmpdir), dry_run=True)
            assert migrator.dry_run is True

    def test_pilot_count_is_none_by_default(self) -> None:
        """Test that pilot_count is None by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            migrator = ReportMigrator(Path(tmpdir))
            assert migrator.pilot_count is None

    def test_pilot_count_can_be_set(self) -> None:
        """Test that pilot_count can be set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            migrator = ReportMigrator(Path(tmpdir), pilot_count=5)
            assert migrator.pilot_count == 5


class TestGetDestinationPath:
    """Tests for destination path calculation."""

    def test_destination_is_in_docs_reports(self) -> None:
        """Test that destination is in docs/reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root)

            source = project_root / "PHASE1_REPORT.md"
            dest = migrator.get_destination_path(source)

            assert "docs/reports" in str(dest).replace("\\", "/")

    def test_destination_preserves_filename(self) -> None:
        """Test that destination preserves the filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root)

            source = project_root / "subdir" / "my_report.md"
            dest = migrator.get_destination_path(source)

            assert dest.name == "my_report.md"


class TestBackupFile:
    """Tests for backup creation."""

    def test_backup_creates_file(self) -> None:
        """Test that backup creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root)

            source = project_root / "test_report.md"
            source.write_text("Test content")

            backup_path = migrator.backup_file(source)

            assert backup_path is not None
            assert backup_path.exists()

    def test_backup_preserves_content(self) -> None:
        """Test that backup preserves file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root)

            source = project_root / "test_report.md"
            content = "Original content here"
            source.write_text(content)

            backup_path = migrator.backup_file(source)

            assert backup_path.read_text() == content

    def test_backup_in_sovereign_healing_backup(self) -> None:
        """Test that backup is in .sovereign_healing_backup directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root)

            source = project_root / "test_report.md"
            source.write_text("Test")

            backup_path = migrator.backup_file(source)

            assert ".sovereign_healing_backup" in str(backup_path)


class TestMigrateFileDryRun:
    """Tests for dry-run migration."""

    def test_dry_run_does_not_move_file(self) -> None:
        """Test that dry-run does not move the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root, dry_run=True)

            source = project_root / "test_report.md"
            source.write_text("Test")

            entry = migrator.migrate_file(source)

            assert source.exists()
            assert entry.status == "dry_run"

    def test_dry_run_returns_correct_destination(self) -> None:
        """Test that dry-run returns correct destination."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root, dry_run=True)

            source = project_root / "test_report.md"
            source.write_text("Test")

            entry = migrator.migrate_file(source)

            assert "docs/reports" in entry.destination.replace("\\", "/")


class TestMigrateFileLive:
    """Tests for live migration."""

    def test_live_migration_moves_file(self) -> None:
        """Test that live migration moves the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            migrator = ReportMigrator(project_root, dry_run=False)

            source = project_root / "test_report.md"
            source.write_text("Test content")

            entry = migrator.migrate_file(source)

            assert entry.status == "migrated"
            assert not source.exists()

            dest = project_root / entry.destination
            assert dest.exists()

    def test_live_migration_preserves_content(self) -> None:
        """Test that live migration preserves content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            migrator = ReportMigrator(project_root, dry_run=False)

            source = project_root / "test_report.md"
            content = "Important report content"
            source.write_text(content)

            entry = migrator.migrate_file(source)

            dest = project_root / entry.destination
            assert dest.read_text() == content

    def test_skips_if_destination_exists(self) -> None:
        """Test that migration skips if destination exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create destination file first
            (docs_reports / "test_report.md").write_text("Existing")

            migrator = ReportMigrator(project_root, dry_run=False)

            source = project_root / "test_report.md"
            source.write_text("New content")

            entry = migrator.migrate_file(source)

            assert entry.status == "skipped"
            assert source.exists()  # Source should still exist


class TestRunMigration:
    """Tests for full migration run."""

    def test_migration_respects_pilot_count(self) -> None:
        """Test that migration respects pilot count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create multiple misplaced reports
            for i in range(5):
                (project_root / f"report_{i}.md").write_text(f"Report {i}")

            migrator = ReportMigrator(project_root, dry_run=True, pilot_count=2)
            manifest = migrator.run_migration()

            assert manifest.total_files == 2

    def test_migration_creates_manifest(self) -> None:
        """Test that migration creates a manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (project_root / "test_report.md").write_text("Test")

            migrator = ReportMigrator(project_root, dry_run=False)
            manifest = migrator.run_migration()

            assert manifest is not None
            assert manifest.total_files == 1


class TestSaveAndLoadManifest:
    """Tests for manifest persistence."""

    def test_save_manifest_creates_file(self) -> None:
        """Test that save_manifest creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            migrator = ReportMigrator(project_root)
            migrator.manifest = MigrationManifest()

            path = migrator.save_manifest()

            assert path.exists()

    def test_save_manifest_contains_valid_json(self) -> None:
        """Test that saved manifest contains valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            migrator = ReportMigrator(project_root)
            migrator.manifest = MigrationManifest()
            migrator.manifest.entries.append(
                MigrationEntry(
                    source="test.md",
                    destination="docs/reports/test.md",
                    timestamp="2026-02-01T12:00:00",
                    status="migrated",
                )
            )

            path = migrator.save_manifest()

            with open(path) as f:
                data = json.load(f)

            assert "entries" in data
            assert len(data["entries"]) == 1

    def test_load_manifest_restores_data(self) -> None:
        """Test that load_manifest restores data correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            migrator = ReportMigrator(project_root)
            migrator.manifest = MigrationManifest()
            migrator.manifest.total_files = 5
            migrator.manifest.migrated_files = 3

            path = migrator.save_manifest()

            loaded = migrator.load_manifest(path)

            assert loaded.total_files == 5
            assert loaded.migrated_files == 3


class TestRollback:
    """Tests for rollback functionality."""

    def test_rollback_restores_files(self) -> None:
        """Test that rollback restores files to original location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create and migrate a file
            source = project_root / "test_report.md"
            source.write_text("Test content")

            migrator = ReportMigrator(project_root, dry_run=False)
            migrator.run_migration()

            # Verify file was moved
            assert not source.exists()
            assert (docs_reports / "test_report.md").exists()

            # Rollback
            manifest_path = migrator.get_manifest_path()
            success = migrator.rollback(manifest_path)

            assert success
            assert source.exists()

    def test_rollback_marks_manifest_as_used(self) -> None:
        """Test that rollback marks manifest as used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "test_report.md"
            source.write_text("Test")

            migrator = ReportMigrator(project_root, dry_run=False)
            migrator.run_migration()

            manifest_path = migrator.get_manifest_path()
            migrator.rollback(manifest_path)

            # Load manifest and check rollback_available
            with open(manifest_path) as f:
                data = json.load(f)

            assert data["rollback_available"] is False

    def test_rollback_fails_if_no_manifests(self) -> None:
        """Test that rollback fails if no manifests exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            migrator = ReportMigrator(project_root)
            success = migrator.rollback()

            assert success is False


class TestGitIntegration:
    """Tests for git integration (mocked)."""

    def test_is_git_tracked_returns_false_for_untracked(self) -> None:
        """Test that is_git_tracked returns False for untracked files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root)

            untracked = project_root / "untracked.md"
            untracked.touch()

            # Not a git repo, so should return False
            assert migrator.is_git_tracked(untracked) is False

    @patch("subprocess.run")
    def test_git_move_calls_git_mv(self, mock_run: MagicMock) -> None:
        """Test that git_move calls git mv."""
        mock_run.return_value = MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            migrator = ReportMigrator(project_root)

            source = project_root / "source.md"
            dest = project_root / "docs" / "reports" / "source.md"

            migrator.git_move(source, dest)

            mock_run.assert_called()
            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "mv" in call_args


class TestEdgeCases:
    """Tests for edge cases."""

    def test_handles_empty_project(self) -> None:
        """Test handling of empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            migrator = ReportMigrator(project_root, dry_run=True)
            manifest = migrator.run_migration()

            assert manifest.total_files == 0

    def test_handles_special_characters_in_filename(self) -> None:
        """Test handling of special characters in filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "report_with_spaces and (parens).md"
            source.write_text("Test")

            migrator = ReportMigrator(project_root, dry_run=False)
            entry = migrator.migrate_file(source)

            assert entry.status == "migrated"

    def test_creates_destination_directory(self) -> None:
        """Test that destination directory is created if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            # Don't create docs/reports

            source = project_root / "test_report.md"
            source.write_text("Test")

            migrator = ReportMigrator(project_root, dry_run=False)
            entry = migrator.migrate_file(source)

            assert entry.status == "migrated"
            assert (project_root / "docs" / "reports").exists()
