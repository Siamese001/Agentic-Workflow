"""ADG-driven tests for apps_rg/config/void_compliance_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module void_compliance_config must be importable."""
    import apps_rg.config.void_compliance_config  # noqa: F401

    assert apps_rg.config.void_compliance_config is not None