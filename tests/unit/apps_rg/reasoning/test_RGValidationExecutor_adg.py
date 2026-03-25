"""ADG importability contract for apps_rg/reasoning/RGValidationExecutor.py."""
from __future__ import annotations

import apps_rg.reasoning.RGValidationExecutor  # noqa: F401


def test_module_importable():
    """Module RGValidationExecutor must be importable."""
    assert apps_rg.reasoning.RGValidationExecutor is not None
