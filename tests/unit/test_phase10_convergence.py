"""Phase 10 Tests: Sovereign Convergence & Categorical Drift Audits.

Tests for convergence flow, categorical audit precision, and sentinel deployment integrity.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestSovereignConvergenceFlow:
    """Phase 10 Tests: Sovereign convergence flow verification."""

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

    def test_execute_sovereign_convergence_method_exists(self, tmp_path):
        """[Phase 10] Verify execute_sovereign_convergence method exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        assert hasattr(agent, "execute_sovereign_convergence")
        assert callable(agent.execute_sovereign_convergence)

    def test_sovereign_convergence_flow(self, clean_project):
        """[Phase 10] Verify convergence purges all drift and achieves final_purity."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        initial_debt = 2160
        call_count = [0]

        # Mock heal_repository to simulate purge then clean verification
        def mock_heal(*args, **kwargs):
            call_count[0] += 1
            execute = kwargs.get("execute", False)
            dry_run = kwargs.get("dry_run", True)

            if execute and not dry_run:
                # Purge execution - fix all violations
                return {
                    "violations_found": initial_debt,
                    "violations_fixed": initial_debt,
                    "status": "PASS",
                    "_raw_result": {
                        "violations_found": initial_debt,
                        "violations_fixed": initial_debt,
                    },
                }
            else:
                # Post-purge verification - clean state
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

        # Execute convergence
        result = agent.execute_sovereign_convergence()

        # Verify results
        assert "purge_status" in result
        assert "lockdown_status" in result
        assert "final_purity" in result

        purge_raw = result["purge_status"].get("_raw_result", result["purge_status"])
        assert purge_raw.get("violations_fixed", 0) == initial_debt
        assert result["final_purity"] is True

    def test_convergence_returns_correct_structure(self, clean_project):
        """[Phase 10] Verify convergence returns expected dictionary structure."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
        )

        # Mock clean state
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "_raw_result": {"violations_found": 0, "violations_fixed": 0},
            }

        agent.heal_repository = mock_heal

        result = agent.execute_sovereign_convergence()

        assert isinstance(result, dict)
        assert "purge_status" in result
        assert "lockdown_status" in result
        assert "final_purity" in result
        assert isinstance(result["final_purity"], bool)


class TestCategoricalAuditPrecision:
    """Phase 10 Tests: Categorical audit precision verification."""

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

    def test_log_categorical_drift_method_exists(self, tmp_path):
        """[Phase 10] Verify _log_categorical_drift method exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        assert hasattr(agent, "_log_categorical_drift")
        assert callable(agent._log_categorical_drift)

    def test_categorical_audit_precision(self, clean_project):
        """[Phase 10] Verify drift analysis correctly categorizes violations."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        # Create test violations - 1 of each type
        violations = [
            {"type": "GRAVITY", "message": "L3 importing L5"},
            {"type": "NAMING", "message": "Missing Agent suffix"},
            {"type": "ORPHAN", "message": "File not in registry"},
        ]

        report = agent._log_categorical_drift(violations)

        assert report["GRAVITY"] == 1
        assert report["NAMING"] == 1
        assert report["ORPHAN"] == 1
        assert report["DUPLICATE"] == 0

    def test_categorical_audit_with_object_violations(self, clean_project):
        """[Phase 10] Verify drift analysis handles object violations."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        # Create mock violation objects
        mock_violation = MagicMock()
        mock_violation.violation_type = MagicMock()
        mock_violation.violation_type.name = "GRAVITY"

        violations = [mock_violation]

        report = agent._log_categorical_drift(violations)

        assert report["GRAVITY"] == 1

    def test_categorical_audit_handles_unknown_types(self, clean_project):
        """[Phase 10] Verify drift analysis handles unknown violation types."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        violations = [
            {"type": "UNKNOWN_TYPE", "message": "Unknown violation"},
            {"type": "CUSTOM", "message": "Custom violation"},
        ]

        report = agent._log_categorical_drift(violations)

        # Unknown types should go to OTHER
        assert report["OTHER"] == 2

    def test_categorical_audit_returns_dict(self, clean_project):
        """[Phase 10] Verify drift analysis returns dictionary."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        report = agent._log_categorical_drift([])

        assert isinstance(report, dict)
        assert "GRAVITY" in report
        assert "NAMING" in report
        assert "ORPHAN" in report
        assert "DUPLICATE" in report
        assert "OTHER" in report


class TestSentinelDeploymentIntegrity:
    """Phase 10 Tests: Sentinel deployment integrity verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    def test_sentinel_deployment_integrity(self, clean_project):
        """[Phase 10] Verify CI script blocks invalid files post-convergence."""
        # Mock the agent to return violations for invalid file
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
                        "violations": [
                            {"type": "ORPHAN", "message": "Invalid file in agentic_core"}
                        ],
                    },
                },
            )
            MockAgent.return_value = mock_instance

            import importlib

            import scripts.ci.sovereign_lockdown_check as ci_script

            importlib.reload(ci_script)

            exit_code = ci_script.main()

            # Should block with non-zero exit code
            assert exit_code != 0

    def test_sentinel_allows_valid_state(self, clean_project):
        """[Phase 10] Verify CI script allows valid state post-convergence."""
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

            # Should allow with exit code 0
            assert exit_code == 0


class TestPhase10ConvergenceIntegration:
    """Phase 10 Tests: Full convergence integration verification."""

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

    def test_full_convergence_workflow(self, clean_project):
        """[Phase 10] Verify full convergence workflow end-to-end."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Mock clean state
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "_raw_result": {"violations_found": 0, "violations_fixed": 0},
            }

        agent.heal_repository = mock_heal

        # Execute full convergence
        result = agent.execute_sovereign_convergence()

        # Verify final purity
        assert result["final_purity"] is True

    def test_convergence_with_remaining_violations(self, clean_project):
        """[Phase 10] Verify convergence reports remaining violations."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Mock state with remaining violations
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 10,
                "violations_fixed": 5,
                "_raw_result": {"violations_found": 10, "violations_fixed": 5},
            }

        agent.heal_repository = mock_heal

        result = agent.execute_sovereign_convergence()

        # Should report incomplete convergence
        assert result["final_purity"] is False
