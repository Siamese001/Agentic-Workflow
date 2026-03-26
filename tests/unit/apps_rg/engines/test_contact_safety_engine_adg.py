"""ADG importability contract for apps_rg/engines/contact_safety_engine.py."""
from __future__ import annotations



def test_module_importable():
    """Module contact_safety_engine must be importable."""
    import apps_rg.engines.contact_safety_engine  # noqa: F401

    assert apps_rg.engines.contact_safety_engine is not None