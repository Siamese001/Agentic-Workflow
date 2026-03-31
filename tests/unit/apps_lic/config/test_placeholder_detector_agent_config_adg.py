"""ADG-driven tests for apps_lic/config/placeholder_detector_agent_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module placeholder_detector_agent_config must be importable."""
    import apps_lic.config.placeholder_detector_agent_config  # noqa: F401

    assert apps_lic.config.placeholder_detector_agent_config is not None
