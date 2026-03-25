"""ADG-driven tests for agentic_core/L0_routing/scripts/file_analysis.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.file_analysis  # noqa: F401


def test_module_importable():
    """Module file_analysis must be importable."""
    assert agentic_core.L0_routing.scripts.file_analysis is not None
