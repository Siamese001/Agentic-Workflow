"""Tests for MetaPriorProvider port (Phase 1)."""

from __future__ import annotations

from system_learning.ports.meta_prior_provider import (
    _NEUTRAL_PRIOR,
    MetaPriorProvider,
    NeutralMetaPriorProvider,
)


class MockMetaPriorProvider:
    """Mock provider for testing."""

    def __init__(self, priors: dict[str, float]) -> None:
        self._priors = priors

    def get_prior(self, error_signature: str) -> float:
        return self._priors.get(error_signature, _NEUTRAL_PRIOR)


def test_neutral_meta_prior_provider() -> None:
    """NeutralMetaPriorProvider always returns neutral prior."""
    provider = NeutralMetaPriorProvider()
    assert provider.get_prior("any_signature") == _NEUTRAL_PRIOR
    assert provider.get_prior("another_signature") == _NEUTRAL_PRIOR


def test_mock_meta_prior_provider() -> None:
    """Mock provider returns configured priors."""
    priors = {"sig1": 0.75, "sig2": 0.25}
    provider = MockMetaPriorProvider(priors)

    assert provider.get_prior("sig1") == 0.75
    assert provider.get_prior("sig2") == 0.25
    assert provider.get_prior("unknown") == _NEUTRAL_PRIOR


def test_meta_prior_provider_protocol() -> None:
    """Mock provider satisfies MetaPriorProvider protocol."""
    provider = MockMetaPriorProvider({})
    assert isinstance(provider, MetaPriorProvider)


def test_neutral_prior_value() -> None:
    """Neutral prior is 0.50 as specified."""
    assert _NEUTRAL_PRIOR == 0.50
