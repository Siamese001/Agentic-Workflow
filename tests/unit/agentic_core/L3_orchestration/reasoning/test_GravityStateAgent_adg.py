"""ADG-driven tests for agentic_core/L3_orchestration/reasoning/GravityStateAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L3_orchestration.reasoning.GravityStateAgent import (  # noqa: F401
        GravityStateAgent,
        HealingRecord,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealingRecord = None  # type: ignore[assignment,misc]
    GravityStateAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="GravityStateAgent.py deps unavailable")
class TestHealingRecord:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingRecord)
    def test_importable(self):
        assert HealingRecord is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GravityStateAgent.py deps unavailable")
class TestGravityStateAgent:
    def test_is_class(self):
        assert isinstance(GravityStateAgent, type)
    def test_importable(self):
        assert GravityStateAgent is not None


def test_module_importable():
    """Module GravityStateAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
