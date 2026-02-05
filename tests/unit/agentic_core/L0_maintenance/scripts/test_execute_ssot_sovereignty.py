"""
File: tests/unit/agentic_core/L0_maintenance/scripts/test_execute_ssot_sovereignty.py
"""

from unittest.mock import MagicMock

import pytest

from agentic_core.L0_maintenance.scripts.general_scripts.execute_ssot import (
    PreFlightValidator,
    SovereignDecisionEngine,
)


@pytest.fixture
def mock_state_mgr():
    return MagicMock()


@pytest.fixture
def sovereign_engine(mock_state_mgr):
    return SovereignDecisionEngine(enable_llm=False, state_mgr=mock_state_mgr)


def test_sovereignty_token_acquisition(sovereign_engine):
    """Verify atomic token locking mechanism."""
    # First request should succeed
    assert sovereign_engine.request_sovereignty_token("TestAgent", "FIX") is True
    assert sovereign_engine._atomic_lock is True
    assert "TestAgent" in sovereign_engine._sovereignty_token

    # Concurrent request should be denied
    assert sovereign_engine.request_sovereignty_token("RogueAgent", "FIX") is False


def test_sovereignty_token_release(sovereign_engine):
    """Verify token release unlocks the engine."""
    sovereign_engine.request_sovereignty_token("TestAgent", "FIX")
    sovereign_engine.release_sovereignty_token("TestAgent", success=True)

    assert sovereign_engine._atomic_lock is False
    assert sovereign_engine._sovereignty_token is None

    # Should perform next op
    assert sovereign_engine.request_sovereignty_token("NextAgent", "FIX") is True


def test_cycle_detection(sovereign_engine):
    """Verify recursive calls are blocked."""
    sovereign_engine.request_sovereignty_token("AgentA", "OP_1")
    # Note: request_sovereignty_token blocks any secondary request if locked.
    # To test cycle detection specifically we simulate the stack state.

    sovereign_engine._atomic_lock = False
    sovereign_engine._operation_stack.append("AgentA:OP_1")

    assert sovereign_engine.request_sovereignty_token("AgentA", "OP_1") is False


def test_stack_depth_limit(sovereign_engine):
    """Verify recursion limit."""
    sovereign_engine._atomic_lock = False
    # Fill stack
    for i in range(10):
        sovereign_engine._operation_stack.append(f"Op_{i}")

    assert sovereign_engine.request_sovereignty_token("OverflowAgent", "FIX") is False


def test_preflight_validator_structure(tmp_path):
    """Verify directory structure enforcement."""
    # Create valid structure
    (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
    (tmp_path / "agentic_core" / "prompt_governance").mkdir(parents=True)

    validator = PreFlightValidator(tmp_path)
    ok, errors = validator.run_checks()
    assert ok is True
    assert len(errors) == 0


def test_preflight_validator_missing_dirs(tmp_path):
    """Verify missing directory detection."""
    # Empty root
    validator = PreFlightValidator(tmp_path)
    ok, errors = validator.run_checks()
    assert ok is False
    assert any("Critical directory missing" in e for e in errors)


def test_agent_integrity_validation(tmp_path):
    """Verify agent interface compliance."""
    validator = PreFlightValidator(tmp_path)

    class ValidAgent:
        def heal(self, v):
            pass

    class InvalidAgent:
        pass

    agents = {"Valid": ValidAgent(), "Invalid": InvalidAgent()}
    errors = validator.validate_agent_integrity(agents)

    assert len(errors) == 1
    assert "Invalid" in errors[0]
