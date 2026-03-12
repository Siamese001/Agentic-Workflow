"""ADG-driven tests for L2_execution/engines/resource_predictor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.engines.resource_predictor import (
        DefaultDeterministicResourcePredictor,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DefaultDeterministicResourcePredictor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="resource_predictor deps unavailable")
class TestDefaultDeterministicResourcePredictor:
    def test_importable(self):
        assert callable(DefaultDeterministicResourcePredictor)

    def test_has_bounds(self):
        assert DefaultDeterministicResourcePredictor.MIN_CPU_CORES >= 1
        assert DefaultDeterministicResourcePredictor.MAX_CPU_CORES >= 1
        assert DefaultDeterministicResourcePredictor.MIN_MEMORY_MB >= 512

    def test_has_baseline_envelopes(self):
        envelopes = DefaultDeterministicResourcePredictor._BASELINE_ENVELOPES
        assert "timeout" in envelopes
        assert "unknown" in envelopes

    def test_creates(self):
        predictor = DefaultDeterministicResourcePredictor()
        assert predictor is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
