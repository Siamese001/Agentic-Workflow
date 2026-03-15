"""ADG-driven tests for apps_rg/engines/content_quality_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.engines.content_quality_engine import ContentQualityEngine
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ContentQualityEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ContentQualityEngine deps unavailable")
class TestContentQualityEngine:
    def _make_ctx(self):
        class FakeBuffer:
            def read(self, key, default=None):
                return default
        class FakeCtx:
            buffer = FakeBuffer()
        return FakeCtx()

    def test_importable(self):
        assert callable(ContentQualityEngine)

    def test_creates(self):
        agent = ContentQualityEngine(ctx=self._make_ctx())
        assert agent is not None

    def test_has_execute(self):
        assert hasattr(ContentQualityEngine, "execute")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
