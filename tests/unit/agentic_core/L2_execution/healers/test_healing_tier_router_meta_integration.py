"""Tests for healing_tier_router meta-learning integration (Phase 1)."""

from __future__ import annotations

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_router import (
    compute_heal_confidence,
    get_historical_success_rate,
    route_healing_tier,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
)
from system_learning.ports.meta_prior_provider import (
    NeutralMetaPriorProvider,
)


class MockMetaPriorProvider:
    """Mock provider with configurable priors."""

    def __init__(self, priors: dict[str, float]) -> None:
        self._priors = priors

    def get_prior(self, error_signature: str) -> float:
        return self._priors.get(error_signature, 0.50)


def test_get_historical_success_rate_with_provider() -> None:
    """get_historical_success_rate uses MetaPriorProvider when available."""
    provider = MockMetaPriorProvider({"sig1": 0.75, "sig2": 0.25})

    assert get_historical_success_rate("sig1", meta_prior_provider=provider) == 0.75
    assert get_historical_success_rate("sig2", meta_prior_provider=provider) == 0.25
    assert get_historical_success_rate("unknown", meta_prior_provider=provider) == 0.50


def test_get_historical_success_rate_fallback_to_stub() -> None:
    """Falls back to module stub when no provider."""
    # Set a stub value
    from agentic_core.L2_execution.healers.healing_tier_router import set_historical_success_rate

    set_historical_success_rate("stub_sig", 0.80)

    assert get_historical_success_rate("stub_sig") == 0.80
    assert get_historical_success_rate("truly_novel_sig") == 0.50

    # Clean up
    from agentic_core.L2_execution.healers.healing_tier_router import clear_historical_success_rates

    clear_historical_success_rates()


def test_compute_heal_confidence_uses_provider() -> None:
    """compute_heal_confidence incorporates MetaPriorProvider data."""
    provider = MockMetaPriorProvider({"high_success_sig": 0.90})

    healing_input = HealingInput(
        error_signature="high_success_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        retry_count=0,
        trace_id="test-trace",
    )

    confidence, reason_codes = compute_heal_confidence(
        healing_input,
        meta_prior_provider=provider,
    )

    assert 0.0 <= confidence <= 1.0
    assert any("historical_success_rate=0.9000" in code for code in reason_codes)


def test_route_healing_tier_uses_provider() -> None:
    """route_healing_tier passes MetaPriorProvider through."""
    provider = MockMetaPriorProvider({"high_success_sig": 0.90})
    config = HealingTierConfig()

    healing_input = HealingInput(
        error_signature="high_success_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        retry_count=0,
        trace_id="test-trace",
    )

    decision = route_healing_tier(
        healing_input,
        config,
        meta_prior_provider=provider,
    )

    assert decision.tier in HealingTier
    assert 0.0 <= decision.heal_confidence <= 1.0
    assert any("historical_success_rate=0.9000" in code for code in decision.reason_codes)


def test_neutral_provider_default() -> None:
    """NeutralMetaPriorProvider returns 0.50 for all signatures."""
    provider = NeutralMetaPriorProvider()

    assert provider.get_prior("any_sig") == 0.50
    assert provider.get_prior("another_sig") == 0.50


def test_backward_compatibility_without_provider() -> None:
    """Router works without MetaPriorProvider (backward compatibility)."""
    config = HealingTierConfig()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        retry_count=0,
        trace_id="test-trace",
    )

    # Should not raise exception
    decision = route_healing_tier(healing_input, config)
    assert decision.tier in HealingTier
