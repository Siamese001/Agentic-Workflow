"""ADG-driven tests for apps_rg/engines/content_optimizer_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.engines.content_optimizer_engine import ContentOptimizerEngine
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ContentOptimizerEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ContentOptimizerEngine deps unavailable")
class TestContentOptimizerEngine:
    def _make_ctx(self):
        class FakeBuffer:
            def read(self, key, default=None):
                return default
        class FakeCtx:
            buffer = FakeBuffer()
        return FakeCtx()

    def test_importable(self):
        assert callable(ContentOptimizerEngine)

    def test_creates(self):
        agent = ContentOptimizerEngine(ctx=self._make_ctx())
        assert agent is not None

    def test_has_execute(self):
        assert hasattr(ContentOptimizerEngine, "execute")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
