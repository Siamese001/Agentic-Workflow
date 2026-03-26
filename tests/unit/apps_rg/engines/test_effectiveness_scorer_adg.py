"""ADG-driven tests for apps_rg/engines/effectiveness_scorer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module effectiveness_scorer must be importable."""
    import apps_rg.engines.effectiveness_scorer  # noqa: F401

    assert apps_rg.engines.effectiveness_scorer is not None