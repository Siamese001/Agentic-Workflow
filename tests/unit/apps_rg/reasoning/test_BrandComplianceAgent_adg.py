"""ADG importability contract for apps_rg/reasoning/BrandComplianceAgent.py."""
from __future__ import annotations

import apps_rg.reasoning.BrandComplianceAgent  # noqa: F401


def test_module_importable():
    """Module BrandComplianceAgent must be importable."""
    assert apps_rg.reasoning.BrandComplianceAgent is not None
