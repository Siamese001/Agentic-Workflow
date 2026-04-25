"""Comprehensive tests for write_adapter_gated.py module."""

import pytest

from agentic_core.L5_safety.identity.write_adapter_gated import WriteRefused, emit_lane_gated_write
from agentic_core.interfaces.principal_aware_write import PrincipalAttachedWrite


@pytest.fixture
def sample_allow_decision():
    """Sample runtime lane decision with allow action."""
    # Use a simple mock object with the required fields
    class MockDecision:
        def __init__(self, final_action):
            self.sweep = None
            self.risk_tier = None
            self.chokepoint = None
            self.handoff = None
            self.final_action = final_action

    return MockDecision("allow")


@pytest.fixture
def sample_reject_decision():
    """Sample runtime lane decision with reject action."""
    class MockDecision:
        def __init__(self, final_action):
            self.sweep = None
            self.risk_tier = None
            self.chokepoint = None
            self.handoff = None
            self.final_action = final_action

    return MockDecision("reject")


def test_write_refused_exception(sample_reject_decision):
    """Test WriteRefused exception carries decision."""
    exception = WriteRefused(sample_reject_decision)

    assert "final_action=reject" in str(exception)
    assert exception.decision == sample_reject_decision
    assert exception.decision.final_action == "reject"


def test_emit_lane_gated_write_soft_mode_allow(
    sample_v4_token,
    sample_allow_decision,
    monkeypatch,
):
    """Test emit_lane_gated_write in soft mode when decision allows."""
    # Mock evaluate_runtime_lane_with_sweep to return allow decision
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.evaluate_runtime_lane_with_sweep",
        lambda *args, **kwargs: sample_allow_decision,
    )

    # Mock emit_v4_write to return sample values
    mock_v3_key = "v3_key_123"
    mock_attached = PrincipalAttachedWrite(
        plan_hash="plan_hash_abc",
        tool_calls=("tool1", "tool2"),
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff",
        principal_chain=sample_v4_token.principal_chain,
        principal_chain_digest="digest_123",
        principal_replay_key="replay_key_123",
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.emit_v4_write",
        lambda *args, **kwargs: (mock_v3_key, mock_attached),
    )

    v3_key, attached, decision = emit_lane_gated_write(
        token=sample_v4_token,
        plan_hash="plan_hash_abc",
        tool_calls=["tool1", "tool2"],
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff",
        strict=False,
    )

    assert v3_key == mock_v3_key
    assert attached == mock_attached
    assert decision == sample_allow_decision
    assert decision.final_action == "allow"


def test_emit_lane_gated_write_soft_mode_reject(
    sample_v4_token,
    sample_reject_decision,
    monkeypatch,
):
    """Test emit_lane_gated_write in soft mode when decision rejects."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.evaluate_runtime_lane_with_sweep",
        lambda *args, **kwargs: sample_reject_decision,
    )

    v3_key, attached, decision = emit_lane_gated_write(
        token=sample_v4_token,
        plan_hash="plan_hash_abc",
        tool_calls=["tool1", "tool2"],
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff",
        strict=False,
    )

    # In soft mode, should return None for v3_key and attached, but decision is returned
    assert v3_key is None
    assert attached is None
    assert decision == sample_reject_decision
    assert decision.final_action == "reject"


def test_emit_lane_gated_write_strict_mode_reject(
    sample_v4_token,
    sample_reject_decision,
    monkeypatch,
):
    """Test emit_lane_gated_write in strict mode when decision rejects."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.evaluate_runtime_lane_with_sweep",
        lambda *args, **kwargs: sample_reject_decision,
    )

    with pytest.raises(WriteRefused) as exc_info:
        emit_lane_gated_write(
            token=sample_v4_token,
            plan_hash="plan_hash_abc",
            tool_calls=["tool1", "tool2"],
            stdout_digest="stdout_digest",
            state_diff_hash="state_diff",
            strict=True,
        )

    # Exception should carry the decision
    assert exc_info.value.decision == sample_reject_decision
    assert exc_info.value.decision.final_action == "reject"


def test_emit_lane_gated_write_strict_mode_allow(
    sample_v4_token,
    sample_allow_decision,
    monkeypatch,
):
    """Test emit_lane_gated_write in strict mode when decision allows."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.evaluate_runtime_lane_with_sweep",
        lambda *args, **kwargs: sample_allow_decision,
    )

    mock_v3_key = "v3_key_123"
    mock_attached = PrincipalAttachedWrite(
        plan_hash="plan_hash_abc",
        tool_calls=("tool1", "tool2"),
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff",
        principal_chain=sample_v4_token.principal_chain,
        principal_chain_digest="digest_123",
        principal_replay_key="replay_key_123",
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.emit_v4_write",
        lambda *args, **kwargs: (mock_v3_key, mock_attached),
    )

    v3_key, attached, decision = emit_lane_gated_write(
        token=sample_v4_token,
        plan_hash="plan_hash_abc",
        tool_calls=["tool1", "tool2"],
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff",
        strict=True,
    )

    # In strict mode with allow, should behave like soft mode
    assert v3_key == mock_v3_key
    assert attached == mock_attached
    assert decision == sample_allow_decision


def test_emit_lane_gated_write_passes_optional_parameters(
    sample_v4_token,
    sample_allow_decision,
    monkeypatch,
):
    """Test emit_lane_gated_write passes optional parameters to evaluate_runtime_lane_with_sweep."""
    evaluate_calls = []

    def mock_evaluate(*args, **kwargs):
        evaluate_calls.append((args, kwargs))
        return sample_allow_decision

    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.evaluate_runtime_lane_with_sweep",
        mock_evaluate,
    )

    mock_v3_key = "v3_key_123"
    mock_attached = PrincipalAttachedWrite(
        plan_hash="plan_hash_abc",
        tool_calls=("tool1", "tool2"),
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff",
        principal_chain=sample_v4_token.principal_chain,
        principal_chain_digest="digest_123",
        principal_replay_key="replay_key_123",
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.write_adapter_gated.emit_v4_write",
        lambda *args, **kwargs: (mock_v3_key, mock_attached),
    )

    from agentic_core.L5_safety.identity.guardrail_bank import GuardrailFamily, GuardrailOutcome

    guardrail_outcome = GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="allow",
        score=0.0,
        evidence="no_pii",
    )

    v3_key, attached, decision = emit_lane_gated_write(
        token=sample_v4_token,
        plan_hash="plan_hash_abc",
        tool_calls=["tool1", "tool2"],
        stdout_digest="stdout_digest",
        state_diff_hash="state_diff",
        action_connector_id="test_connector",
        action_tool_id="test_tool",
        touches_write_surface=True,
        ingress_outcomes=[guardrail_outcome],
        egress_outcomes=[guardrail_outcome],
        guard_model_outcome=None,
    )

    # Verify optional parameters were passed
    assert len(evaluate_calls) == 1
    kwargs = evaluate_calls[0][1]
    assert kwargs["action_connector_id"] == "test_connector"
    assert kwargs["action_tool_id"] == "test_tool"
    assert kwargs["touches_write_surface"] is True
    assert len(kwargs["ingress_outcomes"]) == 1
    assert len(kwargs["egress_outcomes"]) == 1
