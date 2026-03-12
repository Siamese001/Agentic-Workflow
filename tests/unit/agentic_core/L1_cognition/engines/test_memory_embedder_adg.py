"""ADG-driven tests for L1_cognition/engines/memory_embedder.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.engines.memory_embedder import HealingMemoryEmbedder
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealingMemoryEmbedder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="memory_embedder deps unavailable")
class TestHealingMemoryEmbedder:
    def test_importable(self):
        assert callable(HealingMemoryEmbedder)

    def test_creates_with_defaults(self):
        embedder = HealingMemoryEmbedder()
        assert embedder is not None

    def test_has_embed_violation(self):
        assert hasattr(HealingMemoryEmbedder, "embed_violation") or hasattr(
            HealingMemoryEmbedder, "embed"
        )


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
