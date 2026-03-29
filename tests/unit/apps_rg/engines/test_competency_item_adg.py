"""ADG-driven tests for apps_rg/engines/competency_item.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module competency_item must be importable."""
    import apps_rg.engines.competency_item  # noqa: F401

    assert apps_rg.engines.competency_item is not None