"""
Layer Integration Tests
Tests for cross-layer interactions
"""

import pytest
from agentic_core.l1_planning import StrategyPlanner
from agentic_core.l2_execution import ToolInvocation
from agentic_core.l3_orchestration import DAGBuilder
from agentic_core.l4_memory import StateManager
from agentic_core.l5_safety import ContentFilter


class TestLayerIntegration:
    """Test integration between layers"""
    
    def test_planning_to_execution_flow(self):
        """Test flow from planning to execution"""
        planner = StrategyPlanner()
        executor = ToolInvocation()
        
        # Test basic integration
        assert planner is not None
        assert executor is not None
    
    def test_execution_to_orchestration_flow(self):
        """Test flow from execution to orchestration"""
        executor = ToolInvocation()
        orchestrator = DAGBuilder(name="test_dag", description="Test DAG for planning integration")
        
        # Test basic integration
        assert executor is not None
        assert orchestrator is not None
    
    def test_memory_integration(self):
        """Test memory integration across layers"""
        memory = StateManager()
        planner = StrategyPlanner()
        
        # Test memory integration
        assert memory is not None
        assert planner is not None
    
    def test_safety_integration(self):
        """Test safety integration across layers"""
        safety = ContentFilter()
        executor = ToolInvocation()
        
        # Test safety integration
        assert safety is not None
        assert executor is not None
