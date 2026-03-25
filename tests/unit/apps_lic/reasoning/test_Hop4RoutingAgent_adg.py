"""ADG-driven tests for apps_lic/reasoning/Hop4RoutingAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.Hop4RoutingAgent  # noqa: F401


def test_module_importable():
    """Module Hop4RoutingAgent must be importable."""
    assert apps_lic.reasoning.Hop4RoutingAgent is not None
