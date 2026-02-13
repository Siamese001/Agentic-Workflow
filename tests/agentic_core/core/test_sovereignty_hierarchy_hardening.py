"""
Test Suite for Sovereignty & Hierarchy Hardening (Phase 1)

Tests the hardening changes to:
1. PascalSovereigntyAgent - Structural recognition and suffix enforcement
2. HierarchyAgent - target_territory propagation to sub-routines
"""

from unittest.mock import patch

import pytest


# Mock the security validation before importing agents
@pytest.fixture(autouse=True)
def mock_security_validation():
    """Mock security validation to allow temp directories in tests."""
    with patch(
        "agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent._security_hardening_validation",
        return_value=None,
    ):
        yield


class TestPascalSovereigntyStructuralClassification:
    """Tests for PascalSovereigntyAgent structural classification hardening."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a mock project structure."""
        core = tmp_path / "agentic_core"
        core.mkdir()
        (core / "prompt_governance").mkdir()
        (core / "prompt_governance" / "agents").mkdir()
        (core / "L5_safety").mkdir()
        (core / "L5_safety" / "validators").mkdir()
        return tmp_path

    @pytest.fixture
    def agent(self, workspace, mock_security_validation):
        """Create PascalSovereigntyAgent instance."""
        from agentic_core.L5_safety.validators.PascalSovereigntyAgent import (
            PascalSovereigntyAgent,
        )

        return PascalSovereigntyAgent(project_root=workspace, dry_run=True)

    def test_structural_agent_in_agents_folder_classified_as_agent(self, workspace, agent):
        """Verify files in agents/ folder are classified as AGENT regardless of class name."""
        target = workspace / "agentic_core" / "prompt_governance" / "agents" / "GovernanceHub.py"
        target.write_text("class GovernanceHub:\n    pass", encoding="utf-8")

        result = agent.classify_file(target)
        assert result == "AGENT", f"Expected AGENT, got {result}"

    def test_structural_agent_in_validators_folder_classified_as_agent(self, workspace, agent):
        """Verify files in validators/ folder are classified as AGENT regardless of class name."""
        target = workspace / "agentic_core" / "L5_safety" / "validators" / "DashboardRenderer.py"
        target.write_text("class DashboardRenderer:\n    pass", encoding="utf-8")

        result = agent.classify_file(target)
        assert result == "AGENT", f"Expected AGENT, got {result}"

    def test_structural_agent_gets_agent_suffix_recommendation(self, workspace, agent):
        """Verify structural agents are recommended to have Agent suffix."""
        target = workspace / "agentic_core" / "prompt_governance" / "agents" / "GovernanceHub.py"
        target.write_text("class GovernanceHub:\n    pass", encoding="utf-8")

        compliant_name = agent.get_compliant_name(target, "AGENT")
        assert compliant_name == "GovernanceHubAgent.py", (
            f"Expected GovernanceHubAgent.py, got {compliant_name}"
        )

    def test_regular_class_not_in_agent_folder_classified_as_class(self, workspace, agent):
        """Verify regular classes outside agent folders are classified as CLASS."""
        utils = workspace / "agentic_core" / "utils"
        utils.mkdir()
        target = utils / "Helper.py"
        target.write_text("class Helper:\n    pass", encoding="utf-8")

        result = agent.classify_file(target)
        assert result == "CLASS", f"Expected CLASS, got {result}"

    def test_agent_class_by_name_still_classified_as_agent(self, workspace, agent):
        """Verify classes ending in Agent are still classified as AGENT."""
        utils = workspace / "agentic_core" / "utils"
        utils.mkdir()
        target = utils / "HelperAgent.py"
        target.write_text("class HelperAgent:\n    pass", encoding="utf-8")

        result = agent.classify_file(target)
        assert result == "AGENT", f"Expected AGENT, got {result}"

    def test_agent_class_by_inheritance_still_classified_as_agent(self, workspace, agent):
        """Verify classes inheriting from *Agent are still classified as AGENT."""
        utils = workspace / "agentic_core" / "utils"
        utils.mkdir()
        target = utils / "MyHelper.py"
        target.write_text("class MyHelper(SovereignBaseAgent):\n    pass", encoding="utf-8")

        result = agent.classify_file(target)
        assert result == "AGENT", f"Expected AGENT, got {result}"


class TestPascalSovereigntyScopedHealing:
    """Tests for PascalSovereigntyAgent scoped healing with target_territory."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a mock project structure with multiple potential paths."""
        core = tmp_path / "agentic_core"
        core.mkdir()
        (core / "prompt_governance").mkdir()

        # Also create a root-level territory
        (tmp_path / "apps_rg").mkdir()
        return tmp_path

    @pytest.fixture
    def agent(self, workspace, mock_security_validation):
        """Create PascalSovereigntyAgent instance."""
        from agentic_core.L5_safety.validators.PascalSovereigntyAgent import (
            PascalSovereigntyAgent,
        )

        return PascalSovereigntyAgent(project_root=workspace, dry_run=True)

    def test_heal_repository_finds_agentic_core_territory(self, workspace, agent):
        """Verify heal_repository finds territory under agentic_core."""
        result = agent.heal_repository(dry_run=True, target_territory="prompt_governance")
        # Should not skip (skipped=0) since path exists
        assert result.get("skipped", 0) == 0

    def test_heal_repository_finds_root_territory(self, workspace, agent):
        """Verify heal_repository finds territory at project root."""
        result = agent.heal_repository(dry_run=True, target_territory="apps_rg")
        # Should not skip (skipped=0) since path exists
        assert result.get("skipped", 0) == 0

    def test_heal_repository_skips_nonexistent_territory(self, workspace, agent):
        """Verify heal_repository skips when territory doesn't exist."""
        result = agent.heal_repository(dry_run=True, target_territory="nonexistent_territory")
        # Should skip (skipped=1) since path doesn't exist
        assert result.get("skipped", 0) == 1


class TestHierarchyScopedHealing:
    """Tests for HierarchyAgent scoped healing with target_territory propagation."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a mock project structure."""
        core = tmp_path / "agentic_core"
        core.mkdir()
        (core / "L5_safety").mkdir()
        (core / "L5_safety" / "prompt_governance").mkdir()

        # Create apps folder for depth testing
        (tmp_path / "apps_rg").mkdir()
        (tmp_path / "apps_rg" / "engines").mkdir()

        return tmp_path

    @pytest.fixture
    def hierarchy_agent(self, workspace, mock_security_validation):
        """Create HierarchyAgent instance."""
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

        return HierarchyAgent(
            project_root=workspace,
            healing_enabled=False,  # Dry run mode
            auto_approve=True,
        )

    def test_heal_hierarchy_passes_target_territory_to_create_structure(self, workspace, hierarchy_agent):
        """Verify heal_hierarchy passes target_territory to create_missing_structure."""
        with patch.object(
            hierarchy_agent,
            "create_missing_structure",
            return_value={"violations_found": 0, "created": []},
        ) as mock_create:
            hierarchy_agent.heal_hierarchy(
                target_territory="prompt_governance",
                create_structure=True,
                relocate_files=False,
                enforce_depth=False,
                purge_orphans=False,
            )
            mock_create.assert_called_once_with("prompt_governance")

    def test_heal_hierarchy_passes_target_territory_to_relocate_files(self, workspace, hierarchy_agent):
        """Verify heal_hierarchy passes target_territory to relocate_misplaced_files."""
        with patch.object(
            hierarchy_agent,
            "relocate_misplaced_files",
            return_value={"violations_found": 0, "files_relocated": 0},
        ) as mock_relocate:
            hierarchy_agent.heal_hierarchy(
                target_territory="prompt_governance",
                create_structure=False,
                relocate_files=True,
                enforce_depth=False,
                purge_orphans=False,
            )
            mock_relocate.assert_called_once_with("prompt_governance")

    def test_heal_hierarchy_passes_target_territory_to_enforce_depth(self, workspace, hierarchy_agent):
        """Verify heal_hierarchy passes target_territory to enforce_depth_rules."""
        with patch.object(
            hierarchy_agent,
            "enforce_depth_rules",
            return_value={"violations_found": 0},
        ) as mock_depth:
            hierarchy_agent.heal_hierarchy(
                target_territory="prompt_governance",
                create_structure=False,
                relocate_files=False,
                enforce_depth=True,
                purge_orphans=False,
            )
            mock_depth.assert_called_once_with("prompt_governance")

    def test_heal_hierarchy_skips_orphan_purge_in_scoped_mode(self, workspace, hierarchy_agent):
        """Verify heal_hierarchy skips global orphan purge when target_territory is set."""
        with patch.object(
            hierarchy_agent,
            "purge_orphaned_files",
            return_value={"purged": 0, "violations_found": 0},
        ) as mock_purge:
            results = hierarchy_agent.heal_hierarchy(
                target_territory="prompt_governance",
                create_structure=False,
                relocate_files=False,
                enforce_depth=False,
                purge_orphans=True,
            )
            # purge_orphaned_files should NOT be called in scoped mode
            mock_purge.assert_not_called()
            # Results should show 0 purged
            assert results["purge"]["purged"] == 0
            assert results["purge"]["violations_found"] == 0

    def test_heal_hierarchy_runs_orphan_purge_in_global_mode(self, workspace, hierarchy_agent):
        """Verify heal_hierarchy runs orphan purge when target_territory is None."""
        with patch.object(
            hierarchy_agent,
            "purge_orphaned_files",
            return_value={"purged": 0, "violations_found": 0},
        ) as mock_purge:
            hierarchy_agent.heal_hierarchy(
                target_territory=None,
                create_structure=False,
                relocate_files=False,
                enforce_depth=False,
                purge_orphans=True,
            )
            # purge_orphaned_files SHOULD be called in global mode
            mock_purge.assert_called_once()


class TestEnforceDepthRulesScoping:
    """Tests for enforce_depth_rules target_territory scoping."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a mock project structure."""
        core = tmp_path / "agentic_core"
        core.mkdir()
        (tmp_path / "apps_rg").mkdir()
        (tmp_path / "tests").mkdir()
        return tmp_path

    @pytest.fixture
    def hierarchy_agent(self, workspace, mock_security_validation):
        """Create HierarchyAgent instance."""
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

        return HierarchyAgent(project_root=workspace, healing_enabled=False, auto_approve=True)

    def test_enforce_depth_skips_apps_when_targeting_core_module(self, workspace, hierarchy_agent):
        """Verify enforce_depth_rules skips apps depth check when targeting a core module."""
        with patch.object(hierarchy_agent, "_enforce_apps_depth", return_value=0) as mock_apps:
            with patch.object(hierarchy_agent, "_enforce_tests_depth", return_value=0) as mock_tests:
                with patch.object(hierarchy_agent, "_enforce_universal_depth", return_value=0):
                    hierarchy_agent.enforce_depth_rules(target_territory="prompt_governance")
                    # Apps depth should NOT be called when targeting core module
                    mock_apps.assert_not_called()
                    # Tests depth should NOT be called when targeting core module
                    mock_tests.assert_not_called()

    def test_enforce_depth_runs_apps_when_targeting_apps(self, workspace, hierarchy_agent):
        """Verify enforce_depth_rules runs apps depth check when targeting apps_*."""
        with patch.object(hierarchy_agent, "_enforce_apps_depth", return_value=0) as mock_apps:
            with patch.object(hierarchy_agent, "_enforce_tests_depth", return_value=0):
                with patch.object(hierarchy_agent, "_enforce_universal_depth", return_value=0):
                    hierarchy_agent.enforce_depth_rules(target_territory="apps_rg")
                    # Apps depth SHOULD be called when targeting apps
                    mock_apps.assert_called_once()

    def test_enforce_depth_runs_tests_when_targeting_tests(self, workspace, hierarchy_agent):
        """Verify enforce_depth_rules runs tests depth check when targeting tests."""
        with patch.object(hierarchy_agent, "_enforce_apps_depth", return_value=0):
            with patch.object(hierarchy_agent, "_enforce_tests_depth", return_value=0) as mock_tests:
                with patch.object(hierarchy_agent, "_enforce_universal_depth", return_value=0):
                    hierarchy_agent.enforce_depth_rules(target_territory="tests")
                    # Tests depth SHOULD be called when targeting tests
                    mock_tests.assert_called_once()
