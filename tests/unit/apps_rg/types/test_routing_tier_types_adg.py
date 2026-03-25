"""ADG contract tests for apps_rg/types/routing_tier_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.types.routing_tier_types  # noqa: F401


def test_module_importable():
    """Module routing_tier_types must be importable."""
    assert apps_rg.types.routing_tier_types is not None
