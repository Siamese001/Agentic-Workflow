"""ADG importability contract for apps_lic/reasoning/LICValidationExecutor.py."""
from __future__ import annotations

import apps_lic.reasoning.LICValidationExecutor  # noqa: F401


def test_module_importable():
    """Module LICValidationExecutor must be importable."""
    assert apps_lic.reasoning.LICValidationExecutor is not None
