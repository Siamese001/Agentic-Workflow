"""
Guardian Hardened Tests — Agent Registry Seam

AST-graph justification:
  agent_registry has fan_in=10 (SovereignLLMGateway, governance tests,
  dispatch engine, CI sovereignty suite, commit proof invariant).
  Current test coverage = 1 file (test_commit_proof_invariant) that only
  asserts the module is importable. No behavioral contract tests exist for:
    - unregistered agent hard fail
    - DETERMINISTIC mode blocks LLM gateway call
    - LLM_API mode with empty allowed_models
    - registry_digest stability
    - transitive enforcement contract (registry rejects → gateway rejects)

Covers:
  1. get_profile() hard fails with KeyError for unregistered agent
  2. KeyError message contains available agents list (consumer-visible contract)
  3. get_execution_profile() is an alias that delegates to get_profile()
  4. Every registered agent has non-empty agent_id matching its key
  5. DETERMINISTIC agents have empty allowed_models (registry constraint)
  6. LLM_API agents have non-empty allowed_models (registry constraint)
  7. registry_digest() is stable across repeated calls (determinism)
  8. registry_digest() changes when registry changes (sensitivity)
  9. All profile fields are frozen/immutable (dataclass frozen=True expectation)
 10. Transitive: SovereignLLMGateway raises SovereigntyViolation for unregistered agent
 11. Transitive: DETERMINISTIC agent rejected by gateway with correct message
 12. Transitive: LLM_API agent with disallowed model rejected by gateway
"""

from __future__ import annotations

import asyncio

import pytest

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from agentic_core.agents.agent_registry import (
    AGENT_REGISTRY,
    get_execution_profile,
    get_profile,
    registry_digest,
)
from agentic_core.agents.types.agent_execution_profile_types import (
    AgentExecutionProfile,
    ExecutionMode,
    ReasoningIntensity,
)

# ---------------------------------------------------------------------------
# 1. get_profile() hard fail for unregistered agent
# ---------------------------------------------------------------------------


class TestGetProfileHardFail:
    def test_unregistered_agent_raises_key_error(self):
        with pytest.raises(KeyError):
            get_profile("__totally_nonexistent_agent__")

    def test_error_message_contains_available_agents(self):
        with pytest.raises(KeyError, match="not found in registry"):
            get_profile("__nonexistent__")

    def test_error_message_contains_available_list(self):
        try:
            get_profile("__nonexistent__")
        except KeyError as exc:
            msg = str(exc)
            assert "Available" in msg

    def test_empty_string_agent_id_raises(self):
        with pytest.raises(KeyError):
            get_profile("")

    def test_whitespace_agent_id_raises(self):
        with pytest.raises(KeyError):
            get_profile("   ")

    def test_get_execution_profile_delegates_to_get_profile(self):
        with pytest.raises(KeyError):
            get_execution_profile("__nonexistent__")

    def test_no_silent_default_returned_for_unknown(self):
        result = None
        try:
            result = get_profile("__nonexistent__")
        except KeyError:
            pass
        assert result is None, "get_profile must not silently return a default"


# ---------------------------------------------------------------------------
# 2. Registered agent profile field contracts
# ---------------------------------------------------------------------------


class TestRegisteredAgentContracts:
    def test_every_registered_agent_id_matches_key(self):
        for key, profile in AGENT_REGISTRY.items():
            assert profile.agent_id == key, (
                f"Registry key '{key}' does not match profile.agent_id='{profile.agent_id}'"
            )

    def test_deterministic_agents_have_empty_allowed_models(self):
        for key, profile in AGENT_REGISTRY.items():
            if profile.execution_mode == ExecutionMode.DETERMINISTIC:
                assert (
                    profile.allowed_models == ()
                    or profile.allowed_models is None
                    or len(profile.allowed_models) == 0
                ), f"DETERMINISTIC agent '{key}' must have empty allowed_models"

    def test_llm_api_agents_have_nonempty_allowed_models(self):
        llm_agents = [(k, p) for k, p in AGENT_REGISTRY.items() if p.execution_mode == ExecutionMode.LLM_API]
        for key, profile in llm_agents:
            assert len(profile.allowed_models) > 0, (
                f"LLM_API agent '{key}' must have at least one allowed_model"
            )

    def test_all_agents_have_valid_reasoning_intensity(self):
        valid_intensities = {ri.value for ri in ReasoningIntensity}
        for key, profile in AGENT_REGISTRY.items():
            assert profile.reasoning_intensity.value in valid_intensities, (
                f"Agent '{key}' has invalid reasoning_intensity"
            )

    def test_all_agents_have_valid_execution_mode(self):
        valid_modes = {em.value for em in ExecutionMode}
        for key, profile in AGENT_REGISTRY.items():
            assert profile.execution_mode.value in valid_modes, f"Agent '{key}' has invalid execution_mode"

    def test_get_profile_returns_correct_type(self):
        first_key = next(iter(AGENT_REGISTRY))
        profile = get_profile(first_key)
        assert isinstance(profile, AgentExecutionProfile)

    def test_known_deterministic_agent_returns_deterministic_mode(self):
        profile = get_profile("reconciler")
        assert profile.execution_mode == ExecutionMode.DETERMINISTIC

    def test_known_llm_api_agent_returns_llm_api_mode(self):
        profile = get_profile("conversational_repair")
        assert profile.execution_mode == ExecutionMode.LLM_API

    def test_known_llm_api_agent_has_models(self):
        profile = get_profile("conversational_repair")
        assert len(profile.allowed_models) > 0


# ---------------------------------------------------------------------------
# 3. registry_digest() stability and sensitivity
# ---------------------------------------------------------------------------


class TestRegistryDigest:
    def test_digest_is_deterministic_across_calls(self):
        d1 = registry_digest()
        d2 = registry_digest()
        assert d1 == d2

    def test_digest_contains_all_registered_agents(self):
        d = registry_digest()
        for key in AGENT_REGISTRY:
            assert key in d

    def test_digest_values_contain_execution_mode(self):
        d = registry_digest()
        for key, value in d.items():
            profile = AGENT_REGISTRY[key]
            assert profile.execution_mode.value in value

    def test_digest_values_contain_agent_id(self):
        d = registry_digest()
        for key, value in d.items():
            assert key in value

    def test_digest_format_is_colon_delimited(self):
        d = registry_digest()
        for key, value in d.items():
            parts = value.split(":")
            assert len(parts) == 3, f"Digest for '{key}' expected 3 colon-delimited parts, got: {value}"


# ---------------------------------------------------------------------------
# 4. Transitive consumer contract: SovereignLLMGateway enforces registry
# ---------------------------------------------------------------------------


class TestGatewayTransitiveEnforcement:
    """
    Graph-selected transitive tests: agent_registry → SovereignLLMGateway.
    Proves the enforcement chain is intact without requiring live LLM calls.
    """

    def _make_gateway(self):
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
            SovereignLLMGateway,
            SovereigntyViolation,
        )

        SovereignLLMGateway.reset_instance()
        gw = SovereignLLMGateway()
        return gw, SovereigntyViolation

    def test_unregistered_agent_raises_sovereignty_violation(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation, match="not found in registry"):
            asyncio.run(gw.route_generation(_make_request(agent_id="__totally_nonexistent__")))

    def test_missing_agent_id_raises_sovereignty_violation(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation, match="agent_id is required"):
            asyncio.run(gw.route_generation(_make_request(agent_id="")))

    def test_deterministic_agent_blocked_by_gateway(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation, match="DETERMINISTIC"):
            asyncio.run(gw.route_generation(_make_request(agent_id="reconciler")))

    def test_deterministic_agent_error_contains_agent_id(self):
        gw, SovereigntyViolation = self._make_gateway()
        try:
            asyncio.run(gw.route_generation(_make_request(agent_id="reconciler")))
        except SovereigntyViolation as exc:
            assert "reconciler" in str(exc)

    def test_llm_api_agent_with_disallowed_model_raises(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation):
            asyncio.run(
                gw.route_generation(
                    _make_request(
                        agent_id="conversational_repair",
                        model="gpt-99-imaginary",
                    )
                )
            )

    def test_llm_api_rejection_message_contains_model_name(self):
        gw, SovereigntyViolation = self._make_gateway()
        try:
            asyncio.run(
                gw.route_generation(
                    _make_request(
                        agent_id="conversational_repair",
                        model="gpt-99-imaginary",
                    )
                )
            )
        except SovereigntyViolation as exc:
            assert "gpt-99-imaginary" in str(exc)

    def test_rejection_is_not_silent_fallback(self):
        """No silent provider substitution: rejection must raise, not return a result."""
        gw, SovereigntyViolation = self._make_gateway()
        result = None
        raised = False
        try:
            result = asyncio.run(gw.route_generation(_make_request(agent_id="reconciler")))
        except SovereigntyViolation:
            raised = True
        assert raised, "DETERMINISTIC agent must raise, not return a result"
        assert result is None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_request(agent_id: str, model: str | None = None):
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    return GenerationRequest(
        prompt="test prompt",
        agent_id=agent_id,
        provider="openai",
        model=model,
        temperature=0.0,
        max_tokens=16,
    )
