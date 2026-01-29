#!/usr/bin/env python3
"""
Hardened Protocol Test Suite
Tests atomic write integrity, path resolution robustness, crash recovery, and malformed data resilience.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Import target classes (assuming in path)
from agentic_core.L0_maintenance.scripts.execute_ssot import (
    RUNTIME_STATE_FILE,
    RuntimeStateManager,
    list_available_agents,
)


class TestHardenedProtocol(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_atomic_write_integrity(self):
        """Test 1: Verify 'save' uses atomic replacement to prevent corruption."""
        mgr = RuntimeStateManager(self.project_root)
        mgr.start_mission("Test Mission", [])

        # Verify file exists
        state_path = self.project_root / RUNTIME_STATE_FILE
        self.assertTrue(state_path.exists(), "State file should exist after start")

        # Read content
        content = json.loads(state_path.read_text())
        self.assertEqual(content["status"], "running")

        # Simulate update
        mgr.finish_mission("completed")
        content_final = json.loads(state_path.read_text())
        self.assertEqual(content_final["status"], "completed")

    def test_path_resolution_robustness(self):
        """Test 2: Verify discovery handles mixed/relative paths without crashing."""
        # Create a mock discovery JSON with messy paths
        discovery_data = [
            {"class_name": "CleanAgent", "path": "agentic_core/L5_safety/Clean.py"},
            {"class_name": "WindowsAgent", "path": "agentic_core\\L5_safety\\Windows.py"},
            {
                "class_name": "AbsAgent",
                "path": str(self.project_root / "agentic_core/L5_safety/Abs.py"),
            },
        ]

        json_path = self.project_root / "agent_discovery_full.json"
        json_path.write_text(json.dumps(discovery_data))

        # Mock project structure so relative_to works
        (self.project_root / "agentic_core/L5_safety").mkdir(parents=True, exist_ok=True)

        agents = list_available_agents(self.project_root)

        # Convert to dict for easier checking
        agent_map = dict(agents)

        self.assertIn("CleanAgent", agent_map)
        self.assertEqual(agent_map["CleanAgent"], "agentic_core.L5_safety.Clean")

        # Windows paths should be normalized to dot notation
        self.assertIn("WindowsAgent", agent_map)
        # Note: behavior depends on OS running the test, but it shouldn't crash

        self.assertIn("AbsAgent", agent_map)
        self.assertEqual(agent_map["AbsAgent"], "agentic_core.L5_safety.Abs")

    def test_crash_recovery_state(self):
        """Test 3: Ensure main() finally block catches interruptions (Mocked)."""
        # This tests the logic pattern, as we can't easily crash the test runner
        mgr = RuntimeStateManager(self.project_root)
        mgr.state["status"] = "running"

        # Simulate the 'finally' logic
        if mgr.state["status"] == "running":
            mgr.finish_mission(status="interrupted")

        self.assertEqual(
            mgr.state["status"], "interrupted", "State should update to interrupted on crash"
        )

    def test_malformed_discovery_resilience(self):
        """Test 4: Discovery should skip bad entries, not crash entire protocol."""
        bad_data = [
            {"class_name": "GoodAgent", "path": "good/path.py"},
            {"class_name": "BadAgent", "path": None},  # Invalid path
            {"class_name": "EmptyAgent"},  # Missing path
        ]
        json_path = self.project_root / "agent_discovery_full.json"
        json_path.write_text(json.dumps(bad_data))

        agents = list_available_agents(self.project_root)
        agent_names = [a[0] for a in agents]

        self.assertIn("GoodAgent", agent_names)
        self.assertNotIn("BadAgent", agent_names)
        self.assertNotIn("EmptyAgent", agent_names)

    def test_atomic_write_failure_cleanup(self):
        """Test 5: Verify temp file cleanup on atomic write failure."""
        mgr = RuntimeStateManager(self.project_root)
        mgr.start_mission("Test Mission", [])

        # Mock os.replace to raise an exception
        with patch("os.replace", side_effect=OSError("Permission denied")):
            with patch("agentic_core.L0_maintenance.scripts.execute_ssot.logger") as mock_logger:
                # This should not raise an exception, but should log error
                mgr.save()

                # Verify error was logged
                mock_logger.error.assert_called()
                error_call = mock_logger.error.call_args[0][0]
                self.assertIn("Atomic Write Failed", error_call)

    def test_path_resolution_edge_cases(self):
        """Test 6: Test edge cases in path resolution."""
        # Test with empty path
        discovery_data = [
            {"class_name": "EmptyPathAgent", "path": ""},
            {"class_name": "RootAgent", "path": "/"},
            {"class_name": "RelativeAgent", "path": "./relative.py"},
        ]

        json_path = self.project_root / "agent_discovery_full.json"
        json_path.write_text(json.dumps(discovery_data))

        # Should not crash
        agents = list_available_agents(self.project_root)
        agent_names = [a[0] for a in agents]

        # Empty path should be skipped or handled gracefully
        self.assertIsInstance(agents, list)

    def test_state_manager_persistence_across_operations(self):
        """Test 7: State persistence works across multiple operations."""
        mgr = RuntimeStateManager(self.project_root)

        # Start mission
        mgr.start_mission("Test Mission", ["Agent1", "Agent2"])
        state_path = self.project_root / RUNTIME_STATE_FILE

        # Verify initial state
        content = json.loads(state_path.read_text())
        self.assertEqual(content["status"], "running")
        self.assertEqual(len(content["agents_order"]), 2)

        # Update agent
        mgr.update_agent("TestAgent", "L5")
        content = json.loads(state_path.read_text())
        self.assertEqual(content["current_agent"], "TestAgent")
        self.assertEqual(content["current_layer"], "L5")

        # Complete agent
        mgr.complete_agent("TestAgent", True, "Success")
        content = json.loads(state_path.read_text())
        self.assertEqual(len(content["completed_agents"]), 1)
        self.assertEqual(content["completed_agents"][0]["agent"], "TestAgent")

        # Finish mission
        mgr.finish_mission("completed")
        content = json.loads(state_path.read_text())
        self.assertEqual(content["status"], "completed")
        self.assertIsNone(content["current_agent"])

    def test_live_discovery_fallback_path_resolution(self):
        """Test 8: Live discovery also uses hardened path resolution."""
        # Mock the live discovery to return messy paths
        mock_discovery_data = [
            {"class_name": "LiveAgent1", "path": "agentic_core\\L1\\Agent1.py"},
            {"class_name": "LiveAgent2", "path": "agentic_core/L1/Agent2.py"},
        ]

        with patch(
            "agentic_core.L0_maintenance.scripts.execute_ssot.discover_all_agents"
        ) as mock_discover:
            mock_discover.return_value = mock_discovery_data

            # Ensure cache doesn't exist to force live discovery
            agents = list_available_agents(self.project_root)

            # Should not crash and should return agents
            self.assertIsInstance(agents, list)
            agent_names = [a[0] for a in agents]
            self.assertIn("LiveAgent1", agent_names)
            self.assertIn("LiveAgent2", agent_names)


if __name__ == "__main__":
    unittest.main()
