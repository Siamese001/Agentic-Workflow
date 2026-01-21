"""
Mandatory Verification for Phase 5 Legacy Cleanup.

Tests verify that:
- Legacy import patterns are being migrated
- Legacy backup directories can be identified and removed
- SSOT backup locations are used correctly
"""
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.backup_manager import BackupManager
from agentic_core.utils.ssot_discovery import get_python_files


def test_backup_manager_has_decommission_method():
    """Verify BackupManager has the decommission_legacy_backups method."""
    assert hasattr(BackupManager, 'decommission_legacy_backups')
    assert callable(getattr(BackupManager, 'decommission_legacy_backups'))


def test_backup_manager_has_get_legacy_dirs_method():
    """Verify BackupManager has the get_legacy_backup_dirs method."""
    assert hasattr(BackupManager, 'get_legacy_backup_dirs')
    assert callable(getattr(BackupManager, 'get_legacy_backup_dirs'))


def test_legacy_backup_detection(tmp_path):
    """Verify legacy backup directories are detected."""
    # Create fake legacy directories
    (tmp_path / ".sovereign_healing_backup").mkdir()
    (tmp_path / ".governance_healer_backups").mkdir()

    legacy_dirs = BackupManager.get_legacy_backup_dirs(project_root=tmp_path)

    assert len(legacy_dirs) == 2
    assert any(".sovereign_healing_backup" in str(d) for d in legacy_dirs)
    assert any(".governance_healer_backups" in str(d) for d in legacy_dirs)


def test_legacy_backup_removal(tmp_path):
    """Verify legacy backup directories are removed correctly."""
    # Create fake legacy directories
    (tmp_path / ".sovereign_healing_backup").mkdir()
    (tmp_path / ".governance_healer_backups").mkdir()

    # Verify they exist
    assert (tmp_path / ".sovereign_healing_backup").exists()
    assert (tmp_path / ".governance_healer_backups").exists()

    # Decommission them
    removed_count = BackupManager.decommission_legacy_backups(project_root=tmp_path)

    assert removed_count == 2
    assert not (tmp_path / ".sovereign_healing_backup").exists()
    assert not (tmp_path / ".governance_healer_backups").exists()


def test_no_legacy_dirs_returns_empty(tmp_path):
    """Verify empty list when no legacy directories exist."""
    legacy_dirs = BackupManager.get_legacy_backup_dirs(project_root=tmp_path)
    assert legacy_dirs == []


def test_decommission_returns_zero_when_none_exist(tmp_path):
    """Verify decommission returns 0 when no legacy dirs exist."""
    removed_count = BackupManager.decommission_legacy_backups(project_root=tmp_path)
    assert removed_count == 0


def test_ssot_backup_location_constant():
    """Verify SSOT backup location is correctly defined."""
    assert BackupManager.BACKUP_ROOT == Path("archives/healing_backups")


def test_new_backups_use_ssot_location(tmp_path):
    """Verify new backups are created in SSOT location."""
    backup_dir = BackupManager.get_backup_dir("test_category", project_root=tmp_path)

    # Should be under archives/healing_backups/
    assert "archives" in backup_dir.parts
    assert "healing_backups" in backup_dir.parts
    assert "test_category" in backup_dir.parts


def test_migrate_imports_script_exists():
    """Verify the migration script was created."""
    # Use importlib to verify the module is importable
    import importlib.util
    spec = importlib.util.find_spec("agentic_core.L0_maintenance.scripts.migrate_imports")
    assert spec is not None, "Migration script module not found"


def test_migrate_imports_has_migration_map():
    """Verify migration script has the MIGRATION_MAP defined."""
    from agentic_core.L0_maintenance.scripts.migrate_imports import MIGRATION_MAP

    assert isinstance(MIGRATION_MAP, dict)
    assert len(MIGRATION_MAP) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
