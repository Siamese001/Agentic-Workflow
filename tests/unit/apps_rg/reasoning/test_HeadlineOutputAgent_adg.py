"""ADG-driven tests for apps_rg/reasoning/HeadlineOutputAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module HeadlineOutputAgent must be importable."""
    import apps_rg.reasoning.HeadlineOutputAgent  # noqa: F401

    assert apps_rg.reasoning.HeadlineOutputAgent is not None