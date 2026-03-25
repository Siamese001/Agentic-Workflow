"""ADG-driven tests for apps_shared/config/operational_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.config.operational_config  # noqa: F401


def test_module_importable():
    """Module operational_config must be importable."""
    assert apps_shared.config.operational_config is not None
