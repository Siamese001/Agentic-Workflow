"""ADG-driven tests for apps_lic/tools/network_ops.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module network_ops must be importable."""
    import apps_lic.tools.network_ops  # noqa: F401

    assert apps_lic.tools.network_ops is not None