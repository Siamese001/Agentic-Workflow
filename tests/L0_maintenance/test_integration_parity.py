#!/usr/bin/env python3
"""
Integration Parity Tests for Phase 4 Deep Integration
Validates that execute_ssot.py has feature parity with Canon Validator
"""

import unittest
import json
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L0_maintenance.scripts.execute_ssot import (
    RuntimeStateManager,
    try_summon_orchestrator,
    ConfidenceScore,
    AutonomousDecisionEngine
)

class TestIntegrationParity(unittest.TestCase):
    """Test suite for Phase 4 integration features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_root = self.test_dir
        
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_meta_learning_state_update(self):
        """Test 1: Verify meta-learning metrics can be updated and persisted."""
        mgr = RuntimeStateManager(self.project_root)
        
        # Initial state check
        self.assertFalse(mgr.state["meta_learning"]["enabled"])
        self.assertEqual(mgr.state["meta_learning"]["total_experiences"], 0)
        
        # Update with experience data
        experience = {
            "total_experiences": 42,
            "strategy_weights": {"cot": 1.5, "react": 0.8, "tot": 1.2},
            "experience": "Test Success - L3 Mission Complete"
        }
        
        # Mock save to avoid disk writes in test
        mgr.save = MagicMock()
        mgr.update_meta_learning(experience)
        
        # Verify state updated correctly
        ml = mgr.state["meta_learning"]
        self.assertTrue(ml["enabled"])
        self.assertEqual(ml["total_experiences"], 42)
        self.assertEqual(ml["strategy_weights"]["cot"], 1.5)
        self.assertEqual(ml["strategy_weights"]["react"], 0.8)
        self.assertEqual(ml["recent_experiences"][0], "Test Success - L3 Mission Complete")
        
        # Verify save was called
        mgr.save.assert_called_once()
    
    def test_meta_learning_recent_experiences_limit(self):
        """Test 2: Verify recent experiences are limited to 5 items."""
        mgr = RuntimeStateManager(self.project_root)
        mgr.save = MagicMock()
        
        # Add 7 experiences
        for i in range(7):
            mgr.update_meta_learning({
                "experience": f"Experience {i}",
                "total_experiences": i
            })
        
        # Should only keep last 5
        self.assertEqual(len(mgr.state["meta_learning"]["recent_experiences"]), 5)
        self.assertEqual(mgr.state["meta_learning"]["recent_experiences"][0], "Experience 6")
        self.assertEqual(mgr.state["meta_learning"]["recent_experiences"][-1], "Experience 2")
    
    def test_l3_orchestrator_fallback_on_import_error(self):
        """Test 3: Verify fallback to L5 when L3 Orchestrator is missing."""
        # Force ImportError by patching sys.modules
        with patch.dict(sys.modules, {'agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent': None}):
            success, result = try_summon_orchestrator(self.project_root, ["target"], True)
            
        self.assertFalse(success, "Should report failure when L3 not available")
        self.assertIsNone(result, "Should return None result when L3 not available")
    
    def test_l3_orchestrator_success_delegation(self):
        """Test 4: Verify successful delegation to L3."""
        # Mock the entire L3 module structure
        mock_orch_module = MagicMock()
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_mission.return_value = {
            "status": "L3_SUCCESS",
            "territories_processed": 4,
            "experiences": 2
        }
        mock_orch_module.get_consolidated_orchestrator.return_value = mock_orch_instance
        
        # Mock L5 dependencies to prevent ImportErrors
        mock_l5 = MagicMock()
        
        modules = {
            'agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent': mock_orch_module,
            'agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent': mock_l5,
            'agentic_core.L5_safety.validators.LocationAgent': mock_l5,
            'agentic_core.L5_safety.validators.HierarchyAgent': mock_l5,
            'agentic_core.L5_safety.validators.ArchitectureGovernorAgent': mock_l5,
            'agentic_core.L5_safety.validators.SystemArchitectAgent': mock_l5
        }
        
        with patch.dict(sys.modules, modules):
            success, result = try_summon_orchestrator(self.project_root, ["target1", "target2"], True)
            
        self.assertTrue(success, "Should succeed when L3 is available")
        self.assertEqual(result["status"], "L3_SUCCESS")
        mock_orch_instance.run_mission.assert_called_once()
        
        # Verify the mission context was passed correctly
        call_args = mock_orch_instance.run_mission.call_args
        self.assertEqual(call_args[0][0][0][0], "LocationAgent")  # First agent in roster
        self.assertIn("domains", call_args[0][1])  # Mission context has domains
    
    def test_l3_orchestrator_exception_handling(self):
        """Test 5: Verify graceful fallback when L3 throws exception."""
        # Mock L3 module that raises exception
        mock_orch_module = MagicMock()
        mock_orch_module.get_consolidated_orchestrator.side_effect = Exception("L3 initialization failed")
        
        # Mock L5 dependencies
        mock_l5 = MagicMock()
        modules = {
            'agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent': mock_orch_module,
            'agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent': mock_l5,
            'agentic_core.L5_safety.validators.LocationAgent': mock_l5,
            'agentic_core.L5_safety.validators.HierarchyAgent': mock_l5,
            'agentic_core.L5_safety.validators.ArchitectureGovernorAgent': mock_l5,
            'agentic_core.L5_safety.validators.SystemArchitectAgent': mock_l5
        }
        
        with patch.dict(sys.modules, modules):
            success, result = try_summon_orchestrator(self.project_root, ["target"], True)
            
        self.assertFalse(success, "Should report failure when L3 throws exception")
        self.assertIsNone(result, "Should return None result when L3 fails")
    
    def test_runtime_state_manager_atomic_save_simulation(self):
        """Test 6: Verify RuntimeStateManager handles save operations correctly."""
        mgr = RuntimeStateManager(self.project_root)
        
        # Start a mission to create state
        mgr.start_mission("Test Mission", ["Agent1", "Agent2"])
        
        # Update some state
        mgr.update_agent("TestAgent", "L5 - Safety")
        mgr.complete_agent("TestAgent", True, "Test completion")
        
        # Save should create the runtime_state.json file
        mgr.save()
        
        # Verify file was created
        state_file = self.project_root / "runtime_state.json"
        self.assertTrue(state_file.exists(), "Runtime state file should be created")
        
        # Verify content is valid JSON and contains expected data
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        self.assertEqual(saved_state["status"], "running")
        self.assertEqual(saved_state["current_agent"], "TestAgent")
        self.assertEqual(saved_state["current_layer"], "L5 - Safety")
        self.assertEqual(len(saved_state["completed_agents"]), 1)
        self.assertEqual(saved_state["completed_agents"][0]["agent"], "TestAgent")
    
    def test_confidence_score_integration(self):
        """Test 7: Verify confidence scoring works correctly for decision making."""
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        # Test high confidence scenario
        confidence = engine.calculate_healing_confidence(
            violations_count=3,
            violation_types=["SHALLOW", "NAMING"],
            territory="prompt_governance",
            historical_success_rate=0.95
        )
        
        self.assertTrue(confidence.is_high_confidence)
        self.assertGreaterEqual(confidence.value, 0.8)
        self.assertIn("Violations: 3", confidence.reasoning)
        
        # Test decision making
        proceed, reason = engine.should_proceed_with_healing(confidence)
        self.assertTrue(proceed)
        self.assertIn("HIGH CONFIDENCE", reason)
        
        # Test low confidence scenario
        low_conf = engine.calculate_healing_confidence(
            violations_count=100,
            violation_types=["UNKNOWN_TYPE", "MYSTERY"],
            territory="L5_safety",
            historical_success_rate=0.3
        )
        
        self.assertTrue(low_conf.is_low_confidence)
        self.assertLess(low_conf.value, 0.5)
        
        # Should not proceed with low confidence when LLM disabled
        proceed, reason = engine.should_proceed_with_healing(low_conf)
        self.assertFalse(proceed)
        self.assertIn("LOW CONFIDENCE", reason)
        self.assertIn("LLM Disabled", reason)
    
    def test_emergency_cleanup_prevents_zombie_states(self):
        """Test 8: Verify emergency cleanup prevents zombie running states."""
        mgr = RuntimeStateManager(self.project_root)
        
        # Start mission but don't finish it
        mgr.start_mission("Test Mission", ["Agent1"])
        self.assertEqual(mgr.state["status"], "running")
        
        # Simulate emergency cleanup (called by atexit)
        mgr._emergency_cleanup()
        
        # Status should be terminated, not still running
        self.assertEqual(mgr.state["status"], "terminated")
        self.assertIsNone(mgr.state["current_agent"])
        self.assertIsNotNone(mgr.state["end_time"])
    
    def test_meta_learning_strategy_weights_persistence(self):
        """Test 9: Verify strategy weights are properly tracked and updated."""
        mgr = RuntimeStateManager(self.project_root)
        mgr.save = MagicMock()
        
        # Initial weights should be default
        initial_weights = mgr.state["meta_learning"]["strategy_weights"]
        self.assertEqual(initial_weights["cot"], 1.0)
        self.assertEqual(initial_weights["tot"], 1.0)
        self.assertEqual(initial_weights["react"], 1.0)
        
        # Update with new weights
        new_weights = {"cot": 2.5, "tot": 0.8, "react": 1.7}
        mgr.update_meta_learning({
            "strategy_weights": new_weights,
            "total_experiences": 10
        })
        
        # Verify weights updated
        updated_weights = mgr.state["meta_learning"]["strategy_weights"]
        self.assertEqual(updated_weights["cot"], 2.5)
        self.assertEqual(updated_weights["tot"], 0.8)
        self.assertEqual(updated_weights["react"], 1.7)
        self.assertEqual(mgr.state["meta_learning"]["total_experiences"], 10)
    
    def test_integration_feature_completeness(self):
        """Test 10: Verify all Phase 4 integration features are present."""
        # Check that RuntimeStateManager has meta_learning capability
        mgr = RuntimeStateManager(self.project_root)
        self.assertIn("meta_learning", mgr.state)
        self.assertIn("strategy_weights", mgr.state["meta_learning"])
        self.assertIn("recent_experiences", mgr.state["meta_learning"])
        
        # Check that try_summon_orchestrator function exists and is importable
        self.assertTrue(callable(try_summon_orchestrator))
        
        # Check function signature
        import inspect
        sig = inspect.signature(try_summon_orchestrator)
        expected_params = ['project_root', 'targets', 'execute']
        actual_params = list(sig.parameters.keys())
        for param in expected_params:
            self.assertIn(param, actual_params)
        
        # Verify confidence scoring is available
        confidence = ConfidenceScore(value=0.8, reasoning="test")
        self.assertTrue(confidence.is_high_confidence)
        self.assertFalse(confidence.is_low_confidence)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
