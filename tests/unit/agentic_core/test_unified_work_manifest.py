import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent


class TestUnifiedWorkManifest(unittest.TestCase):
    def setUp(self):
        # Use real project root but enable CI mode to prevent actual file operations
        real_root = Path(__file__).parent.parent.parent
        self.agent = ArchitectureGovernorAgent(project_root=real_root, ci_mode=True)
        # Mock the base run_audit to return a clean slate by default
        self.agent.run_audit = MagicMock(
            return_value={"violations": [], "stats": {"violations_found": 0}}
        )

    @patch("agentic_core.L5_safety.validators.HierarchyAgent.HierarchyAgent.scan_root_violations")
    @patch(
        "agentic_core.L5_safety.validators.SystemArchitectAgent.SystemArchitectAgent.validate_core_architecture"
    )
    def test_complete_telemetry_ingestion(self, mock_arch, mock_hierarchy):
        """
        Test 1: Verify JSON captures work from all 3 agents (Naming, Hierarchy, Gravity).
        """
        # Setup: Hierarchy finds 1 file, Arch finds 1 circular dep
        mock_hierarchy.return_value = {"violations": [{"file": "root_agent.py"}]}
        mock_arch.return_value = {"imports_valid": False, "circular_dependencies": ["A->B->A"]}

        manifest = self.agent.comprehensive_territory_audit(
            target_territories=["prompt_governance"]
        )

        violation_types = [v["type"] for v in manifest["violations"]]
        self.assertIn("STRUCTURE", violation_types, "Must ingest HierarchyAgent findings")
        self.assertIn("GRAVITY", violation_types, "Must ingest SystemArchitect findings")
        self.assertEqual(
            manifest["stats"]["violations_found"], 2, "Total count must match sum of all agents"
        )
        print("✅ PASS: Complete Telemetry Ingestion")

    @patch("agentic_core.L5_safety.validators.HierarchyAgent.HierarchyAgent.scan_root_violations")
    def test_partial_failure_resilience(self, mock_hierarchy):
        """
        Test 2: Verify audit continues even if a sub-agent crashes (Resilience).
        """
        # Setup: HierarchyAgent crashes
        mock_hierarchy.side_effect = Exception("Hierarchy DB Locked")

        # Execution should NOT raise exception
        manifest = self.agent.comprehensive_territory_audit(
            target_territories=["prompt_governance"]
        )

        # Verify we still got a result, just without hierarchy data
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest["stats"]["violations_found"], 0)
        print("✅ PASS: Partial Failure Resilience")

    @patch("agentic_core.L5_safety.validators.HierarchyAgent.HierarchyAgent.scan_root_violations")
    @patch(
        "agentic_core.L5_safety.validators.SystemArchitectAgent.SystemArchitectAgent.validate_core_architecture"
    )
    def test_strict_scope_isolation(self, mock_arch, mock_hierarchy):
        """
        Test 3: Verify strict scope targeting does not bleed global data.
        """
        mock_hierarchy.return_value = {"violations": []}
        mock_arch.return_value = {"imports_valid": True}

        target = "prompt_governance"
        self.agent.comprehensive_territory_audit(target_territories=[target])

        # Verify sub-agents were called ONLY with the target territory
        mock_hierarchy.assert_called_with(target_territory=target)
        # Verify SystemArchitect path construction
        self.assertTrue(mock_arch.called, "SystemArchitect should be called")
        call_arg = mock_arch.call_args[0][0]
        self.assertIn(target, str(call_arg), "Architecture scan must be scoped to target")
        print("✅ PASS: Strict Scope Isolation")

    @patch("agentic_core.L5_safety.validators.HierarchyAgent.HierarchyAgent.scan_root_violations")
    @patch(
        "agentic_core.L5_safety.validators.SystemArchitectAgent.SystemArchitectAgent.validate_core_architecture"
    )
    def test_clean_room_certification(self, mock_arch, mock_hierarchy):
        """
        Test 4: Verify a perfect state returns a valid 0-violation manifest.
        """
        mock_hierarchy.return_value = {"violations": []}
        mock_arch.return_value = {"imports_valid": True}

        manifest = self.agent.comprehensive_territory_audit(
            target_territories=["prompt_governance"]
        )

        self.assertEqual(manifest["stats"]["violations_found"], 0)
        self.assertEqual(len(manifest["violations"]), 0)
        self.assertIn("target_territories", manifest)
        print("✅ PASS: Clean Room Certification")


if __name__ == "__main__":
    unittest.main()
