"""ADG-driven tests for apps_rg/engines/optimization_strategy_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.optimization_strategy_engine  # noqa: F401


def test_module_importable():
    """Module optimization_strategy_engine must be importable."""
    assert apps_rg.engines.optimization_strategy_engine is not None
