"""ADG-driven tests for apps_lic/config/reasoning_toggles_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.config.reasoning_toggles_config  # noqa: F401


def test_module_importable():
    """Module reasoning_toggles_config must be importable."""
    assert apps_lic.config.reasoning_toggles_config is not None
