#!/usr/bin/env python3
"""
Test Suite: Archiving Authority Transfer

Verifies that LocationHealerAgent, HierarchyAgent, and FilesystemSSOTReconcilerAgent
use ArchivalGatekeeper for all file operations instead of raw shutil/unlink calls.

REQUIREMENTS:
1. All agents must have a `gatekeeper` attribute (ArchivalGatekeeper instance)
2. safe_move/safe_delete methods must call gatekeeper methods
3. No direct shutil.move, path.unlink(), or path.rename() for tracked files
"""

import inspect
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))


class TestLocationHealerAgentAuthority:
    """Test LocationHealerAgent uses ArchivalGatekeeper."""

    @pytest.fixture
    def mock_gatekeeper(self):
        """Create a mock ArchivalGatekeeper."""
        mock = MagicMock()
        mock.safe_move.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/dest"), error=None
        )
        mock.safe_delete.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/archive"), error=None
        )
        mock.safe_archive.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/archive"), error=None
        )
        return mock

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    def test_has_gatekeeper_attribute(self, temp_project, mock_gatekeeper):
        """Test LocationHealerAgent initializes with gatekeeper."""
        with patch(
            "agentic_core.L5_safety.core.ArchivalGatekeeper.ArchivalGatekeeper.get_instance",
            return_value=mock_gatekeeper,
        ):
            from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

            agent = LocationHealerAgent(project_root=temp_project)

            assert hasattr(agent, "gatekeeper"), (
                "LocationHealerAgent must have gatekeeper attribute"
            )
            assert hasattr(agent, "agent_name"), (
                "LocationHealerAgent must have agent_name attribute"
            )

    def test_safe_move_uses_gatekeeper(self, temp_project, mock_gatekeeper):
        """Test safe_move calls gatekeeper.safe_move."""
        with patch(
            "agentic_core.L5_safety.core.ArchivalGatekeeper.ArchivalGatekeeper.get_instance",
            return_value=mock_gatekeeper,
        ):
            from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

            agent = LocationHealerAgent(project_root=temp_project)

            # Create test file
            src = temp_project / "test_file.py"
            src.write_text("# test")
            dst = temp_project / "agentic_core" / "test_file.py"

            # Execute move (not dry run)
            result = agent.safe_move(src, dst, dry_run=False)

            # Verify gatekeeper was called
            mock_gatekeeper.safe_move.assert_called_once()
            call_args = mock_gatekeeper.safe_move.call_args
            assert call_args[0][0] == src, "Source path should be passed to gatekeeper"
            assert "LocationHealerAgent" in str(call_args[0][2]), "Agent name should be passed"

    def test_safe_delete_uses_gatekeeper(self, temp_project, mock_gatekeeper):
        """Test safe_delete calls gatekeeper.safe_delete."""
        with patch(
            "agentic_core.L5_safety.core.ArchivalGatekeeper.ArchivalGatekeeper.get_instance",
            return_value=mock_gatekeeper,
        ):
            from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

            agent = LocationHealerAgent(project_root=temp_project)

            # Create test file
            test_file = temp_project / "delete_me.py"
            test_file.write_text("# to delete")

            # Execute delete (not dry run)
            result = agent.safe_delete(test_file, dry_run=False)

            # Verify gatekeeper was called
            mock_gatekeeper.safe_delete.assert_called_once()
            call_args = mock_gatekeeper.safe_delete.call_args
            assert call_args[0][0] == test_file, "File path should be passed to gatekeeper"
            assert "LocationHealerAgent" in str(call_args[0][1]), "Agent name should be passed"

    def test_no_direct_unlink_in_safe_delete(self):
        """Verify safe_delete source code doesn't use path.unlink() directly."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        source = inspect.getsource(LocationHealerAgent.safe_delete)

        # Should NOT contain direct unlink calls (except in comments)
        lines = [line for line in source.split("\n") if not line.strip().startswith("#")]
        code_only = "\n".join(lines)

        assert "file_path.unlink()" not in code_only, "safe_delete should not use direct unlink()"
        assert "gatekeeper.safe_delete" in source, "safe_delete should use gatekeeper.safe_delete"


class TestHierarchyAgentAuthority:
    """Test HierarchyAgent uses ArchivalGatekeeper."""

    @pytest.fixture
    def mock_gatekeeper(self):
        """Create a mock ArchivalGatekeeper."""
        mock = MagicMock()
        mock.safe_move.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/dest"), error=None
        )
        mock.safe_delete.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/archive"), error=None
        )
        mock.safe_archive.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/archive"), error=None
        )
        return mock

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)
        (tmp_path / "archives" / "hierarchy_violations").mkdir(parents=True)
        return tmp_path

    def test_has_gatekeeper_attribute(self, temp_project, mock_gatekeeper):
        """Test HierarchyAgent initializes with gatekeeper."""
        with patch(
            "agentic_core.L5_safety.core.ArchivalGatekeeper.ArchivalGatekeeper.get_instance",
            return_value=mock_gatekeeper,
        ):
            from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

            agent = HierarchyAgent(project_root=temp_project, healing_enabled=False)

            assert hasattr(agent, "gatekeeper"), "HierarchyAgent must have gatekeeper attribute"
            assert hasattr(agent, "agent_name"), "HierarchyAgent must have agent_name attribute"
            assert agent.agent_name == "HierarchyAgent"

    def test_no_raw_shutil_move_in_relocation_methods(self):
        """Verify relocation methods use gatekeeper instead of shutil.move."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        # Check _relocate_file_to_l2 method
        source = inspect.getsource(HierarchyAgent)

        # Count shutil.move occurrences (should be minimal or zero in main code paths)
        # Note: shutil.rmtree for __pycache__ is acceptable
        lines = source.split("\n")
        shutil_move_lines = [
            line for line in lines if "shutil.move" in line and not line.strip().startswith("#")
        ]

        # All shutil.move should be replaced with gatekeeper.safe_move
        assert len(shutil_move_lines) == 0, (
            f"Found {len(shutil_move_lines)} shutil.move calls that should use gatekeeper"
        )

    def test_gatekeeper_used_in_depth_healing(self):
        """Verify depth healing uses gatekeeper.safe_move."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        source = inspect.getsource(HierarchyAgent._heal_depth_violation)

        assert "gatekeeper.safe_move" in source, (
            "_heal_depth_violation should use gatekeeper.safe_move"
        )
        assert "file_path.rename" not in source.replace("#", ""), (
            "_heal_depth_violation should not use direct rename"
        )


class TestFilesystemSSOTReconcilerAgentAuthority:
    """Test FilesystemSSOTReconcilerAgent uses ArchivalGatekeeper."""

    @pytest.fixture
    def mock_gatekeeper(self):
        """Create a mock ArchivalGatekeeper."""
        mock = MagicMock()
        mock.safe_move.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/dest"), error=None
        )
        mock.safe_delete.return_value = MagicMock(
            success=True, destination_path=Path("/tmp/archive"), error=None
        )
        return mock

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "agentic_core" / "config" / "blueprint_sovereign").mkdir(parents=True)
        blueprint = (
            tmp_path / "agentic_core" / "config" / "blueprint_sovereign" / "structure_blueprint.py"
        )
        blueprint.write_text("# Blueprint stub\nSOVEREIGN_REGISTRY = {}")
        (tmp_path / "archives" / "unmapped_drift").mkdir(parents=True)
        return tmp_path

    def test_has_gatekeeper_attribute(self, temp_project, mock_gatekeeper):
        """Test FilesystemSSOTReconcilerAgent initializes with gatekeeper."""
        with patch(
            "agentic_core.L5_safety.core.ArchivalGatekeeper.ArchivalGatekeeper.get_instance",
            return_value=mock_gatekeeper,
        ):
            from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
                FilesystemSSOTReconcilerAgent,
            )

            agent = FilesystemSSOTReconcilerAgent(project_root=temp_project)

            assert hasattr(agent, "gatekeeper"), (
                "FilesystemSSOTReconcilerAgent must have gatekeeper attribute"
            )
            assert hasattr(agent, "agent_name"), (
                "FilesystemSSOTReconcilerAgent must have agent_name attribute"
            )
            assert agent.agent_name == "FilesystemSSOTReconcilerAgent"

    def test_no_raw_shutil_move_in_archive_method(self):
        """Verify _apply_filesystem_alignment uses gatekeeper."""
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,
        )

        source = inspect.getsource(FilesystemSSOTReconcilerAgent._apply_filesystem_alignment)

        # Should use gatekeeper.safe_move, not shutil.move
        assert "gatekeeper.safe_move" in source, (
            "_apply_filesystem_alignment should use gatekeeper.safe_move"
        )

        # Check for raw shutil.move (excluding comments)
        lines = [line for line in source.split("\n") if not line.strip().startswith("#")]
        code_only = "\n".join(lines)
        assert "shutil.move" not in code_only, (
            "_apply_filesystem_alignment should not use raw shutil.move"
        )


class TestGatekeeperImportPresence:
    """Verify all target agents import ArchivalGatekeeper."""

    def test_location_healer_imports_gatekeeper(self):
        """Verify LocationHealerAgent imports ArchivalGatekeeper."""
        source_path = (
            project_root / "agentic_core" / "L5_safety" / "validators" / "LocationHealerAgent.py"
        )
        source = source_path.read_text()

        assert (
            "from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper"
            in source
        )

    def test_hierarchy_agent_imports_gatekeeper(self):
        """Verify HierarchyAgent imports ArchivalGatekeeper."""
        source_path = (
            project_root / "agentic_core" / "L5_safety" / "validators" / "HierarchyAgent.py"
        )
        source = source_path.read_text()

        assert (
            "from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper"
            in source
        )

    def test_filesystem_reconciler_imports_gatekeeper(self):
        """Verify FilesystemSSOTReconcilerAgent imports ArchivalGatekeeper."""
        source_path = (
            project_root
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "FilesystemSSOTReconcilerAgent.py"
        )
        source = source_path.read_text()

        assert (
            "from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper"
            in source
        )


class TestGatekeeperLockScript:
    """Test the gatekeeper_lock.py pre-commit hook."""

    def test_lock_script_exists(self):
        """Verify gatekeeper_lock.py exists."""
        # Use absolute path to avoid any path resolution issues
        lock_path = Path("C:/Git/Agentic-Workflow/scripts/security/gatekeeper_lock.py")
        if not lock_path.exists():
            # Fallback to relative path from project_root
            lock_path = project_root / "scripts" / "security" / "gatekeeper_lock.py"
        assert lock_path.exists() or lock_path.is_file(), (
            f"gatekeeper_lock.py should exist at {lock_path}"
        )

    def test_lock_script_has_protected_files(self):
        """Verify lock script protects ArchivalGatekeeper.py."""
        lock_path = project_root / "scripts" / "security" / "gatekeeper_lock.py"
        source = lock_path.read_text(encoding="utf-8")

        assert "ArchivalGatekeeper.py" in source, "Lock script should protect ArchivalGatekeeper.py"
        assert "PROTECTED_FILES" in source, "Lock script should define PROTECTED_FILES"

    def test_lock_script_has_override_mechanism(self):
        """Verify lock script has override mechanism."""
        lock_path = project_root / "scripts" / "security" / "gatekeeper_lock.py"
        source = lock_path.read_text(encoding="utf-8")

        assert "SECURITY-OVERRIDE" in source, "Lock script should support [SECURITY-OVERRIDE] token"
        assert "GATEKEEPER_BYPASS" in source, "Lock script should support GATEKEEPER_BYPASS env var"


class TestPreCommitConfiguration:
    """Test pre-commit configuration includes gatekeeper hooks."""

    def test_precommit_has_gatekeeper_lock(self):
        """Verify .pre-commit-config.yaml has gatekeeper-security-lock hook."""
        config_path = project_root / ".pre-commit-config.yaml"
        config = config_path.read_text()

        assert "gatekeeper-security-lock" in config, (
            "Pre-commit should have gatekeeper-security-lock hook"
        )
        assert "gatekeeper_lock.py" in config, "Pre-commit should reference gatekeeper_lock.py"

    def test_precommit_has_ruff(self):
        """Verify .pre-commit-config.yaml has Ruff linter."""
        config_path = project_root / ".pre-commit-config.yaml"
        config = config_path.read_text()

        assert "ruff" in config.lower(), "Pre-commit should have Ruff linter"
        assert "astral-sh/ruff-pre-commit" in config, "Pre-commit should use official Ruff repo"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
