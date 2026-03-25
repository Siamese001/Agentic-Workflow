"""ADG-driven tests for agentic_core/L2_execution/tools/web_search_client.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.web_search_client  # noqa: F401


def test_module_importable():
    """Module web_search_client must be importable."""
    assert agentic_core.L2_execution.tools.web_search_client is not None
