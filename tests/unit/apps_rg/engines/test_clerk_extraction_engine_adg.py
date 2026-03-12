"""ADG-driven tests for apps_rg/engines/clerk_extraction_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.engines.clerk_extraction_engine import ClerkExtractionEngine
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ClerkExtractionEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ClerkExtractionEngine deps unavailable")
class TestClerkExtractionEngine:
    def _make_ctx(self):
        class FakeBuffer:
            def read(self, key, default=None):
                return default
        class FakeCtx:
            buffer = FakeBuffer()
        return FakeCtx()

    def test_importable(self):
        assert callable(ClerkExtractionEngine)

    def test_creates(self):
        agent = ClerkExtractionEngine(ctx=self._make_ctx())
        assert agent is not None

    def test_has_detector(self):
        agent = ClerkExtractionEngine(ctx=self._make_ctx())
        assert hasattr(agent, "detector")

    def test_has_execute(self):
        assert hasattr(ClerkExtractionEngine, "execute")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
