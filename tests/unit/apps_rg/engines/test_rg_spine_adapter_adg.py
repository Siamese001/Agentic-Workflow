"""ADG importability contract for apps_rg/engines/rg_spine_adapter.py."""
from __future__ import annotations


def test_module_importable():
    """Module rg_spine_adapter must be importable."""
    import apps_rg.engines.rg_spine_adapter  # noqa: F401

    assert apps_rg.engines.rg_spine_adapter is not None
