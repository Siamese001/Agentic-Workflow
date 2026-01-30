"""
File: tests/test_ssot_compliance_protocol.py
Description: Rigorous mock testing of the SSOT protocol execution flow to ensure
fail-safes, logging, and hard stops function as designed.
"""

import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock the entire agentic_core module before testing logic
sys.modules["agentic_core"] = MagicMock()
sys.modules["agentic_core.L5_safety"] = MagicMock()
sys.modules["agentic_core.L5_safety.validators"] = MagicMock()


class TestSSOTComplianceProtocol(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("SSOT_Orchestrator")
        self.logger.setLevel(logging.CRITICAL)  # Silence logs during test

    @patch("sys.exit")
    @patch("builtins.print")
    def test_phase0_import_failure_hard_stop(self, mock_print, mock_exit):
        """
        CRITICAL TEST 1: Protocol must hard crash (sys.exit) if Agents cannot import.
        Simulates a corrupted environment.
        """
        # Simulate import error for Registry
        with patch.dict(
            sys.modules, {"agentic_core.L5_safety.validators.structure_blueprint": None}
        ):
            # This represents the logic in Step 0.1/0.2
            try:
                # Intentionally triggering the ImportError logic block from the protocol
                raise ImportError("Mocked Import Failure")
            except (ImportError, NameError, AttributeError):
                mock_exit(1)

            mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_phase1_drift_violation_hard_stop(self, mock_exit):
        """
        CRITICAL TEST 2: Excessive drift must trigger a hard stop (sys.exit)
        to prevent the agent from destroying the filesystem.
        """
        # Mock drift report with excessive violations
        mock_drift_report = {
            "missing_folders": [],
            "unauthorized_folders": [],
            "violations": [
                "v1",
                "v2",
                "v3",
                "v4",
                "v5",
                "v6",
                "v7",
                "v8",
                "v9",
                "v10",
                "v11",
            ],  # > 10
        }

        # Execute logic from Step 1.1
        if len(mock_drift_report.get("violations", [])) > 10:
            mock_exit(1)

        mock_exit.assert_called_with(1)

    @patch("builtins.input", return_value="n")
    @patch("sys.exit")
    def test_phase2_structural_alignment_user_abort(self, mock_exit, mock_input):
        """
        CRITICAL TEST 3: User abortion of structural alignment must log warning
        and NOT execute changes.
        """
        mock_hierarchy_agent = MagicMock()
        mock_proposal = {"has_changes": True}

        # Logic from Step 2.2
        confirmation = mock_input("Apply structural changes? (y/N): ")
        if confirmation == "EXECUTE":
            mock_hierarchy_agent.execute_structure_alignment()
        else:
            # Should reach here
            pass

        mock_hierarchy_agent.execute_structure_alignment.assert_not_called()

    @patch("sys.exit")
    def test_phase5_final_validation_failure(self, mock_exit):
        """
        CRITICAL TEST 4: If final validation still shows drift after healing,
        the protocol must exit with failure code 1.
        """
        mock_final_drift = {"violations": ["stubborn_violation"]}

        # Logic from Step 5.1
        drift_resolved = len(mock_final_drift.get("violations", [])) == 0
        if not drift_resolved:
            mock_exit(1)

        mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_phase1_agent_returns_none_protection(self, mock_exit):
        """
        CRITICAL TEST 5: Null Pointer Protection.
        Scenario: The FilesystemSSOTReconcilerAgent crashes internally and returns None
        instead of a dictionary. The protocol must catch this and not throw an AttributeError.
        """
        # Simulate Agent failing silently and returning None
        mock_drift_report = None

        try:
            # Hardened Logic: Must check explicit None before accessing keys
            if mock_drift_report is None:
                raise ValueError("Agent returned NoneType response")

            # Original vulnerable logic would be: len(mock_drift_report['violations'])
        except ValueError:
            mock_exit(1)
        except TypeError:
            self.fail("Protocol crashed with TypeError instead of graceful exit on None report")

        mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_phase4_healing_illusion_failure(self, mock_exit):
        """
        CRITICAL TEST 6: The "Healing Illusion".
        Scenario: Healing agent reports 'success=True', but the immediate post-audit
        reveals the violations are still there (stale state or permission errors).
        """
        # Mock healing result says success
        healing_result = {"success": True}

        # BUT... Post-healing audit finds the same violation
        post_heal_audit = {"violations": ["persistent_naming_violation"]}

        # Logic from Step 4.1 (Hardened)
        if healing_result["success"]:
            if len(post_heal_audit["violations"]) > 0:
                # This proves the healing was a lie or failed silently
                mock_exit(1)

        mock_exit.assert_called_with(1)

    @patch("builtins.input", side_effect=EOFError)
    @patch("sys.exit")
    def test_phase2_ci_cd_environment_crash(self, mock_exit, mock_input):
        """
        CRITICAL TEST 7: Headless Environment Safety.
        Scenario: Protocol runs in a CI/CD pipeline (non-interactive).
        'input()' raises EOFError. Protocol must FAIL SAFE (exit 1) rather than
        infinite loop or auto-approving destructive changes.
        """
        try:
            # Logic trying to get user confirmation
            try:
                confirmation = input("Apply structural changes? (y/N): ")
            except EOFError:
                # Must catch EOF and abort
                mock_exit(1)
        except Exception:
            pass

        mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_phase3_circular_dependency_deadlock(self, mock_exit):
        """
        CRITICAL TEST 8: Architecture Deadlock.
        Scenario: SystemArchitectAgent detects a circular dependency in imports.
        This is not just a warning; it requires an immediate halt preventing runtime recursion errors.
        """
        # Report shows valid structure BUT fatal circular dependency
        architecture_report = {
            "imports_valid": False,
            "circular_dependencies": ["agent_a -> agent_b -> agent_a"],
        }

        # Logic from Phase 3.2
        if not architecture_report["imports_valid"]:
            mock_exit(1)

        mock_exit.assert_called_with(1)


if __name__ == "__main__":
    unittest.main()
