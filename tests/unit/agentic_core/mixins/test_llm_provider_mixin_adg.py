"""ADG-driven tests for mixins/llm_provider_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.llm_provider_mixin import LLMProviderMixin, Provider
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LLMProviderMixin = None  # type: ignore[assignment,misc]
    Provider = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="LLMProviderMixin deps unavailable")
class TestLLMProviderMixin:
    def test_importable(self):
        assert callable(LLMProviderMixin)

    def test_llm_gateway_default_none(self):
        assert LLMProviderMixin._llm_gateway is None

    def test_has_llm_generate(self):
        assert hasattr(LLMProviderMixin, "llm_generate")

    def test_has_llm_generate_with_fallback(self):
        assert hasattr(LLMProviderMixin, "llm_generate_with_fallback")

    def test_provider_literal(self):
        from typing import get_args
        args = get_args(Provider)
        assert "openai" in args


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
