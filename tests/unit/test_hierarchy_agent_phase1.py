"""
Phase 1 Tests for HierarchyAgent Universal Scope and Auto-Approve

Tests verify:
1. Auto-approve bypasses interactive prompts
2. Universal scope scans all SOVEREIGN_REGISTRY roots
3. Dry-run safety prevents physical changes
"""

import pytest
from unittest.mock import patch
from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent


class TestHierarchyAgentPhase1:
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

    def test_auto_approve_sovereignty(self, mock_project):
        """Test Case 1.1: Verify auto_approve bypasses user input."""
        # Initialize with Sovereignty Switch ON
        agent = HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)

        # Verify the flag is set
        assert agent._auto_approve is True

        # Create a violation in agentic_core (non-approved L2 layer)
        bad_layer = mock_project / "agentic_core" / "illegal_layer"
        bad_layer.mkdir()
        bad_file = bad_layer / "misplaced.py"
        bad_file.write_text("# Test file")

        # Mock sys.stdin to fail if accessed (proving we bypassed it)
        with patch("builtins.input", side_effect=Exception("Should not ask for input!")):
            results = agent.relocate_misplaced_files()

        # Verification - should detect violation
        assert results["violations_found"] >= 1
        assert "agentic_core" in results["roots_processed"]

    def test_universal_scope_expansion(self, mock_project):
        """Test Case 1.2: Verify agent scans multiple roots, not just agentic_core."""
        agent = HierarchyAgent(mock_project)

        # Force the registry to be processed
        results = agent.relocate_misplaced_files()

        processed_roots = results.get("roots_processed", [])

        # Assert Scope Expansion
        assert "agentic_core" in processed_roots
        assert "apps_shared" in processed_roots, "Agent failed to scan apps_shared"
        assert "apps_rg" in processed_roots, "Agent failed to scan apps_rg"

        # Assert robustness (tests dir doesn't exist in fixture, should be skipped gracefully)
        assert "tests" not in processed_roots

    def test_dry_run_safety(self, mock_project):
        """Test Case 1.3: Verify dry_run prevents physical moves even with auto_approve."""
        agent = HierarchyAgent(mock_project, healing_enabled=False, auto_approve=True)

        # Create a violation
        bad_layer = mock_project / "agentic_core" / "ghost_layer"
        bad_layer.mkdir()
        bad_file = bad_layer / "ghost.py"
        bad_file.write_text("# Ghost file")

        # Execute with healing disabled (dry run)
        results = agent.relocate_misplaced_files()

        # Should report violation but NOT move file
        assert bad_file.exists(), "Dry run deleted the source file!"
        assert results["violations_found"] >= 1
        assert results["files_relocated"] == 0, "Dry run should not relocate files"

    def test_auto_approve_parameter_persistence(self, mock_project):
        """Test Case 1.4: Verify auto_approve persists across agent lifecycle."""
        # Test with auto_approve=True
        agent_auto = HierarchyAgent(mock_project, auto_approve=True)
        assert agent_auto._auto_approve is True

        # Test with auto_approve=False (default)
        agent_manual = HierarchyAgent(mock_project)
        assert agent_manual._auto_approve is False

        # Test explicit False
        agent_explicit = HierarchyAgent(mock_project, auto_approve=False)
        assert agent_explicit._auto_approve is False

    def test_roots_processed_tracking(self, mock_project):
        """Test Case 1.5: Verify roots_processed accurately tracks scanned territories."""
        agent = HierarchyAgent(mock_project)

        results = agent.relocate_misplaced_files()

        # Should track all existing roots
        assert len(results["roots_processed"]) >= 3
        assert all(isinstance(r, str) for r in results["roots_processed"])

        # Should only include roots that exist
        for root_name in results["roots_processed"]:
            assert (mock_project / root_name).exists()

    def test_phase2_placeholders_present(self, mock_project):
        """Test Case 1.6: Verify Phase 2 placeholders are in place for apps and tests."""
        agent = HierarchyAgent(mock_project)

        # Create apps_rg and tests to trigger placeholders
        (mock_project / "tests").mkdir()
        (mock_project / "tests" / "unit").mkdir()

        results = agent.relocate_misplaced_files()

        # Should process these roots without errors
        assert "apps_rg" in results["roots_processed"]
        assert "tests" in results["roots_processed"]
        assert len(results["errors"]) == 0, f"Unexpected errors: {results['errors']}"
