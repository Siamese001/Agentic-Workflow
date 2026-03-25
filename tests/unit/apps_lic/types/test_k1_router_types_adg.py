"""ADG contract tests for apps_lic/types/k1_router_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.k1_router_types  # noqa: F401


def test_module_importable():
    """Module k1_router_types must be importable."""
    assert apps_lic.types.k1_router_types is not None
