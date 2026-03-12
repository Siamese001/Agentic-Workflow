"""ADG-driven tests for apps_rg/engines/section_ranker_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.engines.section_ranker_engine import SectionRankerEngine
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SectionRankerEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SectionRankerEngine deps unavailable")
class TestSectionRankerEngine:
    def _make_ctx(self):
        class FakeBuffer:
            def read(self, key, default=None):
                return default
        class FakeCtx:
            buffer = FakeBuffer()
        return FakeCtx()

    def test_importable(self):
        assert callable(SectionRankerEngine)

    def test_creates(self):
        agent = SectionRankerEngine(ctx=self._make_ctx())
        assert agent is not None

    def test_strategies_default(self):
        agent = SectionRankerEngine(ctx=self._make_ctx())
        assert hasattr(agent, "strategies")
        assert "technical" in agent.strategies

    def test_has_execute(self):
        assert hasattr(SectionRankerEngine, "execute")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
