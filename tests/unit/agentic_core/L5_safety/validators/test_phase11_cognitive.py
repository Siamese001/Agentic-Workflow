"""Phase 11 Tests: Cognitive Disposition Agent - AI-Powered Architectural Triage.

Tests for cognitive agent integration, gravity fallback, and disposition decision structure.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestCognitiveAgentIntegration:
    """Phase 11 Tests: Cognitive agent integration verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L3_orchestration").mkdir(parents=True)
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_cognitive_agent_integration(self, clean_project):
        """[Phase 11] Verify ORPHAN violation triggers cognitive disposition with MOVE."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Create orphan file
        orphan_file = clean_project / "orphan" / "OrphanAgent.py"
        orphan_file.parent.mkdir(parents=True, exist_ok=True)
        orphan_file.write_text("# Orphan agent")

        # Mock cognitive agent to return MOVE decision
        mock_decision = DispositionDecision(
            action="MOVE",
            target_path="agentic_core/L3_orchestration",
            reason="Agent with orchestration pattern",
            confidence=0.8,
        )

        mock_cognitive = MagicMock()
        mock_cognitive.analyze_violation.return_value = mock_decision
        agent._cognitive_agent = mock_cognitive

        # Mock gatekeeper to track moves
        moved_files = []
        mock_gatekeeper = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gatekeeper.safe_move.side_effect = lambda path, **kwargs: (
            moved_files.append(path),
            mock_result,
        )[1]
        agent._archival_gatekeeper = mock_gatekeeper

        # Process cognitive disposition
        result = agent._process_cognitive_disposition(orphan_file, "ORPHAN")

        # Verify
        assert result is True
        assert len(moved_files) == 1
        mock_cognitive.analyze_violation.assert_called_once()

    def test_cognitive_agent_archive_action(self, clean_project):
        """[Phase 11] Verify cognitive agent ARCHIVE action works."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
        )

        # Create file
        test_file = clean_project / "test_file.py"
        test_file.write_text("# Test")

        # Mock cognitive agent to return ARCHIVE decision
        mock_decision = DispositionDecision(
            action="ARCHIVE",
            target_path="archives/orphan_files",
            reason="Unclear destination",
            confidence=0.5,
        )

        mock_cognitive = MagicMock()
        mock_cognitive.analyze_violation.return_value = mock_decision
        agent._cognitive_agent = mock_cognitive

        # Mock gatekeeper
        mock_gatekeeper = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gatekeeper.safe_move.return_value = mock_result
        agent._archival_gatekeeper = mock_gatekeeper

        # Process
        result = agent._process_cognitive_disposition(test_file, "ORPHAN")

        assert result is True


class TestGravityFallbackToCognition:
    """Phase 11 Tests: Gravity fallback to cognitive disposition."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_gravity_fallback_to_cognition(self, clean_project):
        """[Phase 11] Verify gravity violation falls back to cognitive agent on failure."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Create file with gravity violation
        gravity_file = clean_project / "agentic_core" / "L5_safety" / "GravityViolator.py"
        gravity_file.parent.mkdir(parents=True, exist_ok=True)
        gravity_file.write_text("from agentic_core.L3_orchestration import something")

        # Mock gravity repair agent to fail
        mock_gravity_repair = MagicMock()
        mock_gravity_repair.analyze_violation.side_effect = Exception("Repair failed")
        agent._gravity_repair_agent = mock_gravity_repair

        # Mock cognitive agent to return ARCHIVE decision
        mock_decision = DispositionDecision(
            action="ARCHIVE",
            target_path="archives/gravity_violations",
            reason="Gravity violation requires manual refactoring",
            confidence=0.6,
        )

        mock_cognitive = MagicMock()
        mock_cognitive.analyze_violation.return_value = mock_decision
        agent._cognitive_agent = mock_cognitive

        # Mock gatekeeper
        mock_gatekeeper = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gatekeeper.safe_move.return_value = mock_result
        agent._archival_gatekeeper = mock_gatekeeper

        # Create violation dict
        violation = {
            "type": "GRAVITY",
            "file": str(gravity_file),
            "source_layer": "L5",
            "target_layer": "L3",
            "message": "L5 importing L3",
        }

        # Process violation - should fall back to cognitive
        agent._heal_violation(violation, auto_approve=True)

        # Cognitive agent should have been called
        mock_cognitive.analyze_violation.assert_called_once()

    def test_gravity_fallback_executes_archive(self, clean_project):
        """[Phase 11] Verify gravity fallback executes archive action."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
        )

        # Create file
        test_file = clean_project / "test.py"
        test_file.write_text("# Test")

        # Mock cognitive agent
        mock_decision = DispositionDecision(
            action="ARCHIVE",
            target_path="archives/gravity_violations",
            reason="Failed repair",
            confidence=0.6,
        )

        mock_cognitive = MagicMock()
        mock_cognitive.analyze_violation.return_value = mock_decision
        agent._cognitive_agent = mock_cognitive

        # Mock gatekeeper
        archived_files = []
        mock_gatekeeper = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gatekeeper.safe_move.side_effect = lambda path, **kwargs: (
            archived_files.append(path),
            mock_result,
        )[1]
        agent._archival_gatekeeper = mock_gatekeeper

        # Process
        result = agent._process_cognitive_disposition(test_file, "GRAVITY_FAIL")

        assert result is True
        assert len(archived_files) == 1


class TestDispositionDecisionStructure:
    """Phase 11 Tests: Disposition decision structure verification."""

    def test_disposition_decision_structure(self):
        """[Phase 11] Verify DispositionDecision fields are correctly typed."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )

        decision = DispositionDecision(
            action="MOVE",
            target_path="agentic_core/L3",
            reason="Test reason",
            confidence=0.85,
        )

        assert decision.action == "MOVE"
        assert decision.target_path == "agentic_core/L3"
        assert decision.reason == "Test reason"
        assert decision.confidence == 0.85

    def test_disposition_decision_defaults(self):
        """[Phase 11] Verify DispositionDecision defaults are respected."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )

        decision = DispositionDecision(action="IGNORE")

        assert decision.action == "IGNORE"
        assert decision.target_path is None
        assert decision.reason == ""
        assert decision.confidence == 0.0

    def test_disposition_decision_confidence_clamping(self):
        """[Phase 11] Verify confidence is clamped to [0.0, 1.0]."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )

        # Test over 1.0
        decision_high = DispositionDecision(action="MOVE", confidence=1.5)
        assert decision_high.confidence == 1.0

        # Test under 0.0
        decision_low = DispositionDecision(action="MOVE", confidence=-0.5)
        assert decision_low.confidence == 0.0

    def test_disposition_decision_invalid_action(self):
        """[Phase 11] Verify invalid action raises ValueError."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )

        with pytest.raises(ValueError):
            DispositionDecision(action="INVALID_ACTION")

    def test_disposition_decision_all_valid_actions(self):
        """[Phase 11] Verify all valid actions are accepted."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )

        valid_actions = ["MOVE", "REFACTOR", "ARCHIVE", "IGNORE", "MANUAL_REVIEW"]

        for action in valid_actions:
            decision = DispositionDecision(action=action)
            assert decision.action == action


class TestCognitiveAgentHeuristics:
    """Phase 11 Tests: Cognitive agent heuristic analysis."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    def test_orphan_agent_heuristic_validator(self, clean_project):
        """[Phase 11] Verify validator agent is suggested for L5_safety."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(project_root=clean_project)

        # Create validator-named file
        test_file = clean_project / "orphan" / "TestValidatorAgent.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Validator")

        decision = agent.analyze_violation(test_file, "ORPHAN")

        assert decision.action == "MOVE"
        assert "L5_safety" in decision.target_path

    def test_orphan_agent_heuristic_orchestration(self, clean_project):
        """[Phase 11] Verify orchestration agent is suggested for L3."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(project_root=clean_project)

        # Create orchestration-named file
        test_file = clean_project / "orphan" / "WorkflowCoordinatorAgent.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Orchestration")

        decision = agent.analyze_violation(test_file, "ORPHAN")

        assert decision.action == "MOVE"
        assert "L3" in decision.target_path

    def test_orphan_test_file_heuristic(self, clean_project):
        """[Phase 11] Verify test files are suggested for tests directory."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        agent = CognitiveDispositionAgent(project_root=clean_project)

        # Create test file
        test_file = clean_project / "orphan" / "test_something.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Test")

        decision = agent.analyze_violation(test_file, "ORPHAN")

        assert decision.action == "MOVE"
        assert "tests" in decision.target_path


class TestPhase11Integration:
    """Phase 11 Tests: Full integration verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_cognitive_agent_lazy_loading(self, clean_project):
        """[Phase 11] Verify cognitive agent is lazy-loaded."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        # Should be None initially
        assert agent._cognitive_agent is None

        # Should be loaded on first access
        cognitive = agent._get_cognitive_agent()
        assert cognitive is not None
        assert agent._cognitive_agent is not None

    def test_heal_violation_dispatches_orphan_to_cognitive(self, clean_project):
        """[Phase 11] Verify _heal_violation dispatches ORPHAN to cognitive."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Create orphan file
        orphan_file = clean_project / "orphan.py"
        orphan_file.write_text("# Orphan")

        # Mock cognitive agent
        mock_decision = DispositionDecision(
            action="ARCHIVE",
            target_path="archives/orphan_files",
            reason="Test",
            confidence=0.5,
        )

        mock_cognitive = MagicMock()
        mock_cognitive.analyze_violation.return_value = mock_decision
        agent._cognitive_agent = mock_cognitive

        # Mock gatekeeper
        mock_gatekeeper = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gatekeeper.safe_move.return_value = mock_result
        agent._archival_gatekeeper = mock_gatekeeper

        # Create violation
        violation = {
            "type": "ORPHAN",
            "file": str(orphan_file),
            "message": "Orphan file",
        }

        # Process
        agent._heal_violation(violation, auto_approve=True)

        # Cognitive should have been called
        mock_cognitive.analyze_violation.assert_called_once()
