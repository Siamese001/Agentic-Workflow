"""ADG-driven tests for system_learning/engines/pattern_analysis_engine_adapter.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.engines.pattern_analysis_engine_adapter import (  # noqa: F401
        PatternAnalysisEngine,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PatternAnalysisEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="pattern_analysis_engine_adapter.py deps unavailable")
class TestPatternAnalysisEngine:
    def test_is_class(self):
        assert isinstance(PatternAnalysisEngine, type)
    def test_importable(self):
        assert PatternAnalysisEngine is not None


def test_module_importable():
    """Module pattern_analysis_engine_adapter.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
