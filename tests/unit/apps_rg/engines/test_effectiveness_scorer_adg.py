"""ADG-driven tests for apps_rg/engines/effectiveness_scorer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.effectiveness_scorer  # noqa: F401


def test_module_importable():
    """Module effectiveness_scorer must be importable."""
    assert apps_rg.engines.effectiveness_scorer is not None
