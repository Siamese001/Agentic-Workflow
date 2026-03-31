"""ADG-driven tests for apps_shared/scripts/update_observability_usage_safety_type.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module update_observability_usage_safety_type must be importable."""
    import apps_shared.scripts.update_observability_usage_safety_type  # noqa: F401

    assert apps_shared.scripts.update_observability_usage_safety_type is not None
