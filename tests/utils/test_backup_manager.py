"""
Pytest suite for BackupManager ensuring SSOT compliance.

Tests verify that:
- Directory structure matches SSOT: archives/healing_backups/<category>
- Timestamped subdirectories are created correctly
- Cleanup logic removes oldest directories
- File backup operations work correctly
"""
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.backup_manager import BackupManager


def test_get_backup_dir_structure(tmp_path):
    """Verify directory structure matches SSOT: archives/healing_backups/<category>"""
    # Act
    backup_dir = BackupManager.get_backup_dir(
        category="unit_test",
        project_root=tmp_path,
        timestamped=False
    )

    # Assert
    expected = tmp_path / "archives/healing_backups/unit_test"
    assert backup_dir == expected
    assert backup_dir.exists()


def test_get_backup_dir_timestamped(tmp_path):
    """Verify timestamped subdirectories are created."""
    # Act
    backup_dir = BackupManager.get_backup_dir(
        category="unit_test",
        project_root=tmp_path,
        timestamped=True
    )

    # Assert - use Path parts for cross-platform compatibility
    parts = backup_dir.parts
    assert "archives" in parts
    assert "healing_backups" in parts
    assert "unit_test" in parts
    assert backup_dir.name.startswith("20")  # Timestamp starts with year
    assert backup_dir.exists()


def test_cleanup_old_backups(tmp_path):
    """Verify cleanup logic removes oldest directories."""
    # Arrange: Create 5 backup directories
    for i in range(5):
        d = tmp_path / "archives/healing_backups/cleanup_test" / f"20260120_10000{i}"
        d.mkdir(parents=True)

    # Act: Keep only last 2
    removed = BackupManager.cleanup_old_backups(
        category="cleanup_test",
        keep_last_n=2,
        project_root=tmp_path
    )

    # Assert
    remaining = list((tmp_path / "archives/healing_backups/cleanup_test").iterdir())
    assert removed == 3
    assert len(remaining) == 2
    # Ensure 03 and 04 (the highest numbers) remain
    names = sorted([p.name for p in remaining])
    assert "20260120_100003" in names[0]
    assert "20260120_100004" in names[1]


def test_backup_file(tmp_path):
    """Verify single file backup works correctly."""
    # Arrange: Create a test file
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test content")

    # Act
    backup_path = BackupManager.backup_file(
        target_file=test_file,
        category="file_test",
        project_root=tmp_path
    )

    # Assert - use Path parts for cross-platform compatibility
    assert backup_path is not None
    assert backup_path.exists()
    assert backup_path.read_text() == "test content"
    parts = backup_path.parts
    assert "archives" in parts
    assert "healing_backups" in parts
    assert "file_test" in parts


def test_backup_file_nonexistent(tmp_path):
    """Verify backup returns None for nonexistent files."""
    # Act
    result = BackupManager.backup_file(
        target_file=tmp_path / "nonexistent.txt",
        category="file_test",
        project_root=tmp_path
    )

    # Assert
    assert result is None


def test_list_backups(tmp_path):
    """Verify listing backups returns correct order."""
    # Arrange: Create backup directories
    for i in range(3):
        d = tmp_path / "archives/healing_backups/list_test" / f"20260120_10000{i}"
        d.mkdir(parents=True)

    # Act
    backups = BackupManager.list_backups(
        category="list_test",
        project_root=tmp_path
    )

    # Assert
    assert len(backups) == 3
    # Should be sorted newest first
    assert backups[0].name == "20260120_100002"
    assert backups[2].name == "20260120_100000"


def test_list_backups_empty_category(tmp_path):
    """Verify listing nonexistent category returns empty list."""
    # Act
    backups = BackupManager.list_backups(
        category="nonexistent",
        project_root=tmp_path
    )

    # Assert
    assert backups == []


def test_restore_backup_file(tmp_path):
    """Verify file restoration works correctly."""
    # Arrange: Create backup and remove original
    original = tmp_path / "original.txt"
    original.write_text("original content")

    backup = BackupManager.backup_file(
        target_file=original,
        category="restore_test",
        project_root=tmp_path
    )
    original.unlink()

    # Act
    restored_path = tmp_path / "restored.txt"
    result = BackupManager.restore_backup(backup, restored_path)

    # Assert
    assert result is True
    assert restored_path.exists()
    assert restored_path.read_text() == "original content"


def test_backup_root_constant():
    """Verify BACKUP_ROOT constant matches SSOT specification."""
    assert BackupManager.BACKUP_ROOT == Path("archives/healing_backups")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
