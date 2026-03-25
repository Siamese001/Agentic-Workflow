"""ADG-driven tests for agentic_core/L2_execution/tools/content_relevance_impl.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.content_relevance_impl  # noqa: F401


def test_module_importable():
    """Module content_relevance_impl must be importable."""
    assert agentic_core.L2_execution.tools.content_relevance_impl is not None
