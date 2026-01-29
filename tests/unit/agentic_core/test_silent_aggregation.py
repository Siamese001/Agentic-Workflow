#!/usr/bin/env python3
"""
Test Suite for Silent Aggregation & Detailed Reporting
Verifies that the execute_ssot.py script implements the requirements:
1. Silent intermediate output
2. Comprehensive final JSON manifest
3. Markdown executive summary generation
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
from io import StringIO
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDetailedReporting(unittest.TestCase):
    def setUp(self):
        self.captured_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output

        # Mock state manager with test data
        self.state_mgr = MagicMock()
        self.state_mgr.state = {
            "compliance_report": {
                "violations": [
                    {"file": "agent.py", "type": "NAMING", "message": "Bad name"},
                    {"file": "validator.py", "type": "IMPORT", "message": "Missing import"},
                ],
                "stats": {
                    "drift_detected": 1,
                    "violations_found": 2,
                    "errors": 0,
                    "violations_fixed": 1,
                },
            },
            "compliance_scores": {"prompt_governance": 0.85},
            "decisions_made": [
                {
                    "confidence": 0.65,
                    "decision": True,
                    "reason": "Fix Naming - LOW CONFIDENCE (0.65) - LLM Override",
                },
                {
                    "confidence": 0.92,
                    "decision": True,
                    "reason": "Hierarchy Healing - HIGH CONFIDENCE (0.92)",
                },
            ],
        }
        self.state_mgr.save = MagicMock()
        self.state_mgr.update_agent = MagicMock()
        self.state_mgr.complete_agent = MagicMock()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_json_granularity(self):
        """Test 1: JSON output must include metrics, governance log, and file list."""
        # Patch stdout reconfigure to avoid error in test environment
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.reconfigure = MagicMock()

            # Import and test the function
            from agentic_core.L0_maintenance.scripts.execute_ssot import execute_phase5_final_impl

            # Execute the function
            result = execute_phase5_final_impl({}, "prompt_governance", self.state_mgr)

            # Verify structure
            self.assertIn("meta", result)
            self.assertIn("metrics", result)
            self.assertIn("governance_log", result)
            self.assertIn("unified_violations", result)
            self.assertIn("agents_executed", result)

            # Verify specific fields
            self.assertEqual(result["meta"]["territory"], "prompt_governance")
            self.assertEqual(result["meta"]["status"], "NON-COMPLIANT")
            self.assertEqual(result["metrics"]["confidence_score"], 0.85)
            self.assertEqual(result["metrics"]["violation_count"], 2)
            self.assertEqual(result["metrics"]["drift_count"], 1)

            # Verify governance log has decisions and files
            self.assertIn("decisions", result["governance_log"])
            self.assertIn("files_processed", result["governance_log"])
            self.assertEqual(len(result["governance_log"]["decisions"]), 2)
            self.assertIn("agent.py", result["governance_log"]["files_processed"])
            self.assertIn("validator.py", result["governance_log"]["files_processed"])

        print("✅ PASS: JSON Granularity")

    def test_markdown_generation(self):
        """Test 2: Output must include Markdown headers and tables."""
        # Patch stdout reconfigure to avoid error in test environment
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.reconfigure = MagicMock()

            from agentic_core.L0_maintenance.scripts.execute_ssot import execute_phase5_final_impl

            # Execute the function - capture the actual print output
            with patch("builtins.print") as mock_print:
                execute_phase5_final_impl({}, "prompt_governance", self.state_mgr)

                # Get all print calls and join them
                print_calls = [str(call[0][0]) for call in mock_print.call_args_list if call[0]]
                output = "\n".join(print_calls)

            # Check for markdown components
            self.assertIn("# 🛡️ Sovereign Compliance Report: prompt_governance", output)
            self.assertIn("## 📊 Executive Summary", output)
            self.assertIn("## 🧠 AI Governance Log", output)
            self.assertIn("| Decision Context | Confidence | LLM Triggered | Outcome |", output)
            self.assertIn("### 📂 Affected Files", output)

            # Check for decision table content
            self.assertIn("| Fix Naming", output)
            self.assertIn("| 0.65", output)
            self.assertIn("| Yes", output)  # LLM triggered for low confidence
            self.assertIn("| PROCEED", output)

            # Check for file list
            self.assertIn("* `agent.py`", output)
            self.assertIn("* `validator.py`", output)

        print("✅ PASS: Markdown Summary Generation")

    def test_silence_verification(self):
        """Test 3: Intermediate phases must NOT output JSON."""
        # Patch stdout reconfigure to avoid error in test environment
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.reconfigure = MagicMock()

            from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager

            # Create a real state manager instance
            state_mgr = RuntimeStateManager(Path.cwd())

            # Test add_event filtering
            with patch("agentic_core.L0_maintenance.scripts.execute_ssot.logger") as mock_logger:
                # Should log agent events
                state_mgr.add_event("agent_start", "→ Executing TestAgent")
                mock_logger.info.assert_called_with("→ Executing TestAgent")

                # Should log errors
                state_mgr.add_event("error", "Test error")
                mock_logger.error.assert_called_with("Test error")

                # Should log warnings
                state_mgr.add_event("warning", "Test warning")
                mock_logger.warning.assert_called_with("Test warning")

                # Should NOT log other events (they get suppressed)
                mock_logger.reset_mock()
                state_mgr.add_event("info", "This should be suppressed")
                mock_logger.info.assert_not_called()

        print("✅ PASS: Intermediate Silence Verified")

    def test_decision_engine_tracking(self):
        """Test 4: Decision engine properly tracks decisions in state."""
        # Patch stdout reconfigure to avoid error in test environment
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.reconfigure = MagicMock()

            # Clear existing decisions for clean test
            self.state_mgr.state["decisions_made"] = []

            from agentic_core.L0_maintenance.scripts.execute_ssot import (
                AutonomousDecisionEngine,
                ConfidenceScore,
            )

            # Create decision engine with state manager
            decision_engine = AutonomousDecisionEngine(enable_llm=True, state_mgr=self.state_mgr)

            # Create a test confidence score
            confidence = ConfidenceScore(value=0.65, reasoning="Test", factors={"test": 1.0})

            # Make a decision
            proceed, reason = decision_engine.should_proceed_with_healing(confidence)

            # Verify decision was stored in both places
            self.assertEqual(len(decision_engine.decisions_made), 1)
            self.assertEqual(len(self.state_mgr.state["decisions_made"]), 1)

            # Verify decision structure
            decision = self.state_mgr.state["decisions_made"][0]
            self.assertIn("confidence", decision)
            self.assertIn("decision", decision)
            self.assertIn("reason", decision)
            self.assertIn("timestamp", decision)

        print("✅ PASS: Decision Engine Tracking")

    def test_compliant_status_logic(self):
        """Test 5: Status is correctly determined by violation count."""
        # Patch stdout reconfigure to avoid error in test environment
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.reconfigure = MagicMock()

            from agentic_core.L0_maintenance.scripts.execute_ssot import execute_phase5_final_impl

            # Test compliant case (no violations)
            self.state_mgr.state["compliance_report"]["violations"] = []
            result = execute_phase5_final_impl({}, "test_territory", self.state_mgr)
            self.assertEqual(result["meta"]["status"], "COMPLIANT")

            # Reset output
            self.captured_output = StringIO()
            sys.stdout = self.captured_output

            # Test non-compliant case (has violations)
            self.state_mgr.state["compliance_report"]["violations"] = [
                {"file": "test.py", "type": "TEST"}
            ]
            result = execute_phase5_final_impl({}, "test_territory", self.state_mgr)
            self.assertEqual(result["meta"]["status"], "NON-COMPLIANT")

        print("✅ PASS: Compliant Status Logic")


if __name__ == "__main__":
    print("🧪 Running Silent Aggregation Test Suite")
    print("=" * 50)
    unittest.main(verbosity=2)
