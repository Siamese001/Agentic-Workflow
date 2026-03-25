"""ADG-driven tests for apps_rg/tools/query_past_generations.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.query_past_generations  # noqa: F401


def test_module_importable():
    """Module query_past_generations must be importable."""
    assert apps_rg.tools.query_past_generations is not None
