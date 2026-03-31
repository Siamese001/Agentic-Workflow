"""ADG-driven tests for apps_shared/config/routing_tier_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module routing_tier_config must be importable."""
    import apps_shared.config.routing_tier_config  # noqa: F401

    assert apps_shared.config.routing_tier_config is not None
