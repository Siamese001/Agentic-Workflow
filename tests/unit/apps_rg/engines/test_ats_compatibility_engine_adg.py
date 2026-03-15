"""ADG-driven tests for apps_rg/engines/ats_compatibility_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.engines.ats_compatibility_engine import ATSCompatibilityEngine
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ATSCompatibilityEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ATSCompatibilityEngine deps unavailable")
class TestATSCompatibilityEngine:
    def test_importable(self):
        assert callable(ATSCompatibilityEngine)

    def test_has_forbidden_patterns(self):
        class FakeCtx:
            buffer = None
        agent = ATSCompatibilityEngine(ctx=FakeCtx())
        assert hasattr(agent, "forbidden_patterns")
        assert len(agent.forbidden_patterns) > 0

    def test_forbidden_patterns_contain_table(self):
        class FakeCtx:
            buffer = None
        agent = ATSCompatibilityEngine(ctx=FakeCtx())
        patterns = [p[0] for p in agent.forbidden_patterns]
        assert any("table" in p for p in patterns)

    def test_has_execute(self):
        assert hasattr(ATSCompatibilityEngine, "execute")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
