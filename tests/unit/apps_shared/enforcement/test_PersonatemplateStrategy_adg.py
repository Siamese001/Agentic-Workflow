"""ADG-driven tests for apps_shared/enforcement/PersonatemplateStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module PersonatemplateStrategy must be importable."""
    import apps_shared.enforcement.PersonatemplateStrategy  # noqa: F401

    assert apps_shared.enforcement.PersonatemplateStrategy is not None