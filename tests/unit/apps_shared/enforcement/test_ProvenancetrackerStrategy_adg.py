"""ADG-driven tests for apps_shared/enforcement/ProvenancetrackerStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module ProvenancetrackerStrategy must be importable."""
    import apps_shared.enforcement.ProvenancetrackerStrategy  # noqa: F401

    assert apps_shared.enforcement.ProvenancetrackerStrategy is not None
