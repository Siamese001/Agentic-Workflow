"""ADG-driven tests for apps_shared/scripts/meta_control_config_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.meta_control_config_bridge  # noqa: F401


def test_module_importable():
    """Module meta_control_config_bridge must be importable."""
    assert apps_shared.scripts.meta_control_config_bridge is not None
