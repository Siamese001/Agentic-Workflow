"""ADG-driven tests for apps_rg/reasoning/HeadlineOutputAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.reasoning.HeadlineOutputAgent  # noqa: F401


def test_module_importable():
    """Module HeadlineOutputAgent must be importable."""
    assert apps_rg.reasoning.HeadlineOutputAgent is not None
