"""ADG-driven tests for apps_lic/tools/mcp_mocks.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module mcp_mocks must be importable."""
    import apps_lic.tools.mcp_mocks  # noqa: F401

    assert apps_lic.tools.mcp_mocks is not None