#!/usr/bin/env python3
"""
Simple test runner for W5 L3 orchestration implementation.
Bypasses pytest configuration issues to verify functionality.
"""

import sys

sys.path.insert(0, ".")

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler
from agentic_core.L3_orchestration.engines.deterministic_orchestrator import DeterministicOrchestrator
from agentic_core.L3_orchestration.engines.handshake_state_machine import HandshakeState


def test_path_b():
    """Test Path B: Policy Check First."""
    print("Testing Path B: Policy Check First...")

    orchestrator = DeterministicOrchestrator()
    payload = AirlockAssembler.assemble(
        s0_system="Test System",
        i0_instructional="Test Instructions",
        c0_context="Test Context",
        u0_user_prompt="Single task prompt",
    )

    result = orchestrator.orchestrate(
        governed_payload=payload,
        route_mode="B",
        trace_id="test_trace_b_001",
        policy_hash="policy_hash_001",
        allowed_tools=("tool1", "tool2"),
    )

    assert result.success is True
    assert result.route_mode == "B"
    assert result.plan_hash is not None
    assert result.execution_trace is not None
    assert result.handshake_state == HandshakeState.SEALED
    assert result.determinism_digest is not None
    assert result.metadata["policy_check"] == "completed"
    assert result.metadata["certification"] == "granted"
    assert result.metadata["sealed"] is True

    print(f"✓ Path B test passed - Digest: {result.determinism_digest[:16]}...")
    return result.determinism_digest


def test_path_c():
    """Test Path C: Execute Script Directly."""
    print("Testing Path C: Execute Script Directly...")

    orchestrator = DeterministicOrchestrator()
    payload = AirlockAssembler.assemble(
        s0_system="Test System",
        i0_instructional="Test Instructions",
        c0_context="Test Context",
        u0_user_prompt="Execute the data analysis tool",
    )

    result = orchestrator.orchestrate(
        governed_payload=payload,
        route_mode="C",
        trace_id="test_trace_c_001",
        policy_hash="policy_hash_001",
        allowed_tools=("data_analysis", "execute"),
    )

    assert result.success is True
    assert result.route_mode == "C"
    assert result.plan_hash is not None
    assert result.execution_trace is not None
    assert result.handshake_state == HandshakeState.SEALED
    assert result.determinism_digest is not None
    assert result.metadata["tool_execution_detected"] is True
    assert result.metadata["certification_required"] is True

    print(f"✓ Path C test passed - Digest: {result.determinism_digest[:16]}...")
    return result.determinism_digest


def test_path_d():
    """Test Path D: Human Review First."""
    print("Testing Path D: Human Review First...")

    orchestrator = DeterministicOrchestrator()
    prompt = """1. First task
2. Second task
3. Third task"""
    payload = AirlockAssembler.assemble(
        s0_system="Test System",
        i0_instructional="Test Instructions",
        c0_context="Test Context",
        u0_user_prompt=prompt,
    )

    result = orchestrator.orchestrate(
        governed_payload=payload,
        route_mode="D",
        trace_id="test_trace_d_001",
        policy_hash="policy_hash_001",
        allowed_tools=("tool1", "tool2", "tool3"),
    )

    assert result.success is True
    assert result.route_mode == "D"
    assert result.plan_hash is not None
    assert result.execution_trace is not None
    assert result.determinism_digest is not None
    assert result.human_decision_artifact is not None
    assert result.metadata["human_review_required"] is True
    assert result.metadata["dispatched_to_l2"] is False
    assert result.metadata["awaiting_human_decision"] is True
    assert result.handshake_state == HandshakeState.INIT

    print(f"✓ Path D test passed - Digest: {result.determinism_digest[:16]}...")
    return result.determinism_digest


def test_determinism():
    """Test that identical inputs produce identical digests."""
    print("Testing determinism...")

    orchestrator = DeterministicOrchestrator()
    payload = AirlockAssembler.assemble(
        s0_system="Test System",
        i0_instructional="Test Instructions",
        c0_context="Test Context",
        u0_user_prompt="Test prompt",
    )

    params = {
        "governed_payload": payload,
        "route_mode": "B",
        "trace_id": "test_trace_deterministic",
        "policy_hash": "policy_hash_001",
        "allowed_tools": ("tool1", "tool2"),
    }

    # Run twice with identical inputs
    result1 = orchestrator.orchestrate(**params)
    result2 = orchestrator.orchestrate(**params)

    assert result1.determinism_digest == result2.determinism_digest
    print(f"✓ Determinism test passed - Identical digest: {result1.determinism_digest[:16]}...")
    return result1.determinism_digest


def test_handshake_state_machine():
    """Test handshake state machine."""
    print("Testing handshake state machine...")

    from agentic_core.L3_orchestration.engines.handshake_state_machine import HandshakeStateMachine

    machine = HandshakeStateMachine()
    assert machine.current_state == HandshakeState.INIT

    # Test full sequence
    machine.request_preclear()
    assert machine.current_state == HandshakeState.PRECLEAR_REQUESTED

    machine.certify()
    assert machine.current_state == HandshakeState.CERTIFIED

    machine.seal()
    assert machine.current_state == HandshakeState.SEALED

    machine.dispatch()
    assert machine.current_state == HandshakeState.DISPATCHED

    # Test sequence hash
    sequence_hash = machine.get_sequence_hash()
    assert len(sequence_hash) == 64
    print(f"✓ Handshake state machine test passed - Sequence hash: {sequence_hash[:16]}...")
    return sequence_hash


def main():
    """Run all W5 tests."""
    print("=== W5 L3 Orchestration Test Suite ===\n")

    try:
        # Run individual path tests
        digest_b = test_path_b()
        digest_c = test_path_c()
        digest_d = test_path_d()

        # Verify different paths produce different digests
        assert digest_b != digest_c != digest_d
        print("✓ Different paths produce different digests")

        # Test determinism
        deterministic_digest = test_determinism()

        # Test handshake state machine
        sequence_hash = test_handshake_state_machine()

        print("\n=== W5 Test Suite PASSED ===")
        print(f"Path B digest: {digest_b}")
        print(f"Path C digest: {digest_c}")
        print(f"Path D digest: {digest_d}")
        print(f"Deterministic digest: {deterministic_digest}")
        print(f"Handshake sequence hash: {sequence_hash}")

        # Print the single W5-DETERMINISM-DIGEST as required
        print(f"\nW5-DETERMINISM-DIGEST: {deterministic_digest}")

        return 0

    except Exception as e:
        print("\n=== W5 Test Suite FAILED ===")
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
