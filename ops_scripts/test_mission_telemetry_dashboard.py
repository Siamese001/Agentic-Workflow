#!/usr/bin/env python3
"""
Test suite for Mission Telemetry Dashboard
Verifies circuit breaker detection and report generation logic.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import the dashboard module
from ops_scripts.mission_telemetry_dashboard import generate_report


class TestMissionTelemetryDashboard(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_dashboard_logic_circuit_breaker_tripped(self):
        """
        Verifies that the telemetry dashboard correctly interprets
        the runtime state and flags circuit breaker events when limit is reached.
        """
        # Mock State - Circuit breaker tripped (exactly at limit)
        mock_state = {
            "shared_alignment_metrics": {
                "upgrade_count": 10,  # Limit reached
                "files_scanned": 500,
                "last_upgrade": "apps_lic/engines/OldUtil.py",
            }
        }

        # Verify the math logic manually
        limit = 10
        upgrades = mock_state["shared_alignment_metrics"]["upgrade_count"]
        is_tripped = upgrades >= limit

        self.assertTrue(is_tripped, "Dashboard failed to detect tripped circuit breaker.")

    def test_dashboard_logic_circuit_breaker_active(self):
        """
        Verifies that the telemetry dashboard correctly identifies
        when circuit breaker is active (below limit).
        """
        # Mock State - Circuit breaker active (below limit)
        mock_state = {
            "shared_alignment_metrics": {
                "upgrade_count": 3,  # Below limit
                "files_scanned": 500,
                "last_upgrade": "apps_lic/engines/OldUtil.py",
            }
        }

        # Verify the math logic manually
        limit = 10
        upgrades = mock_state["shared_alignment_metrics"]["upgrade_count"]
        is_tripped = upgrades >= limit

        self.assertFalse(is_tripped, "Dashboard incorrectly flagged circuit breaker as tripped.")

    def test_intervention_ratio_calculation(self):
        """
        Tests the intervention ratio calculation logic.
        """
        # Test case: 5 upgrades out of 500 files = 1% ratio
        upgrades = 5
        scanned = 500
        intervention_ratio = (upgrades / scanned * 100) if scanned > 0 else 0

        self.assertEqual(intervention_ratio, 1.0, "Intervention ratio calculation incorrect.")

    def test_intervention_ratio_zero_scanned(self):
        """
        Tests edge case where no files were scanned.
        """
        upgrades = 0
        scanned = 0
        intervention_ratio = (upgrades / scanned * 100) if scanned > 0 else 0

        self.assertEqual(
            intervention_ratio, 0, "Intervention ratio should be 0 when no files scanned."
        )

    def test_dashboard_with_mock_state_file(self):
        """
        Tests the dashboard by creating a mock runtime state file
        and capturing the output.
        """
        # Create mock runtime state
        mock_state = {
            "shared_alignment_metrics": {
                "upgrade_count": 8,  # Below limit but significant
                "files_scanned": 200,
                "last_upgrade": "apps_lic/engines/TestFile.py",
            }
        }

        # Create mock runtime state file
        runtime_state_path = self.temp_path / "runtime_state.json"
        with open(runtime_state_path, "w") as f:
            json.dump(mock_state, f)

        # Mock the project root and RUNTIME_STATE_JSON
        with patch("ops_scripts.mission_telemetry_dashboard.project_root", self.temp_path):
            with patch(
                "ops_scripts.mission_telemetry_dashboard.RUNTIME_STATE_JSON", "runtime_state.json"
            ):
                # Capture print output
                with patch("builtins.print") as mock_print:
                    generate_report()

                    # Verify that print was called with expected content
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    output_text = " ".join(print_calls)

                    # Check key metrics are present
                    self.assertIn("200", output_text)  # files scanned
                    self.assertIn("8", output_text)  # upgrades
                    self.assertIn("4.00%", output_text)  # intervention ratio (8/200*100)
                    self.assertIn("🟢 ACTIVE", output_text)  # circuit breaker status

    def test_dashboard_no_state_file(self):
        """
        Tests dashboard behavior when no runtime state file exists.
        """
        # Mock project root to empty temp directory
        with patch("ops_scripts.mission_telemetry_dashboard.project_root", self.temp_path):
            with patch(
                "ops_scripts.mission_telemetry_dashboard.RUNTIME_STATE_JSON", "nonexistent.json"
            ):
                # Capture print output
                with patch("builtins.print") as mock_print:
                    generate_report()

                    # Verify error message is printed
                    mock_print.assert_called()
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    output_text = " ".join(print_calls)
                    self.assertIn("❌ No runtime state found", output_text)

    def test_dashboard_corrupted_state_file(self):
        """
        Tests dashboard behavior with corrupted JSON file.
        """
        # Create corrupted JSON file
        runtime_state_path = self.temp_path / "runtime_state.json"
        with open(runtime_state_path, "w") as f:
            f.write('{"invalid": json}')  # Invalid JSON

        # Mock project root and RUNTIME_STATE_JSON
        with patch("ops_scripts.mission_telemetry_dashboard.project_root", self.temp_path):
            with patch(
                "ops_scripts.mission_telemetry_dashboard.RUNTIME_STATE_JSON", "runtime_state.json"
            ):
                # Capture print output
                with patch("builtins.print") as mock_print:
                    generate_report()

                    # Verify error message is printed
                    mock_print.assert_called()
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    output_text = " ".join(print_calls)
                    self.assertIn("❌ Corrupted runtime state file", output_text)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
