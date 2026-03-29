"""ADG-driven tests for apps_rg/scripts/test_input.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module test_input must be importable."""
    import apps_rg.scripts.test_input  # noqa: F401

    assert apps_rg.scripts.test_input is not None