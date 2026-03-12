"""ADG-driven tests for L2_execution/enforcement/provider_substitution_prohibition.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.provider_substitution_prohibition import (
    ProviderRequest,
    ProviderSubstitutionViolation,
    validate_provider_request,
)


class TestProviderRequest:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ProviderRequest)

    def test_is_frozen(self):
        req = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="a-1", request_id="r-1"
        )
        with pytest.raises((AttributeError, TypeError)):
            req.provider = "anthropic"


class TestProviderSubstitutionViolation:
    def test_is_exception(self):
        assert issubclass(ProviderSubstitutionViolation, Exception)

    def test_raises(self):
        with pytest.raises(ProviderSubstitutionViolation):
            raise ProviderSubstitutionViolation("substitution detected")


class TestValidateProviderRequest:
    def test_passes_when_matching(self):
        req = ProviderRequest(provider="openai", model="gpt-4", agent_id="a-1", request_id="r-1")
        validate_provider_request(req, actual_provider="openai", actual_model="gpt-4")

    def test_raises_on_provider_mismatch(self):
        req = ProviderRequest(provider="openai", model="gpt-4", agent_id="a-1", request_id="r-1")
        with pytest.raises(ProviderSubstitutionViolation):
            validate_provider_request(req, actual_provider="anthropic", actual_model="gpt-4")
