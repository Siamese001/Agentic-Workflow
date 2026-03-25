"""ADG importability contract for apps_lic/reasoning/LicReflectionAgent.py."""
from __future__ import annotations

import apps_lic.reasoning.LicReflectionAgent  # noqa: F401


def test_module_importable():
    """Module LicReflectionAgent must be importable."""
    assert apps_lic.reasoning.LicReflectionAgent is not None
