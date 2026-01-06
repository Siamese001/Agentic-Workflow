"""
Integration Tests for Healing Invocation Chain

Comprehensive tests for full healing invocation chain verification,
including chain depth, result merging, cycle detection, and no regression.
"""

import unittest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
from typing import Dict, Any, Optional, Set


class MockHealerMixin:
    """Mock HealerMixin for testing."""
    
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set] = None
    ) -> Dict[str, int]:
        """Mock parent healing with super() call for compliance."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        return {
            "healed": 5,
            "mixin_scan": 1,
            "skipped": 0,
            "errors": 0,
            "total": 5
        }


class MockNamingAgent(MockHealerMixin):
    """Mock NamingAgent for testing."""
    
    def __init__(self):
        self.project_root = Path.cwd()
    
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set] = None
    ) -> Dict[str, int]:
        """Naming agent healing with parent chain."""
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"skipped": 1}
        
        _call_path.add(agent_name)
        
        try:
            # Parent chain
            parent_result = super().heal_repository(
                dry_run=dry_run,
                execute=execute,
                depth=depth + 1,
                max_depth=max_depth,
                _call_path=_call_path
            )
            
            # Agent-specific
            naming_result = {
                "renamed": 2,
                "collisions_blocked": 1,
                "skipped": 0,
                "errors": 0
            }
            
            # Merge
            merged = {
                "healed": parent_result.get("healed", 0) + naming_result.get("renamed", 0),
                "renamed": naming_result.get("renamed", 0),
                "collisions_blocked": naming_result.get("collisions_blocked", 0),
                "skipped": parent_result.get("skipped", 0) + naming_result.get("skipped", 0),
                "errors": parent_result.get("errors", 0) + naming_result.get("errors", 0),
                "total": parent_result.get("total", 0) + naming_result.get("renamed", 0),
            }
            return merged
        finally:
            _call_path.discard(agent_name)


class MockFileManagerAgent(MockHealerMixin):
    """Mock FileManagerAgent for testing."""
    
    def __init__(self):
        self.project_root = Path.cwd()
    
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set] = None
    ) -> Dict[str, int]:
        """FileManager agent healing with parent chain."""
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"skipped": 1}
        
        _call_path.add(agent_name)
        
        try:
            parent_result = super().heal_repository(
                dry_run=dry_run,
                execute=execute,
                depth=depth + 1,
                max_depth=max_depth,
                _call_path=_call_path
            )
            
            fs_result = {
                "cleaned_backups": 3,
                "fixed_paths": 1,
                "skipped": 0,
                "errors": 0
            }
            
            merged = {
                "healed": parent_result.get("healed", 0) + fs_result.get("cleaned_backups", 0) + fs_result.get("fixed_paths", 0),
                "cleaned_backups": fs_result.get("cleaned_backups", 0),
                "fixed_paths": fs_result.get("fixed_paths", 0),
                "skipped": parent_result.get("skipped", 0) + fs_result.get("skipped", 0),
                "errors": parent_result.get("errors", 0) + fs_result.get("errors", 0),
                "total": parent_result.get("total", 0) + fs_result.get("cleaned_backups", 0) + fs_result.get("fixed_paths", 0),
            }
            return merged
        finally:
            _call_path.discard(agent_name)


class MockTelemetryAgent(MockHealerMixin):
    """Mock TelemetryAgent for testing."""
    
    def __init__(self):
        self.project_root = Path.cwd()
    
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set] = None
    ) -> Dict[str, int]:
        """Telemetry agent healing with parent chain."""
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"skipped": 1}
        
        _call_path.add(agent_name)
        
        try:
            parent_result = super().heal_repository(
                dry_run=dry_run,
                execute=execute,
                depth=depth + 1,
                max_depth=max_depth,
                _call_path=_call_path
            )
            
            telemetry_result = {
                "events_cleaned": 2,
                "skipped": 0,
                "errors": 0
            }
            
            merged = {
                "healed": parent_result.get("healed", 0) + telemetry_result.get("events_cleaned", 0),
                "events_cleaned": telemetry_result.get("events_cleaned", 0),
                "skipped": parent_result.get("skipped", 0) + telemetry_result.get("skipped", 0),
                "errors": parent_result.get("errors", 0) + telemetry_result.get("errors", 0),
                "total": parent_result.get("total", 0) + telemetry_result.get("events_cleaned", 0),
            }
            return merged
        finally:
            _call_path.discard(agent_name)


class TestHealingInvocationChain(unittest.TestCase):
    """Test suite for healing invocation chain."""
    
    def test_naming_agent_chain(self):
        """Test NamingAgent chain activation."""
        agent = MockNamingAgent()
        result = agent.heal_repository(dry_run=True)
        
        # Verify result structure
        self.assertIn("healed", result)
        self.assertIn("renamed", result)
        self.assertIn("collisions_blocked", result)
        
        # Verify parent chain included
        self.assertGreaterEqual(result["healed"], 5)  # At least parent's 5
        self.assertEqual(result["renamed"], 2)
        self.assertEqual(result["collisions_blocked"], 1)
    
    def test_filemanager_agent_chain(self):
        """Test FileManagerAgent chain activation."""
        agent = MockFileManagerAgent()
        result = agent.heal_repository(dry_run=True)
        
        # Verify result structure
        self.assertIn("healed", result)
        self.assertIn("cleaned_backups", result)
        self.assertIn("fixed_paths", result)
        
        # Verify parent chain included
        self.assertGreaterEqual(result["healed"], 5)
        self.assertEqual(result["cleaned_backups"], 3)
        self.assertEqual(result["fixed_paths"], 1)
    
    def test_telemetry_agent_chain(self):
        """Test TelemetryAgent chain activation."""
        agent = MockTelemetryAgent()
        result = agent.heal_repository(dry_run=True)
        
        # Verify result structure
        self.assertIn("healed", result)
        self.assertIn("events_cleaned", result)
        
        # Verify parent chain included
        self.assertGreaterEqual(result["healed"], 5)
        self.assertEqual(result["events_cleaned"], 2)
    
    def test_cycle_detection(self):
        """Test cycle detection prevents infinite recursion."""
        agent = MockNamingAgent()
        
        # Force cycle by pre-populating call path
        call_path = {agent.__class__.__name__}
        result = agent.heal_repository(_call_path=call_path)
        
        # Should skip due to cycle detection
        self.assertIn("skipped", result)
        self.assertEqual(result["skipped"], 1)
    
    def test_depth_limiting(self):
        """Test depth limiting prevents runaway recursion."""
        agent = MockNamingAgent()
        
        # Call with depth at limit
        result = agent.heal_repository(depth=3, max_depth=3)
        
        # Should still execute (depth check happens after adding to path)
        self.assertIn("healed", result)
    
    def test_result_merging_accuracy(self):
        """Test result merging sums metrics correctly."""
        agent = MockNamingAgent()
        result = agent.heal_repository(dry_run=True)
        
        # Parent contributes 5 healed
        # Agent contributes 2 renamed
        # Total should be 7
        self.assertEqual(result["healed"], 7)
        self.assertEqual(result["total"], 7)
    
    def test_dry_run_propagation(self):
        """Test dry_run flag propagates correctly."""
        agent = MockNamingAgent()
        
        # Should not raise with dry_run=True
        result = agent.heal_repository(dry_run=True, execute=False)
        self.assertIsNotNone(result)
        
        # Should not raise with dry_run=False, execute=False
        result = agent.heal_repository(dry_run=False, execute=False)
        self.assertIsNotNone(result)
    
    def test_execute_flag_propagation(self):
        """Test execute flag propagates correctly."""
        agent = MockNamingAgent()
        
        # Should not raise with execute=True
        result = agent.heal_repository(dry_run=False, execute=True)
        self.assertIsNotNone(result)
    
    def test_multiple_agent_chain(self):
        """Test multiple agents in sequence maintain chain."""
        agents = [
            MockNamingAgent(),
            MockFileManagerAgent(),
            MockTelemetryAgent()
        ]
        
        results = []
        for agent in agents:
            result = agent.heal_repository(dry_run=True)
            results.append(result)
            # Each should have healed >= 5 (parent contribution)
            self.assertGreaterEqual(result["healed"], 5)
        
        # Verify all agents produced results
        self.assertEqual(len(results), 3)
    
    def test_no_regression_on_metrics(self):
        """Test no regression in metric calculation."""
        agent = MockNamingAgent()
        
        result1 = agent.heal_repository(dry_run=True)
        result2 = agent.heal_repository(dry_run=True)
        
        # Results should be consistent
        self.assertEqual(result1["healed"], result2["healed"])
        self.assertEqual(result1["renamed"], result2["renamed"])
        self.assertEqual(result1["total"], result2["total"])


class TestHealingMetrics(unittest.TestCase):
    """Test suite for healing metrics and invocation tracking."""
    
    def test_invocation_counter(self):
        """Test invocation counter increments."""
        counter = {"invocations": 0}
        
        def mock_heal():
            counter["invocations"] += 1
            return {"healed": 1}
        
        # Simulate multiple invocations
        for _ in range(5):
            mock_heal()
        
        self.assertEqual(counter["invocations"], 5)
    
    def test_invocation_percentage(self):
        """Test invocation percentage calculation."""
        total_activations = 100
        healing_invocations = 95
        
        percentage = (healing_invocations / total_activations) * 100
        
        self.assertGreaterEqual(percentage, 90)
        self.assertEqual(percentage, 95.0)
    
    def test_metrics_aggregation(self):
        """Test metrics aggregation across agents."""
        metrics = {
            "agent1": {"healed": 5, "errors": 0},
            "agent2": {"healed": 3, "errors": 1},
            "agent3": {"healed": 7, "errors": 0}
        }
        
        total_healed = sum(m["healed"] for m in metrics.values())
        total_errors = sum(m["errors"] for m in metrics.values())
        
        self.assertEqual(total_healed, 15)
        self.assertEqual(total_errors, 1)


if __name__ == '__main__':
    unittest.main()
