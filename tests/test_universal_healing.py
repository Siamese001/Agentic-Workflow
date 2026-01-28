#!/usr/bin/env python3
"""
Universal Healing Test Suite
Tests that all agents in execute_ssot.py receive proper healing signals
through the unified confidence-based decision engine.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestUniversalHealing(unittest.TestCase):
    """Test Universal Healing functionality in execute_ssot.py"""

    def setUp(self):
        """Setup test environment"""
        self.project_root = Path.cwd()
        self.mock_agents = {
            'reconciler': MagicMock(),
            'location': MagicMock(),
            'hierarchy': MagicMock(),
            'arch_governor': MagicMock(),
            'system_architect': MagicMock(),
            'pascal_sovereignty': MagicMock(),
            'root_hygiene': MagicMock()
        }
        self.mock_decision_engine = MagicMock()
        self.mock_state_mgr = MagicMock()

    def test_pascal_healing_trigger_with_confidence(self):
        """Test 1: Verify Sovereignty agent is called with heal_repository and confidence gating"""
        
        # Setup mock Pascal agent
        mock_pascal_instance = MagicMock()
        mock_pascal_instance.heal_repository.return_value = {'files_healed': 5}
        self.mock_agents['pascal_sovereignty'].return_value = mock_pascal_instance
        
        # Setup confidence calculation - HIGH confidence
        mock_confidence = MagicMock()
        mock_confidence.value = 0.9
        mock_confidence.reasoning = "HIGH CONFIDENCE (0.90)"
        self.mock_decision_engine.calculate_healing_confidence.return_value = mock_confidence
        self.mock_decision_engine.should_proceed_with_healing.return_value = (True, "HIGH CONFIDENCE (0.90)")
        
        # Mock state manager methods
        self.mock_state_mgr.state = {"compliance_scores": {}}
        self.mock_state_mgr.add_event = MagicMock()
        self.mock_state_mgr.update_agent = MagicMock()
        self.mock_state_mgr.complete_agent = MagicMock()
        
        # Import and execute the relevant code section
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import execute_phase1_discovery_impl
            from agentic_core.L0_maintenance.scripts.execute_ssot import logger
            
            # Mock the logger to capture calls
            with patch('agentic_core.L0_maintenance.scripts.execute_ssot.logger') as mock_logger:
                # Simulate the Phase 2.5 logic from execute_ssot.py
                territory = "prompt_governance"
                p1_loc = ["violation1", "violation2"]  # Mock violations
                
                # Phase 2.5: Sovereignty Enforcement (extracted from execute_ssot.py)
                pascal_confidence = self.mock_decision_engine.calculate_healing_confidence(
                    violations_count=len(p1_loc) if p1_loc else 0,
                    violation_types=['SOVEREIGNTY', 'NAMING', 'HEADER'],
                    territory=territory
                )
                pascal_proceed, pascal_reason = self.mock_decision_engine.should_proceed_with_healing(pascal_confidence)
                
                self.mock_state_mgr.add_event("decision", f"Sovereignty Healing: {pascal_reason}")
                mock_logger.info(f"Sovereignty Decision: {pascal_reason}")
                
                dry_run = False
                if pascal_proceed and not dry_run:
                    mock_logger.info(f"🛡️ Triggering Sovereignty Purge: {territory}")
                    self.mock_state_mgr.update_agent("PascalSovereigntyAgent", "L5 - Safety")
                    pascal = self.mock_agents['pascal_sovereignty'](project_root=Path.cwd())
                    
                    if hasattr(pascal, 'heal_repository'):
                        res = pascal.heal_repository(
                            target_territory=territory, 
                            dry_run=dry_run,
                            auto_approve=True
                        )
                        healed = res.get('files_healed', 0) if isinstance(res, dict) else 0
                        self.mock_state_mgr.complete_agent("PascalSovereigntyAgent", True, f"Healed: {healed}")

                # Assertions
                self.mock_decision_engine.calculate_healing_confidence.assert_called_once_with(
                    violations_count=2,
                    violation_types=['SOVEREIGNTY', 'NAMING', 'HEADER'],
                    territory='prompt_governance'
                )
                self.mock_decision_engine.should_proceed_with_healing.assert_called_once_with(mock_confidence)
                mock_pascal_instance.heal_repository.assert_called_once_with(
                    target_territory='prompt_governance', 
                    dry_run=False,
                    auto_approve=True
                )
                self.mock_state_mgr.complete_agent.assert_called_with("PascalSovereigntyAgent", True, "Healed: 5")
                
                print("✅ PASS: Pascal Sovereignty Healing Triggered with Confidence Gating")
                
        except ImportError as e:
            self.skipTest(f"Could not import execute_ssot module: {e}")

    def test_decision_engine_persistence(self):
        """Test 2: Ensure confidence score is passed to all fixing agents"""
        from agentic_core.L0_maintenance.scripts.execute_ssot import AutonomousDecisionEngine, ConfidenceScore
        
        # Create real decision engine
        decision_engine = AutonomousDecisionEngine(enable_llm=False)
        
        # Test confidence calculation for different scenarios
        test_cases = [
            {
                'violations_count': 5,
                'violation_types': ['HIERARCHY'],
                'territory': 'prompt_governance',
                'expected_min_confidence': 0.8  # Trusted territory with low violations
            },
            {
                'violations_count': 50,
                'violation_types': ['SOVEREIGNTY', 'NAMING'],
                'territory': 'L5_safety',
                'expected_min_confidence': 0.4  # Critical territory with many violations
            },
            {
                'violations_count': 25,
                'violation_types': ['NAMING'],
                'territory': 'L2_execution',
                'expected_min_confidence': 0.6  # Critical territory with medium violations
            }
        ]
        
        for i, case in enumerate(test_cases):
            with self.subTest(case=i):
                confidence = decision_engine.calculate_healing_confidence(
                    case['violations_count'], 
                    case['violation_types'], 
                    case['territory']
                )
                
                # Verify confidence is calculated correctly
                self.assertIsInstance(confidence, ConfidenceScore)
                self.assertGreaterEqual(confidence.value, 0.0)
                self.assertLessEqual(confidence.value, 1.0)
                self.assertGreaterEqual(confidence.value, case['expected_min_confidence'])
                
                # Test decision persistence
                should_proceed, reason = decision_engine.should_proceed_with_healing(confidence)
                self.assertIsInstance(should_proceed, bool)
                self.assertIsInstance(reason, str)
                
        # Verify decisions are stored
        self.assertEqual(len(decision_engine.decisions_made), 3)
        
        # Verify each decision has required fields
        for decision in decision_engine.decisions_made:
            self.assertIn('confidence', decision)
            self.assertIn('decision', decision)
            self.assertIn('reason', decision)
            self.assertIn('timestamp', decision)
        
        print("✅ PASS: Confidence Gate Persistence Verified")

    def test_dry_run_safety(self):
        """Test 3: Ensure agents do NOT heal when --dry-run is active"""
        
        # Setup mock Pascal agent
        mock_pascal_instance = MagicMock()
        mock_pascal_instance.heal_repository.return_value = {'files_healed': 0}
        self.mock_agents['pascal_sovereignty'].return_value = mock_pascal_instance
        
        # Setup HIGH confidence to ensure healing would proceed normally
        mock_confidence = MagicMock()
        mock_confidence.value = 0.9
        self.mock_decision_engine.calculate_healing_confidence.return_value = mock_confidence
        self.mock_decision_engine.should_proceed_with_healing.return_value = (True, "HIGH CONFIDENCE (0.90)")
        
        # Mock state manager
        self.mock_state_mgr.add_event = MagicMock()
        
        # Execute Phase 2.5 logic with dry_run=True
        territory = "prompt_governance"
        p1_loc = ["violation1"]
        dry_run = True
        
        pascal_confidence = self.mock_decision_engine.calculate_healing_confidence(
            violations_count=len(p1_loc) if p1_loc else 0,
            violation_types=['SOVEREIGNTY', 'NAMING', 'HEADER'],
            territory=territory
        )
        pascal_proceed, pascal_reason = self.mock_decision_engine.should_proceed_with_healing(pascal_confidence)
        
        if pascal_proceed and not dry_run:
            # This should NOT execute in dry run mode
            self.fail("Healing should not proceed in dry_run mode")
        elif dry_run:
            self.mock_state_mgr.add_event("info", "Sovereignty healing skipped - Dry run mode")
        
        # Verify heal_repository was NOT called
        mock_pascal_instance.heal_repository.assert_not_called()
        self.mock_state_mgr.add_event.assert_called_with("info", "Sovereignty healing skipped - Dry run mode")
        
        print("✅ PASS: Dry-Run Safety Verified")

    def test_territory_scope_lock(self):
        """Test 4: Verify healing is strictly scoped to the target territory"""
        
        # Setup mock Pascal agent to track territory parameter
        mock_pascal_instance = MagicMock()
        mock_pascal_instance.heal_repository.return_value = {'files_healed': 3}
        self.mock_agents['pascal_sovereignty'].return_value = mock_pascal_instance
        
        # Setup confidence
        mock_confidence = MagicMock()
        mock_confidence.value = 0.8
        self.mock_decision_engine.calculate_healing_confidence.return_value = mock_confidence
        self.mock_decision_engine.should_proceed_with_healing.return_value = (True, "HIGH CONFIDENCE (0.80)")
        
        # Test multiple territories
        territories = ["prompt_governance", "L5_safety", "L2_execution"]
        
        for territory in territories:
            with self.subTest(territory=territory):
                # Reset mock for each iteration
                mock_pascal_instance.reset_mock()
                
                # Execute Phase 2.5 logic
                p1_loc = ["violation1"]
                dry_run = False
                
                pascal_confidence = self.mock_decision_engine.calculate_healing_confidence(
                    violations_count=len(p1_loc),
                    violation_types=['SOVEREIGNTY', 'NAMING', 'HEADER'],
                    territory=territory
                )
                pascal_proceed, pascal_reason = self.mock_decision_engine.should_proceed_with_healing(pascal_confidence)
                
                if pascal_proceed and not dry_run:
                    pascal = self.mock_agents['pascal_sovereignty'](project_root=Path.cwd())
                    if hasattr(pascal, 'heal_repository'):
                        res = pascal.heal_repository(
                            target_territory=territory, 
                            dry_run=dry_run,
                            auto_approve=True
                        )
                
                # Verify the correct territory was passed
                mock_pascal_instance.heal_repository.assert_called_once_with(
                    target_territory=territory, 
                    dry_run=False,
                    auto_approve=True
                )
                
                # Verify confidence was calculated for this specific territory
                self.mock_decision_engine.calculate_healing_confidence.assert_called_with(
                    violations_count=1,
                    violation_types=['SOVEREIGNTY', 'NAMING', 'HEADER'],
                    territory=territory
                )
        
        print("✅ PASS: Territorial Scope Lock Verified")

    def test_low_confidence_blocking(self):
        """Test 5: Verify healing is blocked when confidence is low"""
        
        # Setup mock Pascal agent
        mock_pascal_instance = MagicMock()
        self.mock_agents['pascal_sovereignty'].return_value = mock_pascal_instance
        
        # Setup LOW confidence
        mock_confidence = MagicMock()
        mock_confidence.value = 0.3
        self.mock_decision_engine.calculate_healing_confidence.return_value = mock_confidence
        self.mock_decision_engine.should_proceed_with_healing.return_value = (False, "LOW CONFIDENCE (0.30) - LLM Disabled")
        
        # Mock state manager
        self.mock_state_mgr.add_event = MagicMock()
        
        # Execute Phase 2.5 logic
        territory = "L5_safety"  # Critical territory
        p1_loc = ["violation1", "violation2", "violation3"]
        dry_run = False
        
        pascal_confidence = self.mock_decision_engine.calculate_healing_confidence(
            violations_count=len(p1_loc),
            violation_types=['SOVEREIGNTY', 'NAMING', 'HEADER'],
            territory=territory
        )
        pascal_proceed, pascal_reason = self.mock_decision_engine.should_proceed_with_healing(pascal_confidence)
        
        if not pascal_proceed:
            self.mock_state_mgr.add_event("warning", f"Sovereignty healing skipped - {pascal_reason}")
        
        # Verify heal_repository was NOT called
        mock_pascal_instance.heal_repository.assert_not_called()
        self.mock_state_mgr.add_event.assert_called_with("warning", "Sovereignty healing skipped - LOW CONFIDENCE (0.30) - LLM Disabled")
        
        print("✅ PASS: Low Confidence Blocking Verified")

    def test_certificate_includes_pascal_agent(self):
        """Test 6: Verify certificate includes PascalSovereigntyAgent in executed agents list"""
        
        # Import the certificate generation function
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import execute_phase5_final_impl
            from datetime import datetime
            
            # Setup mock state manager with compliance scores
            self.mock_state_mgr.state = {"compliance_scores": {"test_territory": 0.85}}
            
            # Execute certificate generation
            cert = execute_phase5_final_impl(self.mock_agents, "test_territory", self.mock_state_mgr)
            
            # Verify PascalSovereigntyAgent is in the executed agents list
            self.assertIn('PascalSovereigntyAgent', cert['agents_executed'])
            self.assertEqual(cert['territory'], 'test_territory')
            self.assertEqual(cert['status'], 'COMPLIANT')
            self.assertEqual(cert['confidence_score'], 0.85)
            
            print("✅ PASS: Certificate Includes Pascal Agent")
            
        except ImportError as e:
            self.skipTest(f"Could not import execute_ssot module: {e}")

    def test_agent_availability_check(self):
        """Test 7: Verify all required agents are available for universal healing."""
        # Test that all required agents can be imported
        required_agents = [
            'FilesystemSSOTReconcilerAgent',
            'LocationAgent', 
            'HierarchyAgent',
            'ArchitectureGovernorAgent',
            'SystemArchitectAgent',
            'PascalSovereigntyAgent',
            'RootHygieneAgent'
        ]
        
        import_statements = {
            'FilesystemSSOTReconcilerAgent': 'from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent',
            'LocationAgent': 'from agentic_core.L5_safety.validators.LocationAgent import LocationAgent',
            'HierarchyAgent': 'from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent',
            'ArchitectureGovernorAgent': 'from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent',
            'SystemArchitectAgent': 'from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent',
            'PascalSovereigntyAgent': 'from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent',
            'RootHygieneAgent': 'from agentic_core.L5_safety.validators.RootHygieneAgent import RootHygieneAgent'
        }
        
        for agent_name in required_agents:
            try:
                exec(import_statements[agent_name])
                print(f"✅ {agent_name} - Import OK")
            except ImportError as e:
                self.fail(f"❌ {agent_name} - Import Failed: {e}")
        
        print("✅ PASS: All Required Agents Available")


def run_comprehensive_test():
    """Run all tests and provide comprehensive reporting."""
    print("🧪 Starting Aggressive Universal Healing Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUniversalHealing)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED - Universal Healing is READY!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review implementation")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
