"""
Tests for Unified Workflow Engine and Coordinators

Tests the orchestration consolidation implementation:
- ExecutionStrategy implementations
- Base coordinator functionality
- UnifiedWorkflowEngine
- All 10 specialized coordinators
"""

import pytest
import asyncio
from typing import Dict, Any

# Import from unified engine
import sys
sys.path.insert(0, 'c:/Git/Agentic-Workflow')

from agentic_core.L3_orchestration.unified_engine import (
    # Execution Strategies
    ExecutionStrategy,
    ExecutionStatus,
    WorkflowContext,
    WorkflowResult,
    WorkflowStep,
    DAGStrategy,
    StateMachineStrategy,
    EventDrivenStrategy,
    ReactiveStrategy,
    get_strategy,
    # Coordinator Base
    WorkflowCoordinator,
    CoordinatorCapability,
    CoordinatorRegistry,
    # Unified Engine
    UnifiedWorkflowEngine,
    # Coordinators
    RLCoordinator,
    TerritoryCoordinator,
    MCPCoordinator,
    MissionCoordinator,
    ModelCoordinator,
    HealthCoordinator,
    GovernanceCoordinator,
    UtilityCoordinator,
    CachingCoordinator,
    SecurityCoordinator,
    register_all_coordinators,
)


# ============== Test Fixtures ==============

@pytest.fixture
def workflow_context():
    """Create test workflow context."""
    return WorkflowContext(
        workflow_id="test-workflow-001",
        workflow_type="dag",
        input_data={"test": "data"},
        metadata={"source": "test"}
    )


@pytest.fixture
def simple_steps():
    """Create simple workflow steps."""
    def step1(ctx, results):
        return {"step": 1, "done": True}
    
    def step2(ctx, results):
        return {"step": 2, "done": True}
    
    def step3(ctx, results):
        return {"step": 3, "done": True}
    
    return [
        WorkflowStep(step_id="step1", name="Step 1", handler=step1),
        WorkflowStep(step_id="step2", name="Step 2", handler=step2, dependencies=["step1"]),
        WorkflowStep(step_id="step3", name="Step 3", handler=step3, dependencies=["step2"]),
    ]


@pytest.fixture
def unified_engine():
    """Create unified workflow engine with all coordinators."""
    engine = UnifiedWorkflowEngine()
    register_all_coordinators()
    return engine


# ============== Execution Strategy Tests ==============

class TestDAGStrategy:
    """Tests for DAG execution strategy."""
    
    @pytest.mark.asyncio
    async def test_dag_strategy_executes_steps(self, workflow_context, simple_steps):
        """Test DAG strategy executes steps in order."""
        strategy = DAGStrategy()
        result = await strategy.execute(workflow_context, simple_steps)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.steps_executed == 3
        assert "step1" in result.output
        assert "step2" in result.output
        assert "step3" in result.output
    
    @pytest.mark.asyncio
    async def test_dag_strategy_handles_parallel_steps(self, workflow_context):
        """Test DAG strategy handles parallel steps."""
        def step_a(ctx, results):
            return {"step": "a"}
        
        def step_b(ctx, results):
            return {"step": "b"}
        
        def step_c(ctx, results):
            return {"step": "c", "deps": list(results.keys())}
        
        steps = [
            WorkflowStep(step_id="a", name="Step A", handler=step_a),
            WorkflowStep(step_id="b", name="Step B", handler=step_b),
            WorkflowStep(step_id="c", name="Step C", handler=step_c, dependencies=["a", "b"]),
        ]
        
        strategy = DAGStrategy()
        result = await strategy.execute(workflow_context, steps)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.steps_executed == 3
    
    def test_dag_strategy_can_handle(self):
        """Test DAG strategy workflow type handling."""
        strategy = DAGStrategy()
        assert strategy.can_handle("dag")
        assert strategy.can_handle("pipeline")
        assert strategy.can_handle("sequential")
        assert not strategy.can_handle("unknown")
    
    def test_dag_strategy_name(self):
        """Test DAG strategy name."""
        strategy = DAGStrategy()
        assert strategy.get_name() == "dag"


class TestStateMachineStrategy:
    """Tests for state machine execution strategy."""
    
    @pytest.mark.asyncio
    async def test_state_machine_executes_steps(self, workflow_context, simple_steps):
        """Test state machine executes steps."""
        strategy = StateMachineStrategy()
        result = await strategy.execute(workflow_context, simple_steps)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.steps_executed >= 1
    
    def test_state_machine_can_handle(self):
        """Test state machine workflow type handling."""
        strategy = StateMachineStrategy()
        assert strategy.can_handle("state_machine")
        assert strategy.can_handle("fsm")
        assert strategy.can_handle("workflow")


class TestEventDrivenStrategy:
    """Tests for event-driven execution strategy."""
    
    @pytest.mark.asyncio
    async def test_event_driven_executes_steps(self, workflow_context, simple_steps):
        """Test event-driven executes steps."""
        strategy = EventDrivenStrategy()
        result = await strategy.execute(workflow_context, simple_steps)
        
        assert result.status == ExecutionStatus.COMPLETED
    
    def test_event_driven_can_handle(self):
        """Test event-driven workflow type handling."""
        strategy = EventDrivenStrategy()
        assert strategy.can_handle("event")
        assert strategy.can_handle("event_driven")
        assert strategy.can_handle("async")


class TestReactiveStrategy:
    """Tests for reactive execution strategy."""
    
    @pytest.mark.asyncio
    async def test_reactive_executes_steps(self, workflow_context, simple_steps):
        """Test reactive executes steps."""
        strategy = ReactiveStrategy()
        result = await strategy.execute(workflow_context, simple_steps)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.steps_executed == 3
    
    def test_reactive_can_handle(self):
        """Test reactive workflow type handling."""
        strategy = ReactiveStrategy()
        assert strategy.can_handle("reactive")
        assert strategy.can_handle("stream")
        assert strategy.can_handle("observable")


class TestGetStrategy:
    """Tests for strategy selection."""
    
    def test_get_dag_strategy(self):
        """Test getting DAG strategy."""
        strategy = get_strategy("dag")
        assert isinstance(strategy, DAGStrategy)
    
    def test_get_state_machine_strategy(self):
        """Test getting state machine strategy."""
        strategy = get_strategy("state_machine")
        assert isinstance(strategy, StateMachineStrategy)
    
    def test_get_default_strategy(self):
        """Test getting default strategy for unknown type."""
        strategy = get_strategy("unknown")
        assert isinstance(strategy, DAGStrategy)  # Default


# ============== Coordinator Tests ==============

class TestCoordinatorRegistry:
    """Tests for coordinator registry."""
    
    def test_register_coordinator(self):
        """Test coordinator registration."""
        registry = CoordinatorRegistry()
        coordinator = RLCoordinator()
        
        registry.register(coordinator)
        
        assert registry.get("rl_coordinator") is coordinator
    
    def test_get_for_workflow(self):
        """Test getting coordinator for workflow type."""
        registry = CoordinatorRegistry()
        coordinator = RLCoordinator()
        registry.register(coordinator)
        
        found = registry.get_for_workflow("rl")
        
        assert found is coordinator
    
    def test_get_statistics(self):
        """Test getting registry statistics."""
        registry = CoordinatorRegistry()
        coordinator = RLCoordinator()
        registry.register(coordinator)
        
        stats = registry.get_statistics()
        
        assert stats["total_coordinators"] == 1
        assert "rl_coordinator" in stats["coordinators"]


class TestRLCoordinator:
    """Tests for RL coordinator."""
    
    @pytest.mark.asyncio
    async def test_rl_coordination(self):
        """Test RL coordination."""
        coordinator = RLCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="rl",
            input_data={
                "rl_strategy": "ppo",
                "action_space": ["action1", "action2"],
                "state": {"value": 1},
                "reward": 1.0
            }
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["strategy"] == "ppo"
        assert result.output["reward"] == 1.0
    
    def test_rl_can_handle(self):
        """Test RL workflow type handling."""
        coordinator = RLCoordinator()
        assert coordinator.can_handle("rl")
        assert coordinator.can_handle("ppo")
        assert coordinator.can_handle("q_learning")


class TestTerritoryCoordinator:
    """Tests for Territory coordinator."""
    
    @pytest.mark.asyncio
    async def test_territory_map(self):
        """Test territory mapping."""
        coordinator = TerritoryCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="territory",
            input_data={"operation": "map", "territory": "L1_cognition"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["status"] == "mapped"
    
    @pytest.mark.asyncio
    async def test_territory_heal(self):
        """Test territory healing."""
        coordinator = TerritoryCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="territory",
            input_data={"operation": "heal", "territory": "L1_cognition"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["status"] == "healed"


class TestMCPCoordinator:
    """Tests for MCP coordinator."""
    
    @pytest.mark.asyncio
    async def test_mcp_route(self):
        """Test MCP routing."""
        coordinator = MCPCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="mcp",
            input_data={"operation": "route", "tool": "test_tool"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["routed"] == True
    
    @pytest.mark.asyncio
    async def test_mcp_verify(self):
        """Test MCP tool verification."""
        coordinator = MCPCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="mcp",
            input_data={"operation": "verify", "tool": "test_tool"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["verified"] == True


class TestMissionCoordinator:
    """Tests for Mission coordinator."""
    
    @pytest.mark.asyncio
    async def test_mission_run(self):
        """Test mission run."""
        coordinator = MissionCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="mission",
            input_data={"operation": "run", "mission_id": "mission-001"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_mission_test(self):
        """Test mission testing."""
        coordinator = MissionCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="mission",
            input_data={"operation": "test", "mission_id": "mission-001"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["passed"] == True


class TestModelCoordinator:
    """Tests for Model coordinator."""
    
    @pytest.mark.asyncio
    async def test_model_route(self):
        """Test model routing."""
        coordinator = ModelCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="model",
            input_data={"operation": "route", "model": "gpt-4"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["routed"] == True
    
    @pytest.mark.asyncio
    async def test_model_rag(self):
        """Test RAG query."""
        coordinator = ModelCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="model",
            input_data={"operation": "rag", "query": "test query"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["source"] == "rag"


class TestHealthCoordinator:
    """Tests for Health coordinator."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        coordinator = HealthCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="health",
            input_data={"operation": "check"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_deadlock_detection(self):
        """Test deadlock detection."""
        coordinator = HealthCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="health",
            input_data={"operation": "deadlock"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["deadlocks"] == 0


class TestGovernanceCoordinator:
    """Tests for Governance coordinator."""
    
    @pytest.mark.asyncio
    async def test_governance_validate(self):
        """Test governance validation."""
        coordinator = GovernanceCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="governance",
            input_data={"operation": "validate"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["registry"] == "valid"
    
    @pytest.mark.asyncio
    async def test_permission_check(self):
        """Test permission check."""
        coordinator = GovernanceCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="governance",
            input_data={"operation": "permission", "agent": "TestAgent", "action": "read"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["allowed"] == True


class TestUtilityCoordinator:
    """Tests for Utility coordinator."""
    
    @pytest.mark.asyncio
    async def test_handshake(self):
        """Test handshake."""
        coordinator = UtilityCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="utility",
            input_data={"operation": "handshake"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["handshake"] == "complete"
    
    @pytest.mark.asyncio
    async def test_tao_loop(self):
        """Test TAO loop."""
        coordinator = UtilityCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="utility",
            input_data={"operation": "tao"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert "thought" in result.output
        assert "action" in result.output
        assert "observation" in result.output


class TestCachingCoordinator:
    """Tests for Caching coordinator."""
    
    @pytest.mark.asyncio
    async def test_cache_set_get(self):
        """Test cache set and get."""
        coordinator = CachingCoordinator()
        
        # Set
        set_context = WorkflowContext(
            workflow_id="test1",
            workflow_type="cache",
            input_data={"operation": "set", "key": "test_key", "value": "test_value"}
        )
        set_result = await coordinator.coordinate(set_context)
        assert set_result.output["stored"] == True
        
        # Get
        get_context = WorkflowContext(
            workflow_id="test2",
            workflow_type="cache",
            input_data={"operation": "get", "key": "test_key"}
        )
        get_result = await coordinator.coordinate(get_context)
        assert get_result.output["hit"] == True
        assert get_result.output["value"] == "test_value"


class TestSecurityCoordinator:
    """Tests for Security coordinator."""
    
    @pytest.mark.asyncio
    async def test_security_validate(self):
        """Test security validation."""
        coordinator = SecurityCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="security",
            input_data={"operation": "validate"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["valid"] == True
    
    @pytest.mark.asyncio
    async def test_security_audit(self):
        """Test security audit."""
        coordinator = SecurityCoordinator()
        context = WorkflowContext(
            workflow_id="test",
            workflow_type="security",
            input_data={"operation": "audit"}
        )
        
        result = await coordinator.coordinate(context)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output["vulnerabilities"] == 0


# ============== Unified Engine Tests ==============

class TestUnifiedWorkflowEngine:
    """Tests for unified workflow engine."""
    
    @pytest.mark.asyncio
    async def test_execute_with_steps(self, simple_steps):
        """Test execute with steps."""
        engine = UnifiedWorkflowEngine()
        
        result = await engine.execute(
            workflow_type="dag",
            input_data={"test": "data"},
            steps=simple_steps
        )
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.steps_executed == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_coordinator(self):
        """Test execute with coordinator."""
        engine = UnifiedWorkflowEngine()
        engine.register_coordinator(HealthCoordinator())
        
        result = await engine.execute(
            workflow_type="health",
            input_data={"operation": "check"}
        )
        
        assert result.status == ExecutionStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_with_coordinator_by_name(self):
        """Test execute with coordinator by name."""
        engine = UnifiedWorkflowEngine()
        engine.register_coordinator(MissionCoordinator())
        
        result = await engine.execute_with_coordinator(
            coordinator_name="mission_coordinator",
            input_data={"operation": "run", "mission_id": "test"}
        )
        
        assert result.status == ExecutionStatus.COMPLETED
    
    def test_get_statistics(self):
        """Test get statistics."""
        engine = UnifiedWorkflowEngine()
        stats = engine.get_statistics()
        
        assert "metrics" in stats
        assert "strategies" in stats
        assert "coordinators" in stats
    
    def test_register_all_coordinators(self):
        """Test registering all coordinators."""
        engine = UnifiedWorkflowEngine()
        coordinators = register_all_coordinators()
        
        assert len(coordinators) == 10
        
        # Verify all coordinators registered
        stats = engine.coordinator_registry.get_statistics()
        assert stats["total_coordinators"] == 10


class TestIntegration:
    """Integration tests for complete orchestration flow."""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_all_coordinators(self):
        """Test full workflow with all coordinators."""
        engine = UnifiedWorkflowEngine()
        register_all_coordinators()
        
        # Test each coordinator type
        workflow_types = [
            ("rl", {"rl_strategy": "ppo", "action_space": ["a"], "state": {}, "reward": 1.0}),
            ("territory", {"operation": "map", "territory": "L1"}),
            ("mcp", {"operation": "route", "tool": "test"}),
            ("mission", {"operation": "run", "mission_id": "m1"}),
            ("model", {"operation": "route", "model": "gpt"}),
            ("health", {"operation": "check"}),
            ("governance", {"operation": "validate"}),
            ("utility", {"operation": "handshake"}),
            ("cache", {"operation": "get", "key": "test"}),
            ("security", {"operation": "validate"}),
        ]
        
        for wf_type, input_data in workflow_types:
            result = await engine.execute(
                workflow_type=wf_type,
                input_data=input_data
            )
            assert result.status == ExecutionStatus.COMPLETED, f"Failed for {wf_type}"
    
    @pytest.mark.asyncio
    async def test_engine_statistics_after_workflows(self):
        """Test engine statistics after running workflows."""
        engine = UnifiedWorkflowEngine()
        register_all_coordinators()
        
        # Run some workflows
        for i in range(5):
            await engine.execute(
                workflow_type="health",
                input_data={"operation": "check"}
            )
        
        stats = engine.get_statistics()
        
        assert stats["metrics"]["total_workflows"] == 5
        assert stats["metrics"]["completed_workflows"] == 5
        assert stats["metrics"]["success_rate"] == 100.0


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
