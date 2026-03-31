"""ADG-driven tests for apps_shared/scripts/script_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module script_bridge must be importable."""
    import apps_shared.scripts.script_bridge  # noqa: F401

    assert apps_shared.scripts.script_bridge is not None
