"""ADG-driven tests for apps_rg/engines/section_ranker_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.section_ranker_engine  # noqa: F401


def test_module_importable():
    """Module section_ranker_engine must be importable."""
    assert apps_rg.engines.section_ranker_engine is not None
