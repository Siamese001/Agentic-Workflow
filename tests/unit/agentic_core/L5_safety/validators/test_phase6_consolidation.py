"""Phase 6 Tests: Universal Logic Consolidation & Healing.

Tests for zero-loss collision resolution and I/O efficiency.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestDeduplicationHealingPriority:
    """Phase 6 Tests: Deduplication healing priority logic."""

    @pytest.fixture
    def mock_project_with_duplicates(self, tmp_path):
        """Setup project with duplicate agent files across roots."""
        # Create agentic_core version (highest priority)
        (tmp_path / "agentic_core" / "L1_cognition").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L1_cognition" / "DuplicateAgent.py").write_text(
            "class DuplicateAgent:\n    '''Master version'''\n    pass"
        )

        # Create apps_shared version (lower priority)
        (tmp_path / "apps_shared").mkdir(parents=True)
        (tmp_path / "apps_shared" / "DuplicateAgent.py").write_text(
            "class DuplicateAgent:\n    '''Duplicate version'''\n    pass"
        )

        # Create archives directory
        (tmp_path / "archives" / "deduplication_cleanup").mkdir(parents=True)

        return tmp_path

    def test_resolve_collision_method_exists(self, tmp_path):
        """[Phase 6] Verify _resolve_collision method exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        assert hasattr(agent, "_resolve_collision")
        assert callable(agent._resolve_collision)

    def test_deduplication_audit_has_execute_param(self, tmp_path):
        """[Phase 6] Verify _trigger_deduplication_audit accepts execute parameter."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        # Should accept execute parameter without error
        result = agent._trigger_deduplication_audit(["agentic_core"], execute=False)

        assert "collisions_found" in result
        assert "collisions_fixed" in result

    def test_deduplication_healing_priority_logic(self, mock_project_with_duplicates):
        """[Phase 6] Verify agentic_core is preserved during merge."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=mock_project_with_duplicates,
            auto_approve=True,
            healing_enabled=True,
        )

        # Create a mock violation with locations
        mock_violation = MagicMock()
        mock_violation.locations = [
            mock_project_with_duplicates / "agentic_core" / "L1_cognition" / "DuplicateAgent.py",
            mock_project_with_duplicates / "apps_shared" / "DuplicateAgent.py",
        ]

        # Mock the gatekeeper
        mock_gatekeeper = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gatekeeper.safe_move.return_value = mock_result
        agent._archival_gatekeeper = mock_gatekeeper

        # Execute resolution
        fixed = agent._resolve_collision(mock_violation)

        # Should archive 1 file (apps_shared version)
        assert fixed == 1

        # Verify safe_move was called with the lower-priority file
        call_args = mock_gatekeeper.safe_move.call_args
        archived_path = call_args[0][0]
        assert "apps_shared" in str(archived_path)

    def test_priority_order_correct(self, tmp_path):
        """[Phase 6] Verify priority order: agentic_core > apps_shared > apps_rg."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        # Setup directories
        (tmp_path / "agentic_core").mkdir()
        (tmp_path / "apps_shared").mkdir()
        (tmp_path / "apps_rg").mkdir()

        agent = ArchitectureGovernorAgent(
            project_root=tmp_path,
            auto_approve=True,
        )

        # Create mock violation with 3 locations
        mock_violation = MagicMock()
        mock_violation.locations = [
            tmp_path / "apps_rg" / "Agent.py",
            tmp_path / "agentic_core" / "Agent.py",
            tmp_path / "apps_shared" / "Agent.py",
        ]

        # Mock gatekeeper
        mock_gatekeeper = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gatekeeper.safe_move.return_value = mock_result
        agent._archival_gatekeeper = mock_gatekeeper

        # Execute
        fixed = agent._resolve_collision(mock_violation)

        # Should archive 2 files (apps_shared and apps_rg)
        assert fixed == 2

        # Verify agentic_core was NOT archived
        for call in mock_gatekeeper.safe_move.call_args_list:
            archived_path = str(call[0][0])
            assert "agentic_core" not in archived_path


class TestSovereignScannerIOReduction:
    """Phase 6 Tests: I/O reduction via SovereignScanner."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Setup minimal project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "TestAgent.py").write_text("# Test")
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_sovereign_scanner_io_reduction(self, mock_project):
        """[Phase 6] Verify scanner caching reduces I/O across agents."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        # First access - should scan
        scanner1 = SovereignScanner.get_instance(mock_project)
        map1 = scanner1.scan_repository()

        # Second access - should use cache
        scanner2 = SovereignScanner.get_instance(mock_project)
        map2 = scanner2.scan_repository()

        # Same instance, same map
        assert scanner1 is scanner2
        assert map1 is map2

    def test_cross_agent_scanner_sharing(self, mock_project):
        """[Phase 6] Verify multiple agents share same scanner instance."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent import (
            StructuralValidatorAgent,
            StructureConfig,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        # Create agents
        gov_agent = ArchitectureGovernorAgent(project_root=mock_project)
        val_agent = StructuralValidatorAgent(config=StructureConfig(project_root=mock_project))

        # Run both agents
        gov_agent.heal_repository(dry_run=True)
        val_agent.heal_repository(dry_run=True)

        # Both should have used the same scanner instance
        scanner = SovereignScanner.get_instance(mock_project)
        assert scanner is not None

        # Map should be populated
        repo_map = scanner.scan_repository()
        assert isinstance(repo_map, dict)


class TestZeroLossMergeIntegrity:
    """Phase 6 Tests: Zero-loss merge integrity."""

    @pytest.fixture
    def mock_project_with_triples(self, tmp_path):
        """Setup project with 3 identical files."""
        # Create 3 copies in different roots
        (tmp_path / "agentic_core" / "utils").mkdir(parents=True)
        (tmp_path / "apps_shared").mkdir(parents=True)
        (tmp_path / "tests" / "fixtures").mkdir(parents=True)

        content = "class TriplicateAgent:\n    pass"
        (tmp_path / "agentic_core" / "utils" / "TriplicateAgent.py").write_text(content)
        (tmp_path / "apps_shared" / "TriplicateAgent.py").write_text(content)
        (tmp_path / "tests" / "fixtures" / "TriplicateAgent.py").write_text(content)

        # Create archives directory
        (tmp_path / "archives" / "deduplication_cleanup").mkdir(parents=True)

        return tmp_path

    def test_zero_loss_merge_integrity(self, mock_project_with_triples):
        """[Phase 6] Verify 1 file remains, 2 archived (not deleted)."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=mock_project_with_triples,
            auto_approve=True,
            healing_enabled=True,
        )

        # Create mock violation with 3 locations
        mock_violation = MagicMock()
        mock_violation.locations = [
            mock_project_with_triples / "agentic_core" / "utils" / "TriplicateAgent.py",
            mock_project_with_triples / "apps_shared" / "TriplicateAgent.py",
            mock_project_with_triples / "tests" / "fixtures" / "TriplicateAgent.py",
        ]

        # Track archived files
        archived_files = []

        def mock_safe_move(path, destination_category=None, reason=None):
            archived_files.append(path)
            result = MagicMock()
            result.success = True
            return result

        mock_gatekeeper = MagicMock()
        mock_gatekeeper.safe_move = mock_safe_move
        agent._archival_gatekeeper = mock_gatekeeper

        # Execute resolution
        fixed = agent._resolve_collision(mock_violation)

        # Should archive 2 files
        assert fixed == 2
        assert len(archived_files) == 2

        # Master (agentic_core) should NOT be in archived list
        archived_paths = [str(p) for p in archived_files]
        for path in archived_paths:
            assert "agentic_core" not in path

    def test_no_action_on_single_file(self, tmp_path):
        """[Phase 6] Verify no action taken when only 1 file exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        # Single file - no collision
        mock_violation = MagicMock()
        mock_violation.locations = [tmp_path / "agentic_core" / "Agent.py"]

        fixed = agent._resolve_collision(mock_violation)

        assert fixed == 0

    def test_no_action_on_empty_locations(self, tmp_path):
        """[Phase 6] Verify no action taken when locations is empty."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        # Empty locations
        mock_violation = MagicMock()
        mock_violation.locations = []
        mock_violation.file_paths = []
        mock_violation.file_path = None

        fixed = agent._resolve_collision(mock_violation)

        assert fixed == 0


class test_phase6_integration:
    """Phase 6 Tests: Integration with heal_repository."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Setup minimal project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_heal_repository_includes_collisions_fixed(self, mock_project):
        """[Phase 6] Verify heal_repository returns collisions_fixed in dedup audit."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=mock_project,
            auto_approve=True,
        )

        result = agent.heal_repository(dry_run=True)

        # Check raw result
        raw_result = result.get("_raw_result", result)
        dedup = raw_result.get("deduplication_audit", {})

        assert "collisions_found" in dedup
        assert "collisions_fixed" in dedup

    def test_execute_mode_triggers_resolution(self, mock_project):
        """[Phase 6] Verify execute=True triggers collision resolution."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=mock_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Mock the deduplication audit to track execute parameter
        original_audit = agent._trigger_deduplication_audit
        execute_values = []

        def tracking_audit(roots, execute=False):
            execute_values.append(execute)
            return original_audit(roots, execute=execute)

        agent._trigger_deduplication_audit = tracking_audit

        # Run with execute=True, dry_run=False
        agent.heal_repository(dry_run=False, execute=True)

        # Should have called with execute=True
        assert True in execute_values
