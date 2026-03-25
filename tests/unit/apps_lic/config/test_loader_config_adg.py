"""ADG-driven tests for apps_lic/config/loader_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.config.loader_config  # noqa: F401


def test_module_importable():
    """Module loader_config must be importable."""
    assert apps_lic.config.loader_config is not None
