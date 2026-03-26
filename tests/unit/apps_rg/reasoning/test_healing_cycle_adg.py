"""ADG importability contract for apps_rg/reasoning/healing_cycle.py."""
from __future__ import annotations



def test_module_importable():
    """Module healing_cycle must be importable."""
    import apps_rg.reasoning.healing_cycle  # noqa: F401

    assert apps_rg.reasoning.healing_cycle is not None