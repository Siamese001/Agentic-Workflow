"""ADG-driven tests for apps_rg/engines/skill_ordering_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module skill_ordering_engine must be importable."""
    import apps_rg.engines.skill_ordering_engine  # noqa: F401

    assert apps_rg.engines.skill_ordering_engine is not None