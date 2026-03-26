"""ADG contract tests for apps_lic/types/k1_router_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module k1_router_types must be importable."""
    import apps_lic.types.k1_router_types  # noqa: F401

    assert apps_lic.types.k1_router_types is not None