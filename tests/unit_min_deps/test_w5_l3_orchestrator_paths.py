"""
W5 L3 Orchestrator Path Tests

Tests for deterministic L3 orchestration kernel path behaviors.
Validates Path B, C, and D orchestration with proper state transitions.
"""

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler
from agentic_core.L3_orchestration.engines.deterministic_orchestrator import (
    DeterministicOrchestrator,
)
from agentic_core.L3_orchestration.engines.handshake_state_machine import HandshakeState
from agentic_core.L3_orchestration.types.human_decision_artifact_types import HumanAction

pytestmark = pytest.mark.unit_min_deps


class TestW5L3OrchestratorPaths:
    """Test suite for W5 L3 orchestrator path behaviors."""

    @pytest.fixture
    def orchestrator(self):
        """Create deterministic orchestrator instance."""
        return DeterministicOrchestrator()

    @pytest.fixture
    def sample_payload(self):
        """Create sample governed payload for testing."""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt="Single task prompt",
        )

    @pytest.fixture
    def multi_task_payload(self):
        """Create multi-task payload for Path D testing."""
        prompt = """1. First task
2. Second task
3. Third task"""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt=prompt,
        )

    @pytest.fixture
    def tool_execution_payload(self):
        """Create payload with tool execution intent for Path C testing."""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt="Execute the data analysis tool",
        )

    def test_path_b_policy_check_first(self, orchestrator, sample_payload):
        """Test Path B: Policy Check First orchestration."""
        trace_id = "test_trace_b_001"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2")

        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "B"
        assert result.plan_hash is not None
        assert result.execution_trace is not None
        assert result.handshake_state == HandshakeState.SEALED
        assert result.determinism_digest is not None
        assert result.metadata is not None

        # Verify Path B specific metadata
        assert result.metadata["policy_check"] == "completed"
        assert result.metadata["certification"] == "granted"
        assert result.metadata["sealed"] is True

        # Verify execution trace
        assert result.execution_trace["trace_id"] == trace_id
        assert result.execution_trace["plan_hash"] == result.plan_hash
        assert result.execution_trace["actor"] == "L3_Orchestrator"

    def test_path_c_execute_script_directly(self, orchestrator, tool_execution_payload):
        """Test Path C: Execute Script Directly orchestration."""
        trace_id = "test_trace_c_001"
        policy_hash = "policy_hash_001"
        allowed_tools = ("data_analysis", "execute")

        result = orchestrator.orchestrate(
            governed_payload=tool_execution_payload,
            route_mode="C",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "C"
        assert result.plan_hash is not None
        assert result.execution_trace is not None
        assert result.handshake_state == HandshakeState.SEALED
        assert result.determinism_digest is not None

        # Verify Path C specific metadata
        assert result.metadata["tool_execution_detected"] is True
        assert result.metadata["certification_required"] is True
        assert result.metadata["sealed"] is True

    def test_path_c_without_tool_intent(self, orchestrator, sample_payload):
        """Test Path C without tool execution intent."""
        trace_id = "test_trace_c_002"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2")

        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="C",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "C"

        # Verify no tool execution detected
        assert result.metadata["tool_execution_detected"] is False
        assert result.metadata["certification_required"] is False

    def test_path_d_human_review_first(self, orchestrator, multi_task_payload):
        """Test Path D: Human Review First orchestration."""
        trace_id = "test_trace_d_001"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2", "tool3")

        result = orchestrator.orchestrate(
            governed_payload=multi_task_payload,
            route_mode="D",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "D"
        assert result.plan_hash is not None
        assert result.execution_trace is not None
        assert result.determinism_digest is not None

        # Verify Path D specific properties
        assert result.human_decision_artifact is not None
        assert result.metadata["human_review_required"] is True
        assert result.metadata["dispatched_to_l2"] is False
        assert result.metadata["awaiting_human_decision"] is True

        # Verify human decision artifact
        artifact = result.human_decision_artifact
        assert artifact["trace_id"] == trace_id
        assert artifact["policy_hash"] == policy_hash
        assert artifact["original_plan_hash"] == result.plan_hash
        assert artifact["reviewer_id"] is None  # Draft state
        assert artifact["action"] == HumanAction.MODIFY_DIFF.value

    def test_invalid_route_mode_raises_error(self, orchestrator, sample_payload):
        """Test that invalid route mode raises ValueError."""
        with pytest.raises(ValueError, match="is not a valid RouteMode"):
            orchestrator.orchestrate(
                governed_payload=sample_payload,
                route_mode="INVALID",
                trace_id="test_trace",
                policy_hash="policy_hash",
                allowed_tools=(),
            )

    def test_deterministic_plan_hash(self, orchestrator, sample_payload):
        """Test that plan hash is deterministic across runs."""
        trace_id = "test_trace_deterministic"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2")

        # Run orchestration twice with identical inputs
        result1 = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        result2 = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Plan hashes should be identical
        assert result1.plan_hash == result2.plan_hash

        # Verify plan hash is valid SHA256
        assert len(result1.plan_hash) == 64
        assert all(c in "0123456789abcdef" for c in result1.plan_hash)

    def test_determinism_digest_format(self, orchestrator, sample_payload):
        """Test that determinism digest has correct format."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_trace",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Verify digest format
        assert result.determinism_digest is not None
        assert len(result.determinism_digest) == 64
        assert all(c in "0123456789abcdef" for c in result.determinism_digest)

        # Verify digest was printed to stdout (captured in test output)
        assert f"W5-DETERMINISM-DIGEST: {result.determinism_digest}" in result.metadata.get(
            "digest_output", ""
        )

    def test_execution_trace_structure(self, orchestrator, sample_payload):
        """Test execution trace has proper structure."""
        trace_id = "test_trace_structure"
        policy_hash = "policy_hash_001"

        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=(),
        )

        trace = result.execution_trace
        assert trace is not None
        assert "trace_id" in trace
        assert "plan_hash" in trace
        assert "actor" in trace
        assert "governed_payload_hash" in trace
        assert "timestamp" in trace

        assert trace["trace_id"] == trace_id
        assert trace["plan_hash"] == result.plan_hash
        assert trace["actor"] == "L3_Orchestrator"

    def test_handshake_state_transitions_path_b(self, orchestrator, sample_payload):
        """Test proper handshake state transitions for Path B."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_handshake",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Path B should end in SEALED state after certification
        assert result.handshake_state == HandshakeState.SEALED

    def test_handshake_state_transitions_path_c(self, orchestrator, sample_payload):
        """Test proper handshake state transitions for Path C."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="C",
            trace_id="test_handshake",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Path C should end in SEALED state
        assert result.handshake_state == HandshakeState.SEALED

    def test_handshake_state_transitions_path_d(self, orchestrator, multi_task_payload):
        """Test proper handshake state transitions for Path D."""
        result = orchestrator.orchestrate(
            governed_payload=multi_task_payload,
            route_mode="D",
            trace_id="test_handshake",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Path D should not reach SEALED state (stops for human review)
        assert result.handshake_state == HandshakeState.INIT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
