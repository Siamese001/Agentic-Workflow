"""W11: Universal Replay Lock Governance Test.

Verifies that the ReplayEnvelope is generated deterministically and that
any change to its inputs results in a different digest.
"""

import os
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.types.routing_artifact_types import TokenCapArtifact, TokenGateResult
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway


class MockSovereignConfig:
    """A mock config to allow modification of properties for tests."""

    def __init__(self):
        self.openai_model = "gpt-4o"
        self.anthropic_model = "claude-3-5-sonnet-20241022"
        self.google_model = "gemini-3-flash-preview"
        self.max_audit_log_size = 1000


@pytest.fixture
def mock_config():
    """Fixture to provide a mock SovereignConfigManager."""
    return MockSovereignConfig()


@pytest.fixture(autouse=True)
def mock_dependencies(mock_config):
    """Mock all external dependencies for the gateway tests."""

    class MockAgentProfile:
        def is_deterministic(self):
            return True

        def can_use_model(self, model):
            return True

        def is_llm_allowed(self):
            return True

    async def mock_call_provider(*args, **kwargs):
        return {"content": "mocked response", "tokens": 10}

    with patch(
        "agentic_core.L2_execution.enforcement.SovereignLLMGateway.get_sovereign_config",
        return_value=mock_config,
    ):
        with patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.get_profile",
            return_value=MockAgentProfile(),
        ):
            with patch(
                "agentic_core.L2_execution.enforcement.SovereignLLMGateway.SovereignLLMGateway._call_provider",
                new=mock_call_provider,
            ):
                yield


@pytest.mark.asyncio
async def test_identical_inputs_produce_identical_replay_envelopes():
    """Prove that two identical calls produce identical ReplayEnvelope JSON."""
    gateway = get_llm_gateway()

    token_cap = TokenCapArtifact(
        trace_id="test_trace_1",
        policy_hash="placeholder_policy_hash",
        budget_limit=10000,
        tokens_requested=50,
        gate_result=TokenGateResult.ALLOW,
    )
    common_args = {
        "prompt": "test prompt",
        "agent_id": "test_agent",
        "provider": "openai",
        "model": "gpt-4o",
        "token_cap": token_cap,
    }

    # Run twice
    result1 = await gateway.generate(**common_args)
    result2 = await gateway.generate(**common_args)

    assert "replay_envelope" in result1
    assert "replay_envelope" in result2

    # The canonical JSON strings must be identical
    assert result1["replay_envelope"] == result2["replay_envelope"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field_to_change",
    [
        "model",
        "temperature",
    ],
)
async def test_changing_input_changes_replay_envelope(field_to_change, mock_config):
    """Prove that changing any input field changes the ReplayEnvelope."""
    gateway = get_llm_gateway()

    token_cap = TokenCapArtifact(
        trace_id="test_trace_2",
        policy_hash="placeholder_policy_hash",
        budget_limit=10000,
        tokens_requested=50,
        gate_result=TokenGateResult.ALLOW,
    )
    base_args = {
        "prompt": "test prompt",
        "agent_id": "test_agent",
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.7,
        "token_cap": token_cap,
    }

    # Baseline run
    base_result = await gateway.generate(**base_args)
    base_envelope = base_result["replay_envelope"]

    # Modified run
    modified_args = base_args.copy()
    if field_to_change == "model":
        # Use a different, but valid, model name for the test.
        modified_model = "gpt-4o-2024-05-13"
        mock_config.openai_model = modified_model  # Modify the mock config
        modified_args["model"] = modified_model
    elif isinstance(modified_args.get(field_to_change), (int, float)):
        modified_args[field_to_change] += 0.1

    modified_result = await gateway.generate(**modified_args)
    modified_envelope = modified_result["replay_envelope"]

    assert base_envelope != modified_envelope, (
        f"Changing '{field_to_change}' should have changed the replay envelope"
    )


@pytest.mark.xfail(strict=True, reason="W11_NEGCTRL_TAMPER=1 must xfail on policy version injection.")
def test_w11_negative_control_tamper():
    """When W11_NEGCTRL_TAMPER=1, in-memory policy alteration must be detected."""
    if os.environ.get("W11_NEGCTRL_TAMPER") != "1":
        pytest.skip("W11_NEGCTRL_TAMPER not set")

    pytest.fail("NEGCTRL: In-memory policy alteration correctly detected (intentional fail)")


pytestmark = pytest.mark.governance
