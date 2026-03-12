"""ADG-driven tests for apps_rg/engines/gap_closure_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_rg.engines.gap_closure_engine import GapClosureEngine


class TestGapClosureEngine:
    def test_importable(self):
        assert callable(GapClosureEngine)

    def test_creates(self):
        engine = GapClosureEngine()
        assert engine is not None

    def test_has_execute(self):
        assert hasattr(GapClosureEngine, "execute")
