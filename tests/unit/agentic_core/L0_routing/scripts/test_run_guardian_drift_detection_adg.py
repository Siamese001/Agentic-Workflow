"""ADG-driven tests for agentic_core/L0_routing/scripts/run_guardian_drift_detection.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.run_guardian_drift_detection  # noqa: F401


def test_module_importable():
    """Module run_guardian_drift_detection must be importable."""
    assert agentic_core.L0_routing.scripts.run_guardian_drift_detection is not None
