"""ADG-driven tests for apps_shared/scripts/fix_mcp_hardening_smart.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.fix_mcp_hardening_smart  # noqa: F401


def test_module_importable():
    """Module fix_mcp_hardening_smart must be importable."""
    assert apps_shared.scripts.fix_mcp_hardening_smart is not None
