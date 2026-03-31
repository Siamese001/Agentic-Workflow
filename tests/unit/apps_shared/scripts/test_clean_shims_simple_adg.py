"""ADG-driven tests for apps_shared/scripts/clean_shims_simple.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module clean_shims_simple must be importable."""
    import apps_shared.scripts.clean_shims_simple  # noqa: F401

    assert apps_shared.scripts.clean_shims_simple is not None
