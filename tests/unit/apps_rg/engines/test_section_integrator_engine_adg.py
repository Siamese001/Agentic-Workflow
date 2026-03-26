"""ADG-driven tests for apps_rg/engines/section_integrator_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module section_integrator_engine must be importable."""
    import apps_rg.engines.section_integrator_engine  # noqa: F401

    assert apps_rg.engines.section_integrator_engine is not None
