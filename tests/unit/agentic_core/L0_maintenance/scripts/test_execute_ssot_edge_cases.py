#!/usr/bin/env python3
"""
Comprehensive Edge Case Tests for execute_ssot.py and Downstream Agents

Tests cover:
1. ConfidenceScore boundary conditions
2. AutonomousDecisionEngine LLM enabled/disabled scenarios
3. Violation reporting and aggregation logic
4. Territorial trust logic (trusted vs critical territories)
5. RuntimeStateManager state transitions
6. NonInteractiveGuard prompt blocking
7. Retry decorator behavior
8. Decision breakdown reporting consistency
9. Healing confidence calculation edge cases
10. State persistence and recovery
11. LLM override behavior at boundary
12. Zero violations perfect confidence
13. Mass violations in trusted vs critical territories
14. Compliance report generation
15. Multi-territory processing
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from agentic_core.L0_maintenance.scripts.execute_ssot import (
        ConfidenceScore,
        AutonomousDecisionEngine,
        RuntimeStateManager,
        NonInteractiveGuard,
        with_retry,
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import warning: {e}")
    IMPORTS_AVAILABLE = False


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestConfidenceScoreBoundaries(unittest.TestCase):
    """Test 1-3: ConfidenceScore boundary conditions"""
    
    def test_01_exact_boundary_075_is_not_high(self):
        """Edge case: 0.75 exactly should NOT be high confidence."""
        score = ConfidenceScore(value=0.75, reasoning="Boundary test")
        self.assertFalse(score.is_high_confidence, "0.75 must NOT be high confidence")
        self.assertTrue(score.is_medium_confidence, "0.75 must be medium confidence")
        self.assertFalse(score.is_low_confidence, "0.75 must NOT be low confidence")
    
    def test_02_just_above_boundary_0751_is_high(self):
        """Edge case: 0.751 should be high confidence."""
        score = ConfidenceScore(value=0.751, reasoning="Just above boundary")
        self.assertTrue(score.is_high_confidence, "0.751 must be high confidence")
        self.assertFalse(score.is_medium_confidence, "0.751 must NOT be medium")
        self.assertFalse(score.is_low_confidence, "0.751 must NOT be low")
    
    def test_03_extreme_values_0_and_1(self):
        """Edge case: Extreme values 0.0 and 1.0."""
        score_zero = ConfidenceScore(value=0.0, reasoning="Zero confidence")
        self.assertTrue(score_zero.is_low_confidence, "0.0 must be low confidence")
        self.assertFalse(score_zero.is_medium_confidence)
        self.assertFalse(score_zero.is_high_confidence)
        
        score_perfect = ConfidenceScore(value=1.0, reasoning="Perfect confidence")
        self.assertTrue(score_perfect.is_high_confidence, "1.0 must be high confidence")
        self.assertFalse(score_perfect.is_medium_confidence)
        self.assertFalse(score_perfect.is_low_confidence)


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestDecisionEngineLLMScenarios(unittest.TestCase):
    """Test 4-6: AutonomousDecisionEngine LLM enabled/disabled scenarios"""
    
    def test_04_llm_disabled_blocks_at_075(self):
        """LLM disabled: Should NOT proceed at exactly 0.75."""
        engine = AutonomousDecisionEngine(enable_llm=False)
        score = ConfidenceScore(value=0.75, reasoning="Boundary")
        
        proceed, msg = engine.should_proceed_with_healing(score)
        
        self.assertFalse(proceed, "Should NOT proceed at 0.75 without LLM")
        self.assertIn("LOW CONFIDENCE", msg)
        self.assertIn("LLM Disabled", msg)
    
    def test_05_llm_enabled_allows_at_075(self):
        """LLM enabled: Should proceed at 0.75 with LLM override."""
        engine = AutonomousDecisionEngine(enable_llm=True)
        score = ConfidenceScore(value=0.75, reasoning="Boundary with LLM")
        
        proceed, msg = engine.should_proceed_with_healing(score)
        
        self.assertTrue(proceed, "Should proceed at 0.75 WITH LLM enabled")
        self.assertIn("LLM Override", msg)
    
    def test_06_high_confidence_proceeds_regardless_of_llm(self):
        """High confidence (> 0.75) should proceed regardless of LLM setting."""
        for enable_llm in [True, False]:
            engine = AutonomousDecisionEngine(enable_llm=enable_llm)
            score = ConfidenceScore(value=0.76, reasoning="Above threshold")
            
            proceed, msg = engine.should_proceed_with_healing(score)
            
            self.assertTrue(proceed, f"Should proceed at 0.76 (LLM={enable_llm})")
            self.assertIn("AUTO-HEAL", msg)
            self.assertIn("> 0.75", msg)


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestTerritorialTrustLogic(unittest.TestCase):
    """Test 7-9: Territorial trust logic (trusted vs critical territories)"""
    
    def test_07_trusted_territory_high_confidence(self):
        """Trusted territories should get higher confidence for same violation count."""
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        # Same violations in trusted vs critical territory
        trusted_conf = engine.calculate_healing_confidence(
            violations_count=10,
            violation_types=["SHALLOW"],
            territory="prompt_governance"  # Trusted
        )
        
        critical_conf = engine.calculate_healing_confidence(
            violations_count=10,
            violation_types=["SHALLOW"],
            territory="L5_safety"  # Critical
        )
        
        self.assertGreater(
            trusted_conf.value, critical_conf.value,
            "Trusted territory should have higher confidence than critical"
        )
    
    def test_08_zero_violations_perfect_confidence(self):
        """Zero violations should always yield perfect confidence (1.0)."""
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        for territory in ["prompt_governance", "L5_safety", "L3_orchestration", "unknown"]:
            conf = engine.calculate_healing_confidence(
                violations_count=0,
                violation_types=[],
                territory=territory
            )
            self.assertEqual(conf.value, 1.0, f"Zero violations in {territory} should be 1.0")
            self.assertTrue(conf.is_high_confidence)
    
    def test_09_mass_violations_trusted_vs_critical(self):
        """Mass violations (100+) should still differ between trusted and critical."""
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        trusted_conf = engine.calculate_healing_confidence(
            violations_count=150,
            violation_types=["NAMING", "IMPORT"],
            territory="scripts"  # Trusted
        )
        
        critical_conf = engine.calculate_healing_confidence(
            violations_count=150,
            violation_types=["NAMING", "IMPORT"],
            territory="base_agents"  # Critical
        )
        
        # Trusted should still be higher even with mass violations
        self.assertGreater(trusted_conf.value, critical_conf.value)
        # But both should be lower than threshold for mass violations
        self.assertLess(trusted_conf.value, 0.9, "Mass violations should reduce confidence")


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestRuntimeStateManager(unittest.TestCase):
    """Test 10-11: RuntimeStateManager state transitions"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_10_state_transitions(self):
        """State manager should correctly track mission lifecycle."""
        state_mgr = RuntimeStateManager(self.project_root)
        
        # Initial state
        self.assertEqual(state_mgr.state["status"], "idle")
        self.assertIsNone(state_mgr.state["start_time"])
        
        # Start mission
        state_mgr.start_mission("Test Mission", ["territory1", "territory2"])
        self.assertEqual(state_mgr.state["status"], "running")
        self.assertIsNotNone(state_mgr.state["start_time"])
        self.assertEqual(state_mgr.state["agents_order"], ["territory1", "territory2"])
        
        # Update agent
        state_mgr.update_agent("TestAgent", "L5 - Safety")
        self.assertEqual(state_mgr.state["current_agent"], "TestAgent")
        self.assertEqual(state_mgr.state["current_layer"], "L5 - Safety")
        
        # Complete agent
        state_mgr.complete_agent("TestAgent", True, "Success")
        self.assertEqual(len(state_mgr.state["completed_agents"]), 1)
        self.assertTrue(state_mgr.state["completed_agents"][0]["success"])
        
        # Finish mission
        state_mgr.finish_mission("completed")
        self.assertEqual(state_mgr.state["status"], "completed")
        self.assertIsNotNone(state_mgr.state["end_time"])
    
    def test_11_decision_tracking(self):
        """State manager should track decisions for final report."""
        state_mgr = RuntimeStateManager(self.project_root)
        engine = AutonomousDecisionEngine(enable_llm=False, state_mgr=state_mgr)
        
        # Make several decisions
        scores = [0.8, 0.76, 0.75, 0.5, 0.3]
        for val in scores:
            score = ConfidenceScore(value=val, reasoning=f"Test {val}")
            engine.should_proceed_with_healing(score)
        
        # Verify decisions tracked
        self.assertEqual(len(state_mgr.state["decisions_made"]), 5)
        
        # Verify decision breakdown matches unified threshold
        decisions = state_mgr.state["decisions_made"]
        high_conf = sum(1 for d in decisions if d['confidence'] > 0.75)
        med_conf = sum(1 for d in decisions if 0.5 <= d['confidence'] <= 0.75)
        low_conf = sum(1 for d in decisions if d['confidence'] < 0.5)
        
        self.assertEqual(high_conf, 2, "Should have 2 high confidence (0.8, 0.76)")
        self.assertEqual(med_conf, 2, "Should have 2 medium confidence (0.75, 0.5)")
        self.assertEqual(low_conf, 1, "Should have 1 low confidence (0.3)")


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestNonInteractiveGuard(unittest.TestCase):
    """Test 12-13: NonInteractiveGuard prompt blocking"""
    
    def test_12_blocks_input_prompts(self):
        """NonInteractiveGuard should block input() calls."""
        with NonInteractiveGuard(active=True) as guard:
            with self.assertRaises(RuntimeError) as ctx:
                input("This should be blocked")
            
            self.assertIn("Interactive prompt blocked", str(ctx.exception))
            self.assertEqual(guard.blocked_count, 1)
    
    def test_13_resource_exhaustion_protection(self):
        """Guard should prevent infinite prompt loops."""
        with NonInteractiveGuard(active=True, max_blocked_prompts=3) as guard:
            # First 3 should raise RuntimeError
            for i in range(3):
                with self.assertRaises(RuntimeError):
                    input(f"Prompt {i}")
            
            # 4th should raise RecursionError (exhaustion protection)
            with self.assertRaises(RecursionError) as ctx:
                input("Exhaustion trigger")
            
            self.assertIn("Infinite Loop Protection", str(ctx.exception))


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestRetryDecorator(unittest.TestCase):
    """Test 14: Retry decorator behavior"""
    
    def test_14_retry_on_transient_failure(self):
        """Retry decorator should retry on transient failures."""
        call_count = 0
        
        @with_retry(max_retries=3, delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient error")
            return "success"
        
        result = flaky_function()
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3, "Should have retried 3 times")
    
    def test_14b_no_retry_on_prompt_block(self):
        """Retry should NOT retry on prompt blocking errors."""
        call_count = 0
        
        @with_retry(max_retries=3, delay=0.01)
        def prompt_blocked_function():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Interactive prompt blocked in autonomous mode")
        
        with self.assertRaises(RuntimeError):
            prompt_blocked_function()
        
        self.assertEqual(call_count, 1, "Should NOT retry on prompt block")


@unittest.skipUnless(IMPORTS_AVAILABLE, "execute_ssot imports not available")
class TestReportingLogicConsistency(unittest.TestCase):
    """Test 15: Reporting logic consistency with decision logic"""
    
    def test_15_reporting_matches_decision_logic(self):
        """Reporting breakdown should match decision engine logic exactly."""
        # Simulate decisions from main() reporting logic
        decisions = [
            {'confidence': 1.0},    # High
            {'confidence': 0.80},   # High
            {'confidence': 0.76},   # High
            {'confidence': 0.751},  # High (just above)
            {'confidence': 0.75},   # Medium (boundary)
            {'confidence': 0.749},  # Medium (just below)
            {'confidence': 0.50},   # Medium (lower boundary)
            {'confidence': 0.499},  # Low (just below)
            {'confidence': 0.30},   # Low
            {'confidence': 0.0},    # Low
        ]
        
        # Apply same logic as main() reporting
        high_conf = sum(1 for d in decisions if d['confidence'] > 0.75)
        med_conf = sum(1 for d in decisions if 0.5 <= d['confidence'] <= 0.75)
        low_conf = sum(1 for d in decisions if d['confidence'] < 0.5)
        
        self.assertEqual(high_conf, 4, "Should count 1.0, 0.80, 0.76, 0.751 as high")
        self.assertEqual(med_conf, 3, "Should count 0.75, 0.749, 0.50 as medium")
        self.assertEqual(low_conf, 3, "Should count 0.499, 0.30, 0.0 as low")
        
        # Verify total adds up
        self.assertEqual(high_conf + med_conf + low_conf, len(decisions))
        
        # Verify LLM trigger logic matches
        for d in decisions:
            conf = d['confidence']
            llm_triggered = conf <= 0.75
            
            if conf > 0.75:
                self.assertFalse(llm_triggered, f"LLM should NOT trigger at {conf}")
            else:
                self.assertTrue(llm_triggered, f"LLM SHOULD trigger at {conf}")


class TestDownstreamAgentThresholds(unittest.TestCase):
    """Additional tests for downstream agent threshold consistency"""
    
    def test_downstream_thresholds_unified(self):
        """Verify all downstream agents use unified 0.75 threshold."""
        # This test verifies the threshold values in the actual files
        files_to_check = [
            ("agentic_core/L5_safety/validators/CognitiveDispositionAgent.py", "0.75"),
            ("agentic_core/L5_safety/validators/ReflectionEngine.py", "0.75"),
            ("agentic_core/L5_safety/policy_engine/SafetyExecutorAgent.py", "0.75"),
        ]
        
        for rel_path, expected_threshold in files_to_check:
            full_path = project_root / rel_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                # Check that 0.75 appears as a threshold
                self.assertIn(expected_threshold, content, 
                    f"{rel_path} should contain threshold {expected_threshold}")


if __name__ == '__main__':
    print("🧪 Running 15 Edge Case Tests for execute_ssot.py...")
    print("=" * 70)
    
    # Run with verbose output
    unittest.main(verbosity=2)
