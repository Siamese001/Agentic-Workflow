"""
L3 Orchestration Unit Tests
Tests for individual orchestration components
"""

import pytest
from agentic_core.l3_orchestration import (
    PlanNode, DAGBuilder, ReactEngine, Controller
)


class TestDAGComponents:
    """Test DAG orchestration functionality"""
    
    def test_plan_node_init(self):
        """Test PlanNode initialization"""
        node = PlanNode(node_id="test_node", node_type="test")
        assert node is not None
        assert node.node_id == "test_node"
        assert node.node_type == "test"
    
    def test_dag_builder_init(self):
        """Test DAGBuilder initialization"""
        builder = DAGBuilder(name="test_dag", description="Test DAG")
        assert builder is not None
        assert builder.metadata.name == "test_dag"


class TestReactComponents:
    """Test ReAct orchestration functionality"""
    
    def test_react_engine_init(self):
        """Test ReactEngine initialization"""
        engine = ReactEngine()
        assert engine is not None


class TestControllerComponents:
    """Test controller functionality"""
    
    def test_controller_init(self):
        """Test Controller initialization"""
        controller = Controller(name="test_controller")
        assert controller is not None
        assert controller.name == "test_controller"
