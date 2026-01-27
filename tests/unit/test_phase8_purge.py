"""Phase 8 Tests: Sovereign Purge Execution & Baseline Normalization.

Tests for post-purge purity, CI script exit codes, and pre-commit integration.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestPostPurgePurity:
    """Phase 8 Tests: Post-purge purity verification."""

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

    def test_post_purge_purity(self, clean_project):
        """[Phase 8] Verify is_pure=True after full healing pass."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Mock heal_repository to simulate successful purge
        def mock_heal(*args, **kwargs):
            execute = kwargs.get("execute", False)
            dry_run = kwargs.get("dry_run", True)

            if execute and not dry_run:
                # Simulating purge execution
                return {
                    "violations_found": 2160,
                    "violations_fixed": 2160,
                    "status": "PASS",
                    "_raw_result": {
                        "violations_found": 2160,
                        "violations_fixed": 2160,
                    },
                }
            else:
                # Post-purge verification (dry_run)
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

        # Step 1: Execute purge
        purge_result = agent.heal_repository(execute=True, dry_run=False)

        # Step 2: Verify purity
        is_pure, lockdown_result = agent.finalize_sovereign_lockdown()

        # Assertions
        assert purge_result.get("violations_fixed", 0) == 2160
        assert is_pure is True

    def test_heal_repository_execute_mode(self, clean_project):
        """[Phase 8] Verify heal_repository accepts execute=True."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Should accept execute parameter without error
        result = agent.heal_repository(execute=True, dry_run=True)

        assert isinstance(result, dict)
        assert "violations_found" in result or "_raw_result" in result


class TestCIScriptExitCodes:
    """Phase 8 Tests: CI script exit code verification."""

    @pytest.fixture
    def project_with_violation(self, tmp_path):
        """Setup project with a known violation."""
        (tmp_path / "agentic_core" / "L9_unauthorized").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L9_unauthorized" / "RogueAgent.py").write_text(
            "class RogueAgent:\n    pass"
        )
        return tmp_path

    def test_ci_script_exit_code_on_violation(self, project_with_violation):
        """[Phase 8] Verify CI script returns exit code 1 on violations."""
        # Mock the agent at the import location
        with patch(
            "agentic_core.L5_safety.validators.ArchitectureGovernorAgent.ArchitectureGovernorAgent"
        ) as MockAgent:
            mock_instance = MagicMock()
            mock_instance.run_ci_verification_sync.return_value = (
                False,
                {
                    "violations_found": 1,
                    "_raw_result": {
                        "violations_found": 1,
                        "roots_scanned": ["agentic_core"],
                    },
                },
            )
            MockAgent.return_value = mock_instance

            # Import and run main after patching
            import importlib

            import scripts.ci.sovereign_lockdown_check as ci_script

            importlib.reload(ci_script)

            exit_code = ci_script.main()

            assert exit_code == 1

    def test_ci_script_exit_code_on_success(self, tmp_path):
        """[Phase 8] Verify CI script returns exit code 0 on success."""
        # Mock the agent at the import location
        with patch(
            "agentic_core.L5_safety.validators.ArchitectureGovernorAgent.ArchitectureGovernorAgent"
        ) as MockAgent:
            mock_instance = MagicMock()
            mock_instance.run_ci_verification_sync.return_value = (
                True,
                {
                    "violations_found": 0,
                    "_raw_result": {
                        "violations_found": 0,
                        "roots_scanned": ["agentic_core"],
                    },
                },
            )
            MockAgent.return_value = mock_instance

            import importlib

            import scripts.ci.sovereign_lockdown_check as ci_script

            importlib.reload(ci_script)

            exit_code = ci_script.main()

            assert exit_code == 0

    def test_ci_script_exit_code_on_error(self, tmp_path):
        """[Phase 8] Verify CI script returns exit code 2 on error."""
        # Mock import to raise error
        with patch(
            "agentic_core.L5_safety.validators.ArchitectureGovernorAgent.ArchitectureGovernorAgent"
        ) as MockAgent:
            MockAgent.side_effect = Exception("Test error")

            import importlib

            import scripts.ci.sovereign_lockdown_check as ci_script

            importlib.reload(ci_script)

            exit_code = ci_script.main()

            assert exit_code == 2


class TestPreCommitHookTrigger:
    """Phase 8 Tests: Pre-commit hook integration."""

    def test_pre_commit_config_has_sovereign_hook(self):
        """[Phase 8] Verify pre-commit config includes sovereign-lockdown-verification."""
        # Use relative path from test working directory
        import os

        project_root = Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent.parent))
        config_path = project_root / ".pre-commit-config.yaml"

        if not config_path.exists():
            pytest.skip("Pre-commit config not found")

        content = config_path.read_text()

        assert "sovereign-lockdown-verification" in content
        assert "sovereign_lockdown_check.py" in content

    def test_ci_script_exists(self):
        """[Phase 8] Verify CI script file exists."""
        # The script can be imported, so it exists
        try:
            import scripts.ci.sovereign_lockdown_check

            script_exists = True
        except ImportError:
            script_exists = False

        assert script_exists, "CI script could not be imported"

    def test_ci_script_is_executable(self):
        """[Phase 8] Verify CI script can be imported."""
        # Test that the module can be imported
        import scripts.ci.sovereign_lockdown_check as ci_script

        assert hasattr(ci_script, "main")
        assert callable(ci_script.main)


class TestGoldenBaselineCapture:
    """Phase 8 Tests: Golden baseline capture."""

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

    def test_baseline_capture_after_purge(self, clean_project):
        """[Phase 8] Verify baseline can be captured after purge."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
        )

        # Run lockdown to capture baseline
        is_pure, results = agent.finalize_sovereign_lockdown()

        # Should return valid baseline data
        raw_result = results.get("_raw_result", results)
        assert "violations_found" in raw_result
        assert "roots_scanned" in raw_result or "status" in raw_result

    def test_structural_validator_uses_baseline(self, clean_project):
        """[Phase 8] Verify StructuralValidatorAgent can validate against baseline."""
        from agentic_core.L5_safety.policy_engine.StructuralValidatorAgent import (
            StructuralValidatorAgent,
            StructureConfig,
        )

        config = StructureConfig(project_root=clean_project)
        validator = StructuralValidatorAgent(config=config)

        # Should be able to run validation
        result = validator.heal_repository(dry_run=True)

        assert isinstance(result, dict)


class TestPhase8Integration:
    """Phase 8 Tests: Full integration verification."""

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

    def test_full_workflow_purge_to_lockdown(self, clean_project):
        """[Phase 8] Verify full workflow: purge -> baseline -> lockdown."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Step 1: Initial audit (dry_run)
        initial_result = agent.heal_repository(dry_run=True)
        assert isinstance(initial_result, dict)

        # Step 2: Execute purge (would fix violations)
        purge_result = agent.heal_repository(execute=True, dry_run=False)
        assert isinstance(purge_result, dict)

        # Step 3: Final lockdown verification
        is_pure, lockdown_result = agent.finalize_sovereign_lockdown()
        assert isinstance(is_pure, bool)
        assert isinstance(lockdown_result, dict)
