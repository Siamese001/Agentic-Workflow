import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent


class TestGovernorRefinements(unittest.TestCase):
    def setUp(self):
        self.agent = ArchitectureGovernorAgent(project_root=Path("C:/Fake"), ci_mode=True)
        self.agent._get_structure_validator = MagicMock()

    def test_naming_exception_filtering(self):
        """
        Test 1: Verify that 'DuplicatePromptError' is IGNORED, but 'BadNameClass' is CAUGHT.
        """
        # Mock Validator Report with mixed violations
        mock_report = MagicMock()
        mock_report.violations = [
            MagicMock(
                message="Class 'DuplicatePromptError' in agent file must end with 'Agent'",
                violation_type=MagicMock(name="NAMING"),
            ),
            MagicMock(
                message="Class 'BadNameClass' in agent file must end with 'Agent'",
                violation_type=MagicMock(name="NAMING"),
            ),
        ]
        self.agent._get_structure_validator().validate_structure.return_value = mock_report

        # Mock the path existence check
        with patch("pathlib.Path.exists", return_value=True):
            # Run Audit with valid territory
            # Note: We must mock _check_baseline_drift to avoid FS errors
            with patch.object(self.agent, "_check_baseline_drift", return_value=[]):
                results = self.agent.run_audit(target_territories=["agentic_core"])

        # Assertions
        # Should filter out the Error class, leaving only BadNameClass
        self.assertEqual(
            results["stats"]["violations_found"], 1, "Should filter out Exception class violation"
        )
        # Verify the remaining violation is the legitimate one
        violations = results.get("violations", [])
        self.assertEqual(len(violations), 1)
        self.assertIn("BadNameClass", violations[0]["message"])
        print("✅ PASS: Naming Exception Filtering")

    def test_healing_plan_structure_awareness(self):
        """
        Test 2: Verify generate_healing_plan creates specific actions for STRUCTURE violations.
        """
        # Mock a unified manifest with Structure violations
        manifest = {
            "stats": {"violations_found": 1, "drift_detected": 0, "errors": 0},
            "target_territories": ["prompt_governance"],
            "violations": [{"type": "STRUCTURE", "file": "root.py", "message": "Wrong place"}],
        }

        plan = self.agent.generate_healing_plan(manifest)

        self.assertTrue(plan["requires_healing"])
        self.assertIn("Relocate Root Files to SSOT Subfolders", plan["actions"])
        self.assertEqual(len(plan["structure_fixes"]), 1)
        print("✅ PASS: Healing Plan Structure Awareness")

    def test_healing_plan_no_violations(self):
        """
        Test 3: Verify clean report generates no-op plan.
        """
        manifest = {
            "stats": {"violations_found": 0, "drift_detected": 0, "errors": 0},
            "target_territories": ["prompt_governance"],
            "violations": [],
        }

        plan = self.agent.generate_healing_plan(manifest)

        self.assertFalse(plan["requires_healing"])
        self.assertIn("No healing required - system is compliant", plan["actions"])
        print("✅ PASS: Healing Plan No-Op")

    def test_naming_filter_edge_cases(self):
        """
        Test 4: Verify filter handles single quotes and variations.
        """
        mock_report = MagicMock()
        mock_report.violations = [
            MagicMock(
                message="Class 'MyCustomException' in agent file must end with 'Agent'",
                violation_type=MagicMock(name="NAMING"),
            ),
            MagicMock(
                message="Class 'RealAgent' in agent file must end with 'Agent'",
                violation_type=MagicMock(name="NAMING"),
            ),  # Should be caught if logic allows (logic assumes standard msg)
        ]
        self.agent._get_structure_validator().validate_structure.return_value = mock_report

        # Mock the path existence check
        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(self.agent, "_check_baseline_drift", return_value=[]):
                results = self.agent.run_audit(target_territories=["agentic_core"])

        # Only 'RealAgent' implies a violation here (assuming the mock msg implies it failed check)
        # The Exception one should be filtered.
        self.assertEqual(results["stats"]["violations_found"], 1)
        violations = results.get("violations", [])
        self.assertEqual(len(violations), 1)
        self.assertIn("RealAgent", violations[0]["message"])
        print("✅ PASS: Naming Filter Edge Cases")


if __name__ == "__main__":
    unittest.main()
