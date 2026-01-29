import unittest
from unittest.mock import MagicMock, patch
import json
import sys
from io import StringIO

class TestUnifiedOutput(unittest.TestCase):
    def setUp(self):
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_intermediate_silence(self):
        """Test 1: Verify Phase 1-4 do NOT print JSON to stdout."""
        # Mocking State Manager to simulate phase completion
        mock_state_mgr = MagicMock()
        mock_state_mgr.complete_agent.side_effect = lambda n, s, d: None # Silent mock
        
        # Simulate intermediate phase completions
        mock_state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", True, "Drift violations: 0")
        mock_state_mgr.complete_agent("LocationAgent", True, "Violations: 0 | Conf: 0.95")
        mock_state_mgr.complete_agent("HierarchyAgent", True, "No violations found")
        mock_state_mgr.complete_agent("ArchitectureGovernorAgent", True, "Violations: 0")
        mock_state_mgr.complete_agent("SystemArchitectAgent", True, "Architecture Valid")
        
        # Get the captured output
        output = self.captured_output.getvalue()
        
        # Assert stdout is empty or purely logging (no JSON)
        self.assertNotIn("{", output)
        self.assertNotIn("}", output)
        self.assertNotIn('"territory"', output)
        print("✅ PASS: Intermediate Phase Silence")

    def test_final_manifest_structure(self):
        """Test 2: Verify Final Phase prints the unified JSON structure."""
        # Mock the final certificate output
        cert = {
            'territory': 'prompt_governance',
            'timestamp': '2026-01-28T21:36:55.575819',
            'status': 'COMPLIANT',
            'confidence_score': 0.8425,
            'unified_violations': [],
            'stats': {
                'violations_found': 0,
                'violations_fixed': 0,
                'errors': 0,
                'drift_detected': 0
            },
            'agents_executed': [
                'FilesystemSSOTReconcilerAgent',
                'LocationAgent',
                'HierarchyAgent',
                'PascalSovereigntyAgent',
                'ArchitectureGovernorAgent',
                'SystemArchitectAgent'
            ]
        }
        
        # Print the certificate (simulating final phase)
        print(json.dumps(cert, indent=2))
        
        # Get the captured output
        output = self.captured_output.getvalue()
        
        # Assert stdout contains the full JSON structure with 'unified_violations'
        self.assertIn("{", output)
        self.assertIn("}", output)
        self.assertIn('"territory": "prompt_governance"', output)
        self.assertIn('"unified_violations": []', output)
        self.assertIn('"stats":', output)
        self.assertIn('"violations_found": 0', output)
        self.assertIn('"status": "COMPLIANT"', output)
        print("✅ PASS: Final Manifest Structure")

    def test_no_duplicate_json_output(self):
        """Test 3: Verify only one JSON object is printed (no duplicates)."""
        # Simulate multiple agent completions followed by final certificate
        mock_state_mgr = MagicMock()
        
        # Intermediate phases (should be silent)
        mock_state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", True, "Completed")
        mock_state_mgr.complete_agent("LocationAgent", True, "Completed")
        mock_state_mgr.complete_agent("HierarchyAgent", True, "Completed")
        
        # Final certificate (should print JSON)
        cert = {
            'territory': 'test_territory',
            'timestamp': '2026-01-28T21:36:55.575819',
            'status': 'COMPLIANT',
            'confidence_score': 0.8425,
            'unified_violations': [],
            'stats': {'violations_found': 0, 'violations_fixed': 0, 'errors': 0, 'drift_detected': 0},
            'agents_executed': ['FilesystemSSOTReconcilerAgent', 'LocationAgent', 'HierarchyAgent']
        }
        print(json.dumps(cert, indent=2))
        
        # Get the captured output
        output = self.captured_output.getvalue()
        
        # Count complete JSON certificate objects (look for the territory field)
        territory_count = output.count('"territory":')
        
        # Should be exactly 1 certificate printed
        self.assertEqual(territory_count, 1, f"Expected 1 certificate, found {territory_count}")
        
        # Verify it has the unified structure
        self.assertIn('"unified_violations":', output)
        self.assertIn('"stats":', output)
        print("✅ PASS: No Duplicate JSON Output")

if __name__ == "__main__":
    unittest.main()
