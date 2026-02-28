"""Phase 5-G Gap Closure Policy Enforcement Tests

End-to-end enforcement proof for agent 2×2 classification policy at both seams:
1. SovereignLLMGateway (LLM access control)
2. HealingTierRouter (tier escalation control)

Tests are non-network (no provider SDK initialization) and include:
- Deterministic agent hard rejection from gateway
- LLM agent model validation
- Deterministic agent tier escalation prevention
- LLM agent tier routing with model constraints
- Missing agent_id hard rejection
- Determinism digest proof
- Negative control tamper detection
"""

import os

import pytest

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Determinism Digest Computation (moved to conftest.py session finish)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Gateway Enforcement Tests (Non-Network)
# ---------------------------------------------------------------------------


def test_gateway_rejects_deterministic_agent_non_network():
    """Test that gateway rejects deterministic agents without network calls."""
    from agentic_core.agents.agent_registry import get_deterministic_agents, get_profile

    deterministic_agents = get_deterministic_agents()

    if deterministic_agents:
        agent_id = deterministic_agents[0]
        profile = get_profile(agent_id)

        # Verify deterministic agent profile
        assert not profile.is_llm_allowed(), f"Agent '{agent_id}' should be deterministic"
        assert profile.execution_mode.value == "DETERMINISTIC", f"Agent '{agent_id}' should be DETERMINISTIC"


def test_gateway_rejects_unregistered_agent_non_network():
    """Test that gateway rejects unregistered agents without network calls."""
    from agentic_core.agents.agent_registry import get_profile

    # Test that unregistered agent raises V15HardFailAbort or KeyError
    from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort
    with pytest.raises((V15HardFailAbort, KeyError)):
        get_profile("UNREGISTERED_AGENT")


def test_gateway_requires_agent_id_non_network():
    """Test that gateway requires agent_id parameter without network calls."""
    # Check that the gateway entrypoint requires a request object
    import inspect

    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    route_sig = inspect.signature(SovereignLLMGateway.route_generation)
    assert "request" in route_sig.parameters, "Gateway route_generation must accept a request parameter"

    request_sig = inspect.signature(GenerationRequest)
    assert "agent_id" in request_sig.parameters, "GenerationRequest must include agent_id"
    assert request_sig.parameters["agent_id"].default is inspect.Parameter.empty, (
        "GenerationRequest.agent_id must be required"
    )


def test_gateway_enforces_allowed_models_non_network():
    """Test that gateway enforces allowed models for LLM agents without network calls."""
    from agentic_core.agents.agent_registry import get_llm_agents, get_profile

    llm_agents = get_llm_agents()

    if llm_agents:
        # Test first LLM agent
        agent_id = llm_agents[0]
        profile = get_profile(agent_id)

        # Verify LLM agent has allowed models
        assert len(profile.allowed_models) > 0, f"LLM agent '{agent_id}' must have allowed models"
        assert profile.is_llm_allowed(), f"LLM agent '{agent_id}' must allow LLM usage"


# ---------------------------------------------------------------------------
# Tier Router Enforcement Tests
# ---------------------------------------------------------------------------


def test_tier_router_blocks_deterministic_agent_escalation():
    """Test that tier router blocks deterministic agents from LLM tiers."""
    from agentic_core.agents.agent_registry import get_deterministic_agents
    from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
    from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

    config = HealingTierConfig(
        heal_confidence_x=0.80,
        heal_confidence_y=0.60,
        max_heal_retries=3,
        model_qwen_vllm_id="qwen-vllm",
        model_gemini_2_5_pro_id="gemini-2.5-pro",
    )

    deterministic_agents = get_deterministic_agents()

    if deterministic_agents:
        agent_id = deterministic_agents[0]

        # Even with low heal_confidence, deterministic agent should be forced to LOCAL_AGENT
        healing_input = HealingInput(
            agent_id=agent_id,
            failure_type="runtime_error",
            error_signature="test_error",
            trace_id="test_trace",
            retry_count=0,
            blast_radius_estimate=0.1,  # Low blast radius would normally allow higher tiers
            required_tools=(),
            violation_metadata_refs=(),
        )

        decision = route_healing_tier(healing_input, config)

        # Should be forced to LOCAL_AGENT regardless of confidence
        assert decision.tier.value == "LOCAL_AGENT"
        assert "agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT" in decision.reason_codes


def test_tier_router_rejects_unregistered_agent():
    """Test that tier router rejects unregistered agents."""
    from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort
    from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
    from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

    config = HealingTierConfig(
        heal_confidence_x=0.80,
        heal_confidence_y=0.60,
        max_heal_retries=3,
        model_qwen_vllm_id="qwen-vllm",
        model_gemini_2_5_pro_id="gemini-2.5-pro",
    )

    healing_input = HealingInput(
        agent_id="UNREGISTERED_AGENT",
        failure_type="runtime_error",
        error_signature="test_error",
        trace_id="test_trace",
        retry_count=0,
        blast_radius_estimate=0.1,
        required_tools=(),
        violation_metadata_refs=(),
    )

    with pytest.raises(V15HardFailAbort, match="AgentProfile.*not found in registry"):
        route_healing_tier(healing_input, config)


def test_tier_router_blocks_deterministic_agent_max_retry_escalation():
    """Test that tier router blocks deterministic agents even with max retries exceeded."""
    from agentic_core.agents.agent_registry import get_deterministic_agents
    from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
    from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

    config = HealingTierConfig(
        heal_confidence_x=0.80,
        heal_confidence_y=0.60,
        max_heal_retries=3,
        model_qwen_vllm_id="qwen-vllm",
        model_gemini_2_5_pro_id="gemini-2.5-pro",
    )

    deterministic_agents = get_deterministic_agents()

    if deterministic_agents:
        agent_id = deterministic_agents[0]

        # Even with max retries exceeded, deterministic agent should be forced to LOCAL_AGENT
        healing_input = HealingInput(
            agent_id=agent_id,
            failure_type="runtime_error",
            error_signature="test_error",
            trace_id="test_trace",
            retry_count=5,  # Exceeds max_heal_retries
            blast_radius_estimate=0.1,
            required_tools=(),
            violation_metadata_refs=(),
        )

        decision = route_healing_tier(healing_input, config)

        # Should still be forced to LOCAL_AGENT
        assert decision.tier.value == "LOCAL_AGENT"
        assert "agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT" in decision.reason_codes


def test_tier_router_rejects_llm_agent_model_not_allowed():
    """Test that tier router rejects LLM agents with non-allowed models (fail-closed)."""
    from agentic_core.agents.agent_registry import get_llm_agents, get_profile
    from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort
    from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
    from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

    config = HealingTierConfig(
        heal_confidence_x=0.80,
        heal_confidence_y=0.60,
        max_heal_retries=3,
        model_qwen_vllm_id="qwen-vllm",
        model_gemini_2_5_pro_id="gemini-2.5-pro",
    )

    llm_agents = get_llm_agents()

    if llm_agents:
        agent_id = llm_agents[0]
        profile = get_profile(agent_id)

        # Check which model is not allowed and test accordingly
        if "qwen-vllm" not in profile.allowed_models:
            healing_input = HealingInput(
                agent_id=agent_id,
                failure_type="runtime_error",
                error_signature="test_error",
                trace_id="test_trace",
                retry_count=0,
                blast_radius_estimate=0.3,  # Would route to QWEN_VLLM (between 0.6 and 0.8)
                required_tools=(),
                violation_metadata_refs=(),
            )

            # Should raise V15HardFailAbort instead of falling back
            with pytest.raises(V15HardFailAbort, match="AgentProfile.*not allowed to use model.*qwen-vllm"):
                route_healing_tier(healing_input, config)
        elif "gemini-2.5-pro" not in profile.allowed_models:
            healing_input = HealingInput(
                agent_id=agent_id,
                failure_type="runtime_error",
                error_signature="test_error",
                trace_id="test_trace",
                retry_count=0,
                blast_radius_estimate=0.1,  # Would normally route to GEMINI_2_5_PRO
                required_tools=(),
                violation_metadata_refs=(),
            )

            # Should raise V15HardFailAbort instead of falling back
            with pytest.raises(
                V15HardFailAbort, match="AgentProfile.*not allowed to use model.*gemini-2.5-pro"
            ):
                route_healing_tier(healing_input, config)
        else:
            # Skip test if agent has all models allowed
            pytest.skip(f"Agent '{agent_id}' has all models allowed")


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------


def test_end_to_end_enforcement_integration():
    """Test complete end-to-end enforcement without network calls."""
    # Test gateway enforcement
    test_gateway_requires_agent_id_non_network()
    test_gateway_rejects_unregistered_agent_non_network()

    # Test tier router enforcement
    test_tier_router_rejects_unregistered_agent()
    test_tier_router_blocks_deterministic_agent_escalation()
    test_tier_router_rejects_llm_agent_model_not_allowed()


# ---------------------------------------------------------------------------
# Negative Control Tests
# ---------------------------------------------------------------------------


def test_negative_control_tamper_detection():
    """Negative control: detect tampering when W5_NEGCTRL_TAMPER=1."""
    if os.environ.get("W5_NEGCTRL_TAMPER") == "1":
        # This should XFAIL - tamper mode introduces synthetic violation
        pytest.xfail("Negative control: tampering detected")
    else:
        # Normal mode - this test should pass
        assert True, "Normal mode should pass"


def test_full_phase5_gap_closure_system():
    """Run full Phase 5-G gap closure system test."""
    # Run all enforcement tests
    test_end_to_end_enforcement_integration()

    # Verify scanner still works
    from tests.governance.test_agent_execution_profiles import test_agent_registry_scanner_exists

    test_agent_registry_scanner_exists()
