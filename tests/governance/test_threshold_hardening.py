#!/usr/bin/env python3
"""
Test suite for Threshold Hardening (0.7 confidence gate).
Verifies that the new threshold correctly gates actions and triggers LLM logic.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L0_maintenance.scripts.execute_ssot import ConfidenceScore, AutonomousDecisionEngine

class TestThresholdHardening(unittest.TestCase):
    def setUp(self):
        # Enable LLM for testing the trigger
        self.engine = AutonomousDecisionEngine(enable_llm=True)

    def test_high_confidence_bypass(self):
        """Test 1: Scores >= 0.8 should proceed as HIGH CONFIDENCE."""
        score = ConfidenceScore(value=0.85, reasoning="Trusted Territory")
        proceed, reason = self.engine.should_proceed_with_healing(score)
        self.assertTrue(proceed)
        self.assertIn("HIGH CONFIDENCE", reason)
        print("✅ PASS: High Confidence Bypass")

    def test_medium_confidence_bypass(self):
        """Test 2: Scores between 0.7 and 0.8 should proceed as MEDIUM CONFIDENCE."""
        score = ConfidenceScore(value=0.72, reasoning="Moderate violations")
        proceed, reason = self.engine.should_proceed_with_healing(score)
        self.assertTrue(proceed)
        self.assertIn("MEDIUM CONFIDENCE", reason)
        print("✅ PASS: Medium Confidence Bypass")

    def test_llm_trigger_at_new_threshold(self):
        """Test 3: Score of 0.69 (formerly Medium) must now trigger LLM Override."""
        score = ConfidenceScore(value=0.69, reasoning="Borderline uncertainty")
        proceed, reason = self.engine.should_proceed_with_healing(score)
        # proceed is True because enable_llm=True (it's an 'Override')
        self.assertTrue(proceed)
        self.assertIn("LLM Override", reason)
        print("✅ PASS: LLM Trigger at < 0.7")

    def test_llm_disabled_rejection(self):
        """Test 4: If LLM is disabled, a score < 0.7 must result in a hard STOP."""
        self.engine.enable_llm = False
        score = ConfidenceScore(value=0.65, reasoning="Uncertain")
        proceed, reason = self.engine.should_proceed_with_healing(score)
        self.assertFalse(proceed)
        self.assertIn("LLM Disabled", reason)
        print("✅ PASS: LLM Disabled Rejection")

    def test_exact_boundary_conditions(self):
        """Test 5: Verify exact boundary values work correctly."""
        # Test exactly 0.7 (should be MEDIUM)
        score = ConfidenceScore(value=0.7, reasoning="Exact boundary")
        proceed, reason = self.engine.should_proceed_with_healing(score)
        self.assertTrue(proceed)
        self.assertIn("MEDIUM CONFIDENCE", reason)
        
        # Test exactly 0.8 (should be HIGH)
        score = ConfidenceScore(value=0.8, reasoning="Exact boundary")
        proceed, reason = self.engine.should_proceed_with_healing(score)
        self.assertTrue(proceed)
        self.assertIn("HIGH CONFIDENCE", reason)
        
        # Test just below 0.7 (should trigger LLM)
        score = ConfidenceScore(value=0.699, reasoning="Just below boundary")
        proceed, reason = self.engine.should_proceed_with_healing(score)
        self.assertTrue(proceed)
        self.assertIn("LLM Override", reason)
        
        print("✅ PASS: Exact Boundary Conditions")

    def test_decision_tracking(self):
        """Test 6: Verify decisions are properly tracked."""
        score = ConfidenceScore(value=0.85, reasoning="Test tracking")
        initial_count = len(self.engine.decisions_made)
        
        proceed, reason = self.engine.should_proceed_with_healing(score)
        
        self.assertEqual(len(self.engine.decisions_made), initial_count + 1)
        last_decision = self.engine.decisions_made[-1]
        self.assertEqual(last_decision['confidence'], 0.85)
        self.assertTrue(last_decision['decision'])
        self.assertIn("HIGH CONFIDENCE", last_decision['reason'])
        
        print("✅ PASS: Decision Tracking")

if __name__ == "__main__":
    print("🧪 Running Threshold Hardening Test Suite")
    print("=" * 50)
    unittest.main(verbosity=2)
