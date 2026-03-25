"""ADG-driven tests for apps_rg/tools/word_counter_tool.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.word_counter_tool  # noqa: F401


def test_module_importable():
    """Module word_counter_tool must be importable."""
    assert apps_rg.tools.word_counter_tool is not None
