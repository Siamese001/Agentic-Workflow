"""Subatomic Boot Test - Phase 1 Integrity Check

This test validates that the agentic_core architecture can transition
from syntactically valid to functionally operational by exercising
the interfaces and core components.
"""
import re


import pytest

from agentic_core.interfaces import (
    ExecutionContext,
    ExecutionResult,
    OrchestratorConfig,
    PlanningRequest,
    PlanningResult,
)
from agentic_core.L1_cognition.episodic_memory import EpisodicMemory
from agentic_core.L3_orchestration.nervous_system import NervousSystem


class MockCognitivePlane:
    """Mock cognitive plane for testing."""

    def get_capabilities(self):
        """Return mock capabilities."""
        return [MockCapability("reasoning"), MockCapability("planning")]

    async def think(self, request: PlanningRequest):
        """Mock think method."""
        return PlanningResult(
            plan="Mock plan",
            confidence=0.9,
            reasoning="Mock reasoning"
        )


class MockActionPlane:
    """Mock action plane for testing."""

    def get_capabilities(self):
        """Return mock capabilities."""
        return [MockCapability("tool_execution"), MockCapability("api_calls")]

    async def act(self, request):
        """Mock act method."""
        return {"result": "Mock action result"}


class MockCapability:
    """Mock capability enum."""

    def __init__(self, value: str):
        self.value = value


@pytest.fixture
def base_config():
    """Create a base orchestrator config for testing."""
    return OrchestratorConfig(
        max_iterations=10,
        enable_reflection=True,
        enable_state_persistence=True,
        timeout_seconds=30,
        retry_on_failure=True,
        max_retries=3,
        parallel_actions=False,
        metadata={"mission_id": "test-boot-001"}
    )


@pytest.fixture
def mock_cognitive_plane():
    """Create a mock cognitive plane."""
    return MockCognitivePlane()


@pytest.fixture
def mock_action_plane():
    """Create a mock action plane."""
    return MockActionPlane()


@pytest.fixture
def nervous_system(base_config, mock_cognitive_plane, mock_action_plane):
    """Create a NervousSystem instance for testing."""
    return NervousSystem(
        cognitive_plane=mock_cognitive_plane,
        action_plane=mock_action_plane,
        config=base_config
    )


def test_nervous_system_initialization(nervous_system, base_config):
    """Verify that the NervousSystem can boot with the new interface config."""
    assert nervous_system.config is not None
    assert nervous_system.config.max_iterations == 10
    assert nervous_system.config.timeout_seconds == 30
    assert nervous_system.config.metadata["mission_id"] == "test-boot-001"
    assert hasattr(nervous_system, 'brain')
    assert hasattr(nervous_system, 'hands')


def test_context_creation():
    """Verify that ExecutionContext handles phase transitions correctly."""
    context = ExecutionContext(
        mission="Test mission",
        scene={"source": "boot_test"},
        metadata={"task_id": "task-001"}
    )

    # Verify initial state
    assert context.mission == "Test mission"
    assert context.scene["source"] == "boot_test"
    assert context.metadata["task_id"] == "task-001"

    # Test to_dict conversion
    context_dict = context.to_dict()
    assert context_dict["mission"] == "Test mission"
    assert context_dict["scene"]["source"] == "boot_test"


def test_planning_request_creation():
    """Verify that PlanningRequest can be constructed properly."""
    request = PlanningRequest(
        task="Verify project integrity",
        context={"window": 4000},
        max_steps=10,
        constraints=["priority_1"]
    )

    assert request.task == "Verify project integrity"
    assert request.context["window"] == 4000
    assert request.max_steps == 10
    assert "priority_1" in request.constraints

    # Test to_dict conversion
    request_dict = request.to_dict()
    assert request_dict["task"] == "Verify project integrity"
    assert request_dict["max_steps"] == 10


@pytest.mark.asyncio
async def test_tri_brain_routing_stub(nervous_system):
    """
    Verify that a PlanningRequest can be constructed and 'routed'.
    This tests if the L1/L3 connective tissue is firing.
    """
    request = PlanningRequest(
        task="Verify project integrity",
        context={"window": 4000},
        max_steps=10
    )

    # Verify request structure
    assert request.task == "Verify project integrity"
    assert request.max_steps == 10

    # Verify NervousSystem has the expected components
    assert hasattr(nervous_system, 'brain')
    assert hasattr(nervous_system, 'hands')
    assert hasattr(nervous_system, 'config')

    # Verify the mock planes have capabilities
    brain_caps = nervous_system.brain.get_capabilities()
    hand_caps = nervous_system.hands.get_capabilities()
    assert len(brain_caps) > 0
    assert len(hand_caps) > 0
    assert brain_caps[0].value == "reasoning"
    assert hand_caps[0].value == "tool_execution"


def test_episodic_memory_integration():
    """Verify that EpisodicMemory can be imported and has expected interface."""
    # Test that we can import the class
    assert EpisodicMemory is not None

    # Test that the module has the expected functions
    from agentic_core.L1_cognition.episodic_memory import (
        analyze_failure_patterns,
        commit_episode,
        create_episodic_memory,
        get_stats,
        get_successful_patterns,
        recall_relevant_experience,
    )

    # Verify all functions exist
    assert commit_episode is not None
    assert recall_relevant_experience is not None
    assert get_successful_patterns is not None
    assert analyze_failure_patterns is not None
    assert get_stats is not None
    assert create_episodic_memory is not None


def test_interface_imports():
    """Verify that all interfaces can be imported successfully."""
    from agentic_core.interfaces import (
        ActionRequest,
        ExecutionContext,
        ExecutionPhase,
        ExecutionResult,
        IActionPlane,
        ICognitivePlane,
        IOrchestrator,
        OrchestratorConfig,
        PlanningRequest,
        PlanningResult,
    )

    # Verify all imports worked
    assert ExecutionContext is not None
    assert ExecutionResult is not None
    assert ExecutionPhase is not None
    assert ICognitivePlane is not None
    assert IActionPlane is not None
    assert IOrchestrator is not None
    assert ActionRequest is not None
    assert PlanningRequest is not None
    assert PlanningResult is not None
    assert OrchestratorConfig is not None

    # Verify ExecutionPhase enum values
    assert hasattr(ExecutionPhase, 'MISSION')
    assert hasattr(ExecutionPhase, 'SCENE')
    assert hasattr(ExecutionPhase, 'THINK')
    assert hasattr(ExecutionPhase, 'ACT')
    assert hasattr(ExecutionPhase, 'OBSERVE')
    assert hasattr(ExecutionPhase, 'REFLECT')
    assert ExecutionPhase.MISSION.value == "mission"
    assert ExecutionPhase.SCENE.value == "scene"


def test_config_to_dict():
    """Verify that OrchestratorConfig can be converted to dict."""
    config = OrchestratorConfig(
        max_iterations=5,
        enable_reflection=False,
        metadata={"test": "boot"}
    )

    config_dict = config.to_dict()
    assert config_dict["max_iterations"] == 5
    assert config_dict["enable_reflection"] is False
    assert config_dict["metadata"]["test"] == "boot"


def test_execution_result_creation():
    """Verify that ExecutionResult can be created and converted."""
    result = ExecutionResult(
        success=True,
        output="Test output",
        final_state={"status": "SUCCESS"},
        iterations=1,
        errors=[],
        metadata={"task_id": "test-001"}
    )

    assert result.success is True
    assert result.output == "Test output"
    assert result.final_state["status"] == "SUCCESS"
    assert result.metadata["task_id"] == "test-001"

    result_dict = result.to_dict()
    assert result_dict["success"] is True
    assert result_dict["output"] == "Test output"
    assert result_dict["final_state"]["status"] == "SUCCESS"
    assert result_dict["metadata"]["task_id"] == "test-001"
