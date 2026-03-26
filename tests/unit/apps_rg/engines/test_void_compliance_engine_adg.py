"""ADG importability contract for apps_rg/engines/void_compliance_engine.py."""
from __future__ import annotations



def test_module_importable():
    """Module void_compliance_engine must be importable."""
    import apps_rg.engines.void_compliance_engine  # noqa: F401

    assert apps_rg.engines.void_compliance_engine is not None