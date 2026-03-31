"""ADG-driven tests for apps_shared/scripts/manage_false_positives.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module manage_false_positives must be importable."""
    import apps_shared.scripts.manage_false_positives  # noqa: F401

    assert apps_shared.scripts.manage_false_positives is not None
