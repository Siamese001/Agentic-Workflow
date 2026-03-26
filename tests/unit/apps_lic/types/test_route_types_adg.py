"""ADG contract tests for apps_lic/types/route_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module route_types must be importable."""
    import apps_lic.types.route_types  # noqa: F401

    assert apps_lic.types.route_types is not None