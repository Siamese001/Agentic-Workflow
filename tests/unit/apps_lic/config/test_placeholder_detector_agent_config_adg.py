"""ADG-driven tests for apps_lic/config/placeholder_detector_agent_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.config.placeholder_detector_agent_config  # noqa: F401


def test_module_importable():
    """Module placeholder_detector_agent_config must be importable."""
    assert apps_lic.config.placeholder_detector_agent_config is not None
