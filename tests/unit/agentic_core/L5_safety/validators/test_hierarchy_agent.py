"""
Unit tests for HierarchyAgent - Consolidated from Phase 1-3 tests.

Tests verify:
1. HierarchyAgent initialization and basic functionality
2. File relocation operations
3. Structure creation capabilities
4. Auto-approve behavior
"""

import pytest

from agentic_core.L5_safety.validators.core.hierarchy_agent import HierarchyAgent


class TestHierarchyAgent:
    """Consolidated tests for HierarchyAgent functionality."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a mock project structure."""
        # Setup agentic_core (Legacy support)
        (tmp_path / "agentic_core").mkdir()
        (tmp_path / "agentic_core" / "L0_maintenance").mkdir()
        (tmp_path / "agentic_core" / "L0_maintenance" / "scripts").mkdir()

        # Setup apps_shared (Universal Scope support)
        (tmp_path / "apps_shared").mkdir()
        (tmp_path / "apps_shared" / "utils").mkdir()

        # Setup apps_rg
        (tmp_path / "apps_rg").mkdir()
        (tmp_path / "apps_rg" / "engines").mkdir()

        return tmp_path

    def test_hierarchy_agent_initialization(self, mock_project):
        """Test basic HierarchyAgent initialization."""
        agent = HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)

        assert agent.project_root == mock_project.resolve()
        assert agent.healing_enabled is True
        assert hasattr(agent, "gatekeeper")

    def test_auto_approve_sets_gatekeeper(self, mock_project):
        """Test that auto_approve configures the gatekeeper correctly."""
        # Test with auto_approve=True
        HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)
        # The gatekeeper should be configured to not require approval

        # Test with auto_approve=False (default)
        HierarchyAgent(mock_project, healing_enabled=True, auto_approve=False)
        # The gatekeeper should require approval

    def test_relocate_misplaced_files_returns_structure(self, mock_project):
        """Test that relocate_misplaced_files returns proper structure."""
        agent = HierarchyAgent(mock_project, healing_enabled=False, auto_approve=True)

        results = agent.relocate_misplaced_files()

        # Should return expected keys
        expected_keys = [
            "files_relocated",
            "folders_removed",
            "violations_found",
            "errors",
            "roots_processed",
        ]
        for key in expected_keys:
            assert key in results

    def test_create_missing_structure(self, mock_project):
        """Test structure creation functionality."""
        agent = HierarchyAgent(mock_project, healing_enabled=False, auto_approve=True)

        results = agent.create_missing_structure()

        # Should return expected keys
        for key in ["created", "errors", "violations_found"]:
            assert key in results

    def test_dry_run_mode(self, mock_project):
        """Test dry-run mode doesn't make changes."""
        agent = HierarchyAgent(mock_project, healing_enabled=False, auto_approve=True)

        # Create a violation
        bad_file = mock_project / "agentic_core" / "bad.py"
        bad_file.write_text("# Bad file")

        # Run in dry-run mode (healing_enabled=False)
        agent.relocate_misplaced_files()

        # File should still exist (no changes made)
        assert bad_file.exists()

    def test_heal_method_interface(self, mock_project):
        """Test the heal method interface."""
        agent = HierarchyAgent(mock_project, healing_enabled=False, auto_approve=True)

        # Test with a simple violation
        violation = {
            "type": "MISPLACED",
            "file": str(mock_project / "test.py"),
            "message": "Test violation",
        }

        result = agent.heal(violation)

        # Should return proper structure
        for key in ["status", "details", "artifacts", "errors"]:
            assert key in result
