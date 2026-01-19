#!/usr/bin/env python3
"""
Comprehensive test suite for StrategicRecommendationAgent.

Tests:
1. Basic functionality - agent initialization and run
2. Plan generation - correct prompt structure
3. Act execution - fallback recommendations
4. Edge cases - empty data, missing fields, extreme values
5. Integration - works with real dashboard data
"""
import json
import sys
import unittest
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L3_orchestration.strategic_recommendation.StrategicRecommendationAgent import StrategicRecommendationAgent
from agentic_core.utils.file_utils import safe_read_file, safe_write_file


class TestStrategicRecommendationAgentBasic(unittest.TestCase):
    """Basic functionality tests."""
    
    def setUp(self):
        """Initialize agent for each test."""
        self.agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.project_root, PROJECT_ROOT)
        self.assertIsNone(self.agent.llm_client)
    
    def test_agent_has_required_methods(self):
        """Test agent has all required methods."""
        self.assertTrue(hasattr(self.agent, 'plan'))
        self.assertTrue(hasattr(self.agent, 'act'))
        self.assertTrue(hasattr(self.agent, 'run'))
        self.assertTrue(hasattr(self.agent, 'heal_repository'))
    
    def test_agent_with_llm_client(self):
        """Test agent accepts LLM client."""
        mock_client = object()
        agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT, llm_client=mock_client)
        self.assertEqual(agent.llm_client, mock_client)


class TestStrategicRecommendationAgentPlan(unittest.TestCase):
    """Plan generation tests."""
    
    def setUp(self):
        self.agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
        self.sample_data = [
            {"Territory": "TOTAL", "Total": 100, "Health": 75.0, "Invocation %": 80.0, 
             "Hardened %": 60.0, "Test %": 70.0, "Heal Cap %": 90.0, "Avg CC": 12.0},
            {"Territory": "L5 Safety/Validators", "Total": 20, "Health": 65.0, 
             "Invocation %": 40.0, "Hardened %": 30.0, "Test %": 50.0, "Avg CC": 18.0},
        ]
    
    def test_plan_returns_string(self):
        """Test plan returns a string prompt."""
        result = self.agent.plan(self.sample_data)
        self.assertIsInstance(result, str)
    
    def test_plan_contains_key_signals(self):
        """Test plan contains key metric signals."""
        result = self.agent.plan(self.sample_data)
        self.assertIn("Overall Health:", result)
        self.assertIn("Total Agents:", result)
        self.assertIn("Healing Capability:", result)
    
    def test_plan_identifies_low_invocation(self):
        """Test plan identifies territories with low invocation."""
        result = self.agent.plan(self.sample_data)
        self.assertIn("L5 Safety/Validators", result)
    
    def test_plan_with_empty_data(self):
        """Test plan handles empty data gracefully."""
        result = self.agent.plan([])
        self.assertIsInstance(result, str)
        self.assertIn("Total Agents: 0", result)


class TestStrategicRecommendationAgentAct(unittest.TestCase):
    """Act execution tests."""
    
    def setUp(self):
        self.agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
    
    def test_act_returns_dict(self):
        """Test act returns a dictionary."""
        data = [{"Territory": "TOTAL", "Total": 100, "Health": 50.0, "Invocation %": 30.0,
                 "Hardened %": 40.0, "Test %": 60.0, "Heal Cap %": 80.0, "Avg CC": 20.0,
                 "Observable %": 50.0, "Documented %": 70.0}]
        plan = self.agent.plan(data)
        result = self.agent.act(plan, data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('review', result)
        self.assertIn('recommendations', result)
    
    def test_act_generates_recommendations(self):
        """Test act generates at least one recommendation."""
        data = [{"Territory": "TOTAL", "Total": 100, "Health": 50.0, "Invocation %": 30.0,
                 "Hardened %": 40.0, "Test %": 60.0, "Heal Cap %": 80.0, "Avg CC": 20.0}]
        plan = self.agent.plan(data)
        result = self.agent.act(plan, data)
        
        self.assertGreater(len(result['recommendations']), 0)
    
    def test_act_review_not_empty(self):
        """Test act generates a non-empty review."""
        data = [{"Territory": "TOTAL", "Total": 100, "Health": 50.0, "Invocation %": 30.0,
                 "Hardened %": 40.0, "Test %": 60.0, "Heal Cap %": 80.0}]
        plan = self.agent.plan(data)
        result = self.agent.act(plan, data)
        
        self.assertIsInstance(result['review'], str)
        self.assertGreater(len(result['review']), 0)


class TestStrategicRecommendationAgentRun(unittest.TestCase):
    """Full run execution tests."""
    
    def setUp(self):
        self.agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
    
    def test_run_returns_complete_result(self):
        """Test run returns complete result structure."""
        data = [{"Territory": "TOTAL", "Total": 100, "Health": 50.0, "Invocation %": 30.0,
                 "Hardened %": 40.0, "Test %": 60.0, "Heal Cap %": 80.0, "Avg CC": 20.0}]
        result = self.agent.run(data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('review', result)
        self.assertIn('recommendations', result)
        self.assertIsInstance(result['recommendations'], list)
    
    def test_run_with_real_discovery_data(self):
        """Test run with actual discovery data."""
        discovery_path = PROJECT_ROOT / 'agent_discovery_full.json'
        if discovery_path.exists():
            with open(discovery_path, 'r', encoding='utf-8') as f:
                agents = json.load(f)
            
            # Build minimal dashboard data
            total_agents = len(agents)
            dashboard_data = [{
                "Territory": "TOTAL",
                "Total": total_agents,
                "Health": 75.0,
                "Invocation %": 80.0,
                "Hardened %": 100.0,
                "Test %": 68.0,
                "Heal Cap %": 100.0,
                "Avg CC": 10.0,
                "Observable %": 50.0,
                "Documented %": 91.0
            }]
            
            result = self.agent.run(dashboard_data)
            self.assertIn('review', result)
            self.assertIn('recommendations', result)


class TestStrategicRecommendationAgentEdgeCases(unittest.TestCase):
    """Edge case tests."""
    
    def setUp(self):
        self.agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
    
    def test_empty_dashboard_data(self):
        """Test with empty dashboard data."""
        result = self.agent.run([])
        self.assertIsInstance(result, dict)
        self.assertIn('review', result)
        self.assertIn('recommendations', result)
    
    def test_missing_total_row(self):
        """Test with no TOTAL row."""
        data = [{"Territory": "L5 Safety", "Total": 10, "Health": 50.0}]
        result = self.agent.run(data)
        self.assertIsInstance(result, dict)
    
    def test_missing_fields(self):
        """Test with missing metric fields."""
        data = [{"Territory": "TOTAL", "Total": 100}]  # Missing all metrics
        result = self.agent.run(data)
        self.assertIsInstance(result, dict)
        self.assertIn('review', result)
    
    def test_extreme_low_values(self):
        """Test with all metrics at 0%."""
        data = [{
            "Territory": "TOTAL", "Total": 100, "Health": 0.0,
            "Invocation %": 0.0, "Hardened %": 0.0, "Test %": 0.0,
            "Heal Cap %": 0.0, "Avg CC": 100.0, "Observable %": 0.0, "Documented %": 0.0
        }]
        result = self.agent.run(data)
        
        # Should generate many recommendations for poor metrics
        self.assertGreater(len(result['recommendations']), 3)
    
    def test_extreme_high_values(self):
        """Test with all metrics at 100%."""
        data = [{
            "Territory": "TOTAL", "Total": 100, "Health": 100.0,
            "Invocation %": 100.0, "Hardened %": 100.0, "Test %": 100.0,
            "Heal Cap %": 100.0, "Avg CC": 5.0, "Observable %": 100.0, "Documented %": 100.0
        }]
        result = self.agent.run(data)
        
        # Should generate fewer recommendations for excellent metrics
        self.assertIsInstance(result['recommendations'], list)
    
    def test_negative_values(self):
        """Test with negative metric values (invalid but shouldn't crash)."""
        data = [{
            "Territory": "TOTAL", "Total": 100, "Health": -10.0,
            "Invocation %": -5.0, "Hardened %": -20.0
        }]
        result = self.agent.run(data)
        self.assertIsInstance(result, dict)
    
    def test_none_values(self):
        """Test with None values in metrics."""
        data = [{
            "Territory": "TOTAL", "Total": 100, "Health": None,
            "Invocation %": None, "Hardened %": None
        }]
        result = self.agent.run(data)
        self.assertIsInstance(result, dict)
    
    def test_large_dataset(self):
        """Test with large number of territories."""
        data = [{"Territory": "TOTAL", "Total": 1000, "Health": 75.0, 
                 "Invocation %": 80.0, "Hardened %": 90.0, "Test %": 70.0,
                 "Heal Cap %": 100.0, "Avg CC": 15.0}]
        
        # Add 50 territory rows
        for i in range(50):
            data.append({
                "Territory": f"L{i % 6} Territory/{i}",
                "Total": 20,
                "Health": 50.0 + (i % 50),
                "Invocation %": 30.0 + (i % 70),
                "Hardened %": 40.0 + (i % 60),
                "Test %": 20.0 + (i % 80),
                "Avg CC": 10 + (i % 20)
            })
        
        result = self.agent.run(data)
        self.assertIsInstance(result, dict)
        self.assertIn('recommendations', result)


class TestStrategicRecommendationAgentFallback(unittest.TestCase):
    """Fallback recommendation tests."""
    
    def setUp(self):
        self.agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
    
    def test_fallback_low_invocation(self):
        """Test fallback generates invocation recommendation for low invocation."""
        data = [{"Territory": "TOTAL", "Total": 100, "Health": 50.0, 
                 "Invocation %": 30.0, "Hardened %": 90.0, "Test %": 90.0, "Heal Cap %": 90.0}]
        result = self.agent._generate_fallback_recommendations(data)
        
        # Should mention invocation
        recs_text = ' '.join(result['recommendations'])
        self.assertIn('Invocation', recs_text)
    
    def test_fallback_low_mcp(self):
        """Test fallback generates MCP recommendation for low hardening."""
        data = [{"Territory": "TOTAL", "Total": 100, "Health": 50.0,
                 "Invocation %": 90.0, "Hardened %": 30.0, "Test %": 90.0, "Heal Cap %": 90.0}]
        result = self.agent._generate_fallback_recommendations(data)
        
        recs_text = ' '.join(result['recommendations'])
        self.assertIn('Harden', recs_text)
    
    def test_fallback_low_tests(self):
        """Test fallback generates test recommendation for low coverage."""
        data = [{"Territory": "TOTAL", "Total": 100, "Health": 50.0,
                 "Invocation %": 90.0, "Hardened %": 90.0, "Test %": 30.0, "Heal Cap %": 90.0}]
        result = self.agent._generate_fallback_recommendations(data)
        
        recs_text = ' '.join(result['recommendations'])
        self.assertIn('Test', recs_text)
    
    def test_fallback_high_complexity(self):
        """Test fallback generates complexity recommendation for high CC."""
        data = [
            {"Territory": "TOTAL", "Total": 100, "Health": 50.0, "Avg CC": 25.0,
             "Invocation %": 90.0, "Hardened %": 90.0, "Test %": 90.0, "Heal Cap %": 90.0},
            {"Territory": "L5 Safety/Validators", "Total": 20, "Avg CC": 25.0}
        ]
        result = self.agent._generate_fallback_recommendations(data)
        
        recs_text = ' '.join(result['recommendations'])
        self.assertIn('Complexity', recs_text)


class TestStrategicRecommendationAgentHealing(unittest.TestCase):
    """Healing capability tests."""
    
    def setUp(self):
        self.agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
    
    def test_heal_repository_exists(self):
        """Test heal_repository method exists and is callable."""
        self.assertTrue(callable(self.agent.heal_repository))
    
    def test_heal_repository_dry_run(self):
        """Test heal_repository in dry run mode."""
        result = self.agent.heal_repository(dry_run=True)
        self.assertIsInstance(result, dict)


def run_tests():
    """Run all tests and return results."""
    print("=" * 70)
    print("StrategicRecommendationAgent Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicRecommendationAgentBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicRecommendationAgentPlan))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicRecommendationAgentAct))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicRecommendationAgentRun))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicRecommendationAgentEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicRecommendationAgentFallback))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicRecommendationAgentHealing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"✅ ALL {result.testsRun} TESTS PASSED")
    else:
        print(f"❌ {len(result.failures) + len(result.errors)} TESTS FAILED")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
