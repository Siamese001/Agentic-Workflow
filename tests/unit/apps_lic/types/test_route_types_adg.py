"""ADG contract tests for apps_lic/types/route_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.route_types  # noqa: F401


def test_module_importable():
    """Module route_types must be importable."""
    assert apps_lic.types.route_types is not None
