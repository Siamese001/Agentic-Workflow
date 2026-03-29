"""ADG importability contract for apps_rg/reasoning/RGValidationExecutor.py."""
from __future__ import annotations


def test_module_importable():
    """Module RGValidationExecutor must be importable."""
    import apps_rg.reasoning.RGValidationExecutor  # noqa: F401

    assert apps_rg.reasoning.RGValidationExecutor is not None