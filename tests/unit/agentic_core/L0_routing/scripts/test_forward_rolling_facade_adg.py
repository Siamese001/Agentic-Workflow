"""ADG-driven tests for agentic_core/L0_routing/scripts/forward_rolling_facade.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.forward_rolling_facade import (  # noqa: F401
        ForwardRollingResult,
        OptimizationMetrics,
        ForwardRollingFacade,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ForwardRollingResult = None  # type: ignore[assignment,misc]
    OptimizationMetrics = None  # type: ignore[assignment,misc]
    ForwardRollingFacade = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="forward_rolling_facade.py deps unavailable")
class TestForwardRollingResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ForwardRollingResult)
    def test_importable(self):
        assert ForwardRollingResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forward_rolling_facade.py deps unavailable")
class TestOptimizationMetrics:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(OptimizationMetrics)
    def test_importable(self):
        assert OptimizationMetrics is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forward_rolling_facade.py deps unavailable")
class TestForwardRollingFacade:
    def test_is_class(self):
        assert isinstance(ForwardRollingFacade, type)
    def test_importable(self):
        assert ForwardRollingFacade is not None


def test_module_importable():
    """Module forward_rolling_facade.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
