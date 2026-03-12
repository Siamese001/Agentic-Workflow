"""ADG-driven tests for mixins/embedding_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.embedding_mixin import EmbeddingMixin, EmbeddingProvider


class TestEmbeddingMixin:
    def test_importable(self):
        assert callable(EmbeddingMixin)

    def test_embedding_gateway_default_none(self):
        assert EmbeddingMixin._embedding_gateway is None

    def test_has_get_embedding(self):
        assert hasattr(EmbeddingMixin, "get_embedding")

    def test_embedding_provider_type(self):
        # EmbeddingProvider is a Literal type alias — verify it's accessible
        assert EmbeddingProvider is not None


class TestEmbeddingProviderLiteral:
    def test_gemini_is_valid(self):
        from typing import get_args
        args = get_args(EmbeddingProvider)
        assert "gemini" in args

    def test_openai_is_valid(self):
        from typing import get_args
        args = get_args(EmbeddingProvider)
        assert "openai" in args
