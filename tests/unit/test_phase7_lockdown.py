"""Phase 7 Tests: Final Sovereign Lockdown & CI/CD Integration.

Tests for CI-ready lockdown verification and non-interactive mode.
"""

from __future__ import annotations

import pytest
from unittest.mock import patch


class TestFinalLockdownPurity:
    """Phase 7 Tests: Final lockdown purity verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project with no violations."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "__init__.py").write_text("")
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_finalize_sovereign_lockdown_method_exists(self, tmp_path):
        """[Phase 7] Verify finalize_sovereign_lockdown method exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        assert hasattr(agent, "finalize_sovereign_lockdown")
        assert callable(agent.finalize_sovereign_lockdown)

    def test_finalize_sovereign_lockdown_returns_tuple(self, clean_project):
        """[Phase 7] Verify method returns (bool, dict) tuple."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)
        result = agent.finalize_sovereign_lockdown()

        assert isinstance(result, tuple)
        assert len(result) == 2

        is_pure, results = result
        assert isinstance(is_pure, bool)
        assert isinstance(results, dict)

    def test_final_lockdown_purity(self, clean_project):
        """[Phase 7] Verify is_pure=True when 0 violations."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        # Mock heal_repository to return 0 violations
        original_heal = agent.heal_repository

        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "status": "PASS",
                "_raw_result": {
                    "violations_found": 0,
                    "violations_fixed": 0,
                },
            }

        agent.heal_repository = mock_heal

        is_pure, results = agent.finalize_sovereign_lockdown()

        assert is_pure is True

    def test_lockdown_returns_violations_found(self, clean_project):
        """[Phase 7] Verify results contain violations_found."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)
        is_pure, results = agent.finalize_sovereign_lockdown()

        # Check raw result
        raw_result = results.get("_raw_result", results)
        assert "violations_found" in raw_result


class TestLockdownBlocksDrift:
    """Phase 7 Tests: Lockdown detects unauthorized changes."""

    @pytest.fixture
    def project_with_rogue_folder(self, tmp_path):
        """Setup project with unauthorized L9 folder."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L9_unauthorized").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L9_unauthorized" / "RogueAgent.py").write_text(
            "class RogueAgent:\n    pass"
        )
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_lockdown_blocks_drift(self, project_with_rogue_folder):
        """[Phase 7] Verify is_pure=False when rogue folder exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=project_with_rogue_folder)

        # Mock heal_repository to return violations
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 1,
                "violations_fixed": 0,
                "status": "FAIL",
                "_raw_result": {
                    "violations_found": 1,
                    "violations_fixed": 0,
                    "roots_scanned": ["agentic_core"],
                },
            }

        agent.heal_repository = mock_heal

        is_pure, results = agent.finalize_sovereign_lockdown()

        assert is_pure is False

    def test_lockdown_identifies_rogue_in_results(self, project_with_rogue_folder):
        """[Phase 7] Verify rogue folder is identified in results."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=project_with_rogue_folder)

        # Mock to include violation details
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 1,
                "violations_fixed": 0,
                "status": "FAIL",
                "_raw_result": {
                    "violations_found": 1,
                    "violations_fixed": 0,
                    "violations": [{"type": "ORPHAN", "path": "agentic_core/L9_unauthorized"}],
                },
            }

        agent.heal_repository = mock_heal

        is_pure, results = agent.finalize_sovereign_lockdown()

        assert is_pure is False
        raw_result = results.get("_raw_result", results)
        assert raw_result.get("violations_found", 0) > 0


class TestCIModeNonInteractive:
    """Phase 7 Tests: CI mode non-interactive operation."""

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

    def test_ci_mode_non_interactive(self, clean_project):
        """[Phase 7] Verify lockdown completes without TTY/stdin."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,  # CI mode
        )

        # Mock sys.stdin.isatty to return False (no TTY)
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            mock_stdin.readline.side_effect = EOFError("No stdin in CI")

            # Should complete without raising EOFError or hanging
            is_pure, results = agent.finalize_sovereign_lockdown()

        # Should return valid result
        assert isinstance(is_pure, bool)
        assert isinstance(results, dict)

    def test_ci_mode_with_auto_approve(self, clean_project):
        """[Phase 7] Verify auto_approve prevents interactive prompts."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
        )

        # Verify auto_approve is set
        assert agent.auto_approve is True

        # Run lockdown - should not prompt
        is_pure, results = agent.finalize_sovereign_lockdown()

        assert isinstance(results, dict)

    def test_lockdown_uses_dry_run(self, clean_project):
        """[Phase 7] Verify lockdown uses dry_run=True (non-destructive)."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        # Track heal_repository calls
        heal_calls = []
        original_heal = agent.heal_repository

        def tracking_heal(*args, **kwargs):
            heal_calls.append(kwargs)
            return original_heal(*args, **kwargs)

        agent.heal_repository = tracking_heal

        agent.finalize_sovereign_lockdown()

        # Should have called with dry_run=True
        assert len(heal_calls) > 0
        assert heal_calls[0].get("dry_run") is True
        assert heal_calls[0].get("execute") is False


class TestPhase7Integration:
    """Phase 7 Tests: Integration with existing phases."""

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

    def test_lockdown_after_healing_pass(self, clean_project):
        """[Phase 7] Verify lockdown works after full healing pass."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # First: Run healing pass
        heal_result = agent.heal_repository(dry_run=True)

        # Then: Run lockdown
        is_pure, lockdown_result = agent.finalize_sovereign_lockdown()

        # Both should complete successfully
        assert isinstance(heal_result, dict)
        assert isinstance(lockdown_result, dict)

    def test_run_ci_verification_sync_exists(self, clean_project):
        """[Phase 7] Verify run_ci_verification_sync method exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        assert hasattr(agent, "run_ci_verification_sync")
        assert callable(agent.run_ci_verification_sync)
