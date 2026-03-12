"""ADG-driven tests for L1_cognition/engines/semantic_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.semantic_manager import (
    EmbeddingProvider,
    VectorIndex,
)


class TestEmbeddingProvider:
    def test_creates_with_default(self):
        ep = EmbeddingProvider()
        assert ep.model == "BAAI/bge-m3"

    def test_embed_returns_list(self):
        ep = EmbeddingProvider()
        result = ep.embed("hello")
        assert isinstance(result, list)
        assert len(result) > 0


class TestVectorIndex:
    def test_creates(self):
        idx = VectorIndex()
        assert idx.dimension == 1024

    def test_add_and_contains(self):
        idx = VectorIndex()
        idx.add("key1", [0.1] * 1024)
        assert "key1" in idx._vectors
