"""ADG-driven tests for apps_lic/tools/order_call_to_actions.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.order_call_to_actions  # noqa: F401


def test_module_importable():
    """Module order_call_to_actions must be importable."""
    assert apps_lic.tools.order_call_to_actions is not None
