"""
Test: Void Violation Handling

Verifies that VOID VIOLATION is handled properly:
1. First option: Relocate to existing subfolder
2. Second option: Create new subfolder and update SSOT
3. Last resort: Archive (only with explicit user approval)

This test ensures archiving is NOT the default behavior for void violations.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest


def get_project_root() -> Path:
    """Get project root directory."""
    import os

    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"])

    known_root = Path("C:/Git/Agentic-Workflow")
    if known_root.exists() and (known_root / "agentic_core").is_dir():
        return known_root

    test_file = Path(__file__).resolve()
    return test_file.parent.parent.parent


class test_void_violation_handling:
    """Test suite for void violation handling."""

    @pytest.fixture
    def project_root(self) -> Path:
        return get_project_root()

    def test_healing_strategy_map_has_void_violation(self):
        """Verify VOID VIOLATION is in the healing strategy map."""
        from agentic_core.L5_safety.validators.location_constants import HEALING_STRATEGY_MAP

        assert "VOID VIOLATION" in HEALING_STRATEGY_MAP
        assert HEALING_STRATEGY_MAP["VOID VIOLATION"] == "_heal_void_violation"

    def test_location_healer_has_void_violation_method(self):
        """Verify LocationHealerAgent has _heal_void_violation method."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        assert hasattr(LocationHealerAgent, "_heal_void_violation")
        assert hasattr(LocationHealerAgent, "_relocate_to_existing_subfolder")
        assert hasattr(LocationHealerAgent, "_create_new_subfolder_and_update_ssot")

    def test_void_violation_dry_run_shows_options(self, project_root):
        """Verify dry run shows all options instead of archiving."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        healer = LocationHealerAgent(project_root=project_root)

        # Create a mock file path that would trigger void violation
        mock_file = project_root / "agentic_core" / "unknown_folder" / "test_file.py"

        result = healer._heal_void_violation(
            file_path=mock_file,
            msg="VOID VIOLATION: Path 'agentic_core/unknown_folder/test_file.py' not in sovereign territory",
            dry_run=True,
            affected_paths=[],
            import_touched_paths=[],
        )

        # Should show options, not archive
        assert result["applied"] == True
        assert "PREVIEW" in result["action_taken"]
        assert "options" in result
        assert "1_relocate" in result["options"]
        assert "2_create" in result["options"]
        assert "3_archive" in result["options"]

    def test_void_violation_not_default_archive(self):
        """Verify void violation does NOT default to archiving."""
        from agentic_core.L5_safety.validators.location_constants import HEALING_STRATEGY_MAP

        # VOID VIOLATION should have its own handler, not fall through to archiving
        assert "VOID VIOLATION" in HEALING_STRATEGY_MAP

        # The handler should be _heal_void_violation, not _heal_via_archiving
        assert HEALING_STRATEGY_MAP["VOID VIOLATION"] != "_heal_via_archiving"

    def test_apply_healing_strategy_routes_void_violation(self, project_root):
        """Verify _apply_healing_strategy routes VOID VIOLATION to correct handler."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        healer = LocationHealerAgent(project_root=project_root)

        # Mock the _heal_void_violation method
        healer._heal_void_violation = MagicMock(
            return_value={"applied": True, "action_taken": "MOCKED"}
        )

        mock_file = project_root / "agentic_core" / "unknown_folder" / "test_file.py"
        archives_root = project_root / "archives"

        result = healer._apply_healing_strategy(
            file_path=mock_file,
            msg="VOID VIOLATION: test",
            archives_root=archives_root,
            dry_run=True,
            affected_paths=[],
            import_touched_paths=[],
        )

        # Should have called _heal_void_violation, not _heal_via_archiving
        healer._heal_void_violation.assert_called_once()


class TestSSOTSubfolderUpdate:
    """Test SSOT subfolder update functionality."""

    @pytest.fixture
    def project_root(self) -> Path:
        return get_project_root()

    def test_sovereign_registry_has_agentic_core_subfolders(self):
        """Verify SOVEREIGN_REGISTRY has subfolders for agentic_core."""
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY

        assert "agentic_core" in SOVEREIGN_REGISTRY
        assert "subfolders" in SOVEREIGN_REGISTRY["agentic_core"]
        assert len(SOVEREIGN_REGISTRY["agentic_core"]["subfolders"]) > 0

    def test_is_path_allowed_checks_subfolders(self):
        """Verify is_path_allowed checks subfolder membership."""
        from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed

        # Valid path (L5_safety is in subfolders)
        assert is_path_allowed("agentic_core/L5_safety/validators/test.py") == True

        # Invalid path (random_folder is NOT in subfolders)
        assert is_path_allowed("agentic_core/random_nonexistent_folder/test.py") == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
