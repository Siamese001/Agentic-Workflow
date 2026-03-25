"""ADG-driven tests for apps_rg/engines/competency_item.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.competency_item  # noqa: F401


def test_module_importable():
    """Module competency_item must be importable."""
    assert apps_rg.engines.competency_item is not None
