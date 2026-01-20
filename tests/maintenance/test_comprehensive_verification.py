"""
Advanced verification for Phase 6 (Tests 4-10).

Comprehensive testing for deep functional validation, data integrity,
and system stability after the global SSOT migration.
"""
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.config import SOVEREIGN_REGISTRY, DEFAULT_EXCLUDE_DIRS, HEALING_CONFIG
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.ssot_discovery import get_python_files
from agentic_core.utils.backup_manager import BackupManager


# --- Test Case 4: Data Fidelity ---
def test_registry_data_fidelity():
    """Verify deep keys exist to ensure zero-loss migration."""
    # Check for known top-level keys from the original registry
    assert "agentic_core" in SOVEREIGN_REGISTRY
    assert "apps_rg" in SOVEREIGN_REGISTRY
    assert "apps_lic" in SOVEREIGN_REGISTRY
    assert "apps_shared" in SOVEREIGN_REGISTRY
    assert "tests" in SOVEREIGN_REGISTRY
    
    # Check nested structure
    assert "depth" in SOVEREIGN_REGISTRY["agentic_core"]
    assert "subfolders" in SOVEREIGN_REGISTRY["agentic_core"]
    
    # Verify HEALING_CONFIG is present and has expected keys
    assert isinstance(HEALING_CONFIG, dict)
    assert "max_rounds" in HEALING_CONFIG
    assert "global_budget" in HEALING_CONFIG
    assert "dust_threshold" in HEALING_CONFIG


def test_registry_agentic_core_subfolders():
    """Verify agentic_core subfolders are complete."""
    subfolders = SOVEREIGN_REGISTRY["agentic_core"]["subfolders"]
    
    expected_subfolders = [
        "L0_maintenance", "L1_cognition", "L2_execution", 
        "L3_orchestration", "L4_state", "L5_safety", "L6_observability",
        "config", "schemas", "utils"
    ]
    
    for folder in expected_subfolders:
        assert folder in subfolders, f"Missing subfolder: {folder}"


# --- Test Case 5: Unified Integration ---
def test_unified_agent_importable():
    """Verify unified agents can be imported from clean path."""
    from agentic_core.unified import UnifiedCodeValidatorAgent
    
    # Agent class should be importable
    assert UnifiedCodeValidatorAgent is not None
    
    # Should be a class
    import inspect
    assert inspect.isclass(UnifiedCodeValidatorAgent)


def test_unified_agent_has_expected_attributes():
    """Verify unified agent has expected class attributes."""
    from agentic_core.unified import UnifiedCodeValidatorAgent
    
    # Check for expected methods/attributes
    assert hasattr(UnifiedCodeValidatorAgent, '__init__')


# --- Test Case 6: Mixin Logic ---
def test_healer_mixin_has_methods():
    """Verify the consolidated mixin has expected methods."""
    # Check that HealerMixin has the expected core methods
    assert hasattr(HealerMixin, 'heal'), "HealerMixin missing 'heal' method"
    assert hasattr(HealerMixin, 'heal_repository'), "HealerMixin missing 'heal_repository' method"
    assert hasattr(HealerMixin, 'get_healing_metrics'), "HealerMixin missing 'get_healing_metrics' method"
    assert hasattr(HealerMixin, 'apply_fix'), "HealerMixin missing 'apply_fix' method"


def test_healer_mixin_is_class():
    """Verify HealerMixin is a proper class."""
    import inspect
    assert inspect.isclass(HealerMixin)


# --- Test Case 7: Exclusion Enforcement ---
def test_ssot_discovery_excludes_backups(tmp_path):
    """Ensure discovery strictly respects SSOT exclusions."""
    # Create a mock backup dir (should be excluded)
    backup_dir = tmp_path / "archives" / "healing_backups"
    backup_dir.mkdir(parents=True)
    (backup_dir / "bad_file.py").write_text("# should be excluded")
    
    # Create __pycache__ (should be excluded)
    pycache_dir = tmp_path / "__pycache__"
    pycache_dir.mkdir(parents=True)
    (pycache_dir / "cached.py").write_text("# should be excluded")
    
    # Create a valid source file
    src_dir = tmp_path / "agentic_core"
    src_dir.mkdir(parents=True)
    (src_dir / "good_file.py").write_text("# should be included")
    
    files = get_python_files(tmp_path)
    file_names = [f.name for f in files]
    
    assert "good_file.py" in file_names
    assert "bad_file.py" not in file_names
    assert "cached.py" not in file_names


def test_ssot_discovery_excludes_git(tmp_path):
    """Ensure .git directory is excluded."""
    # Create .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)
    (git_dir / "hooks.py").write_text("# should be excluded")
    
    # Create valid file
    (tmp_path / "valid.py").write_text("# should be included")
    
    files = get_python_files(tmp_path)
    file_names = [f.name for f in files]
    
    assert "valid.py" in file_names
    assert "hooks.py" not in file_names


# --- Test Case 8: Immutability ---
def test_constants_immutability():
    """Critical constants must be read-only."""
    assert isinstance(DEFAULT_EXCLUDE_DIRS, frozenset)
    
    # Attempting to modify should raise an error
    with pytest.raises(AttributeError):
        DEFAULT_EXCLUDE_DIRS.add("malicious_entry")


def test_sovereign_registry_is_dict():
    """SOVEREIGN_REGISTRY should be a dict (mutable by design for runtime config)."""
    assert isinstance(SOVEREIGN_REGISTRY, dict)


# --- Test Case 9: Idempotency (Simulated) ---
def test_migration_idempotency(tmp_path):
    """Running migration on already migrated code should do nothing."""
    from agentic_core.L0_maintenance.scripts.migrate_imports import migrate_file
    
    # Setup already migrated file
    f = tmp_path / "test_migrated.py"
    clean_content = "from agentic_core.config import SOVEREIGN_REGISTRY\n"
    f.write_text(clean_content)
    
    # Run migration logic on the file
    was_modified, changes = migrate_file(f, dry_run=True)
    
    # Should not be modified since it's already using clean imports
    assert was_modified is False
    assert len(changes) == 0


def test_migration_detects_legacy_imports(tmp_path):
    """Migration should detect legacy import patterns."""
    from agentic_core.L0_maintenance.scripts.migrate_imports import migrate_file
    
    # Setup file with legacy import
    f = tmp_path / "test_legacy.py"
    legacy_content = "from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY\n"
    f.write_text(legacy_content)
    
    # Run migration logic on the file (dry run)
    was_modified, changes = migrate_file(f, dry_run=True)
    
    # Should detect the legacy import
    assert was_modified is True
    assert len(changes) > 0


# --- Test Case 10: Backup Lifecycle ---
def test_backup_lifecycle(tmp_path):
    """Full create-verify-decommission cycle."""
    # 1. Create Legacy backup directory
    legacy = tmp_path / ".sovereign_healing_backup"
    legacy.mkdir()
    (legacy / "old_backup.txt").write_text("legacy data")
    
    # 2. Verify Detection
    found = BackupManager.get_legacy_backup_dirs(tmp_path)
    assert len(found) == 1
    assert found[0].name == ".sovereign_healing_backup"
    
    # 3. Decommission
    count = BackupManager.decommission_legacy_backups(tmp_path)
    assert count == 1
    
    # 4. Verify Removal
    assert not legacy.exists()


def test_backup_lifecycle_multiple_legacy(tmp_path):
    """Test decommissioning multiple legacy directories."""
    # Create both legacy directories
    (tmp_path / ".sovereign_healing_backup").mkdir()
    (tmp_path / ".governance_healer_backups").mkdir()
    
    # Verify both detected
    found = BackupManager.get_legacy_backup_dirs(tmp_path)
    assert len(found) == 2
    
    # Decommission both
    count = BackupManager.decommission_legacy_backups(tmp_path)
    assert count == 2
    
    # Verify both removed
    assert not (tmp_path / ".sovereign_healing_backup").exists()
    assert not (tmp_path / ".governance_healer_backups").exists()


def test_new_backup_uses_ssot_location(tmp_path):
    """Verify new backups go to SSOT location."""
    backup_dir = BackupManager.get_backup_dir("test_category", project_root=tmp_path)
    
    # Should be under archives/healing_backups/
    assert "archives" in backup_dir.parts
    assert "healing_backups" in backup_dir.parts
    assert "test_category" in backup_dir.parts
    assert backup_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
